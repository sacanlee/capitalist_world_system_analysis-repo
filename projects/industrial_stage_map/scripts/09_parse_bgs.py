# -*- coding: utf-8 -*-
"""解析 BGS World Mineral Production 粗钢表(2020-2024)。
按 y 聚行 + 按 x 分列(名称列 + 5个年份列)，输出 data/bgs_crude_steel.csv。"""
import os
import re
import json
import pdfplumber

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(BASE, "raw", "bgs_wmp_2020_2024.pdf")
OUT = os.path.join(BASE, "data", "bgs_crude_steel.csv")

# 5个年份数值列的 x 区间（由调试坐标得出：列头右对齐，首位数字可至约488）
COLS = [(204, 266), (279, 336), (349, 406), (420, 474), (484, 548)]
YEARS = [2020, 2021, 2022, 2023, 2024]


def parse_page(page):
    words = page.extract_words(use_text_flow=False)
    rows = {}
    for wd in words:
        y = round(wd["top"] * 2) / 2.0  # 0.5pt 桶
        rows.setdefault(y, []).append(wd)
    # 合并相邻 y 桶（行距约10pt，容差1.6pt）
    ys = sorted(rows)
    merged = []
    for y in ys:
        if merged and y - merged[-1][-1] <= 1.6:
            merged[-1].append(y)
        else:
            merged.append([y])
    out = []
    for grp in merged:
        ws = [w for y in grp for w in rows[y]]
        name_ws = [w for w in ws if w["x0"] < 200 and re.search(r"[A-Za-z]", w["text"])]
        name = " ".join(w["text"] for w in sorted(name_ws, key=lambda d: d["x0"]))
        if not name or len(name) < 3:
            continue
        vals, ests = [], []
        for (x0, x1) in COLS:
            cell = [w for w in ws if x0 <= w["x0"] < x1 and not re.search(r"[A-Za-z]", w["text"])]
            digits = "".join(ch for w in sorted(cell, key=lambda d: d["x0"]) for ch in w["text"] if ch.isdigit())
            est = any("*" in w["text"] for w in cell)
            vals.append(int(digits) if digits else None)
            ests.append(est)
        out.append({"name": name, "vals": vals, "ests": ests})
    return out


with pdfplumber.open(PDF) as pdf:
    pages = [p for p in pdf.pages if "Production of crude steel" in (p.extract_text() or "")]
    recs = []
    for p in pages:
        recs.extend(parse_page(p))
    print("页:", [p.page_number for p in pages], "行:", len(recs))

# 校验：worldsteel 维基表 2024 值（Mt→t）
import csv as _csv
ws = {r["name"]: r for r in _csv.DictReader(open(os.path.join(BASE, "data", "steel_countries.csv"), encoding="utf-8-sig"))}
ALIAS = {"South Korea": "Korea (Rep. of)", "North Korea": "Korea, Dem. P.R. of",
         "United States": "USA", "Czechia": "Czech Republic", "Turkey": "Turkey",
         "Bosnia Herzegovina": "Bosnia & Herzegovina"}
by = {r["name"]: r for r in recs}
ok = True
for nm, r in ws.items():
    if nm.startswith("Others"):
        continue
    v24 = r["2024"].strip()
    if not v24:
        continue
    want = float(v24) * 1e6
    k = ALIAS.get(nm, nm)
    got = by.get(k, {}).get("vals", [None] * 5)[4]
    if got is None:
        print(f"  {nm:<22} 缺行")
        continue
    diff = (got - want) / want * 100
    if abs(diff) > 5:
        ok = False
        print(f"  {nm:<22} BGS2024={got:>13,} 世界钢协={want:>13,.0f} diff={diff:6.1f}% <<<")

rows = []
for r in recs:
    if r["name"].lower().startswith(("country", "world")):
        continue
    rows.append({"name": r["name"], **{str(y): v for y, v in zip(YEARS, r["vals"])},
                 **{f"est{y}": e for y, e in zip(YEARS, r["ests"])}})
import csv
with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    wr.writeheader()
    wr.writerows(rows)
print("写出", OUT, len(rows), "行; 校验:", "通过" if ok else "失败")
