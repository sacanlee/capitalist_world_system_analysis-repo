# -*- coding: utf-8 -*-
"""解析世界钢铁协会《Steel Statistical Yearbook 2003》(raw/worldsteel_ssy2003.pdf)
Table "Total Production of Crude Steel"（1993-2002 逐年，kt），取 1995 列。
输出 data/steel_1995_raw.csv（原始解析）+ 打印世界合计核对。"""
import os
import re

import pdfplumber
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(BASE, "raw", "worldsteel_ssy2003.pdf")
OUT = os.path.join(BASE, "data", "steel_1995_raw.csv")

HEADER_RE = re.compile(r"^\s*1993\s+1994\s+1995\s")

rows_out = []
with pdfplumber.open(PDF) as pdf:
    pages = [i for i, p in enumerate(pdf.pages)
             if (p.extract_text() or "").startswith("Table 4 Total Production of Crude Steel")
             or "Total Production of Crude Steel" in (p.extract_text() or "").split("\n")[0]]
    print("crude steel 表页(0-based):", pages)

    for pi in pages:
        page = pdf.pages[pi]
        words = page.extract_words(keep_blank_chars=False, use_text_flow=False)
        # 按 top 归行
        lines = {}
        for w in words:
            key = round(w["top"] / 3.0)
            lines.setdefault(key, []).append(w)

        header_cols = None
        for key in sorted(lines):
            ws = sorted(lines[key], key=lambda w: w["x0"])
            text = " ".join(w["text"] for w in ws)
            m = HEADER_RE.match(text)
            if m:
                years = [int(y) for y in re.findall(r"\d{4}", text)]
                # 每个年份列的中心 x（用该 token 的 x0/x1）
                cols = []
                toks = [w for w in ws if re.fullmatch(r"\d{4}", w["text"])]
                for w in toks:
                    cols.append((int(w["text"]), w["x0"], w["x1"]))
                header_cols = cols
                print(f"page {pi}: 表头年份 {years}  列数={len(cols)}")
                print("  列中心x:", [round((c[1] + c[2]) / 2, 1) for c in cols])
                continue
            if header_cols is None:
                continue
            if not ws:
                continue
            # 数据行：年份列左边界 = 第一个年份列的 x0
            year_x0 = min(c[1] for c in header_cols)
            name_words = [w for w in ws if w["x1"] <= year_x0 - 2]
            val_words = [w for w in ws if w["x1"] > year_x0 - 2]
            if not name_words:
                continue
            name = " ".join(w["text"] for w in name_words).strip()
            if not name or name.lower().startswith("table"):
                continue
            # 值按列中心分桶
            centers = [(y, (x0 + x1) / 2.0) for y, x0, x1 in header_cols]
            buckets = {y: [] for y, _ in centers}
            for w in sorted(val_words, key=lambda w: w["x0"]):
                cx = (w["x0"] + w["x1"]) / 2.0
                y = min(centers, key=lambda c: abs(c[1] - cx))[0]
                buckets[y].append(w["text"])
            vals = {}
            for y, toks in buckets.items():
                s = "".join(toks).replace(" ", "")
                if s == "":
                    vals[y] = None
                elif s.lower().endswith("e"):
                    vals[y] = float(s[:-1].replace(",", ""))
                elif s in ("...", "..", "."):
                    vals[y] = None
                elif re.fullmatch(r"[\d,]+", s):
                    vals[y] = float(s.replace(",", ""))
                else:
                    vals[y] = s
            rows_out.append({"page": pi, "name": name, **{str(y): vals.get(y) for y, _ in centers}})

df = pd.DataFrame(rows_out)
df.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"\n解析行数={len(df)}  列={list(df.columns)}")

ycols = [c for c in df.columns if re.fullmatch(r"\d{4}", str(c))]
print("\n各年非空计数:")
for c in ycols:
    n = df[c].apply(lambda v: isinstance(v, (int, float))).sum()
    print(f"  {c}: {n}")

num = df[ycols].apply(pd.to_numeric, errors="coerce")
print("\n各年合计(kt) -> Mt:")
for c in ycols:
    print(f"  {c}: {num[c].sum():>12,.0f} kt  {num[c].sum()/1000:>9.1f} Mt")

print("\n=== 1995 非空行预览 ===")
sub = df[["name", "1995"]].copy()
sub["v"] = pd.to_numeric(sub["1995"], errors="coerce")
print(sub.dropna(subset=["v"]).sort_values("v", ascending=False).head(30).to_string(index=False))
print("\n非数值1995行:", df[~df["1995"].apply(lambda v: isinstance(v, (int, float)) | (v is None))][["name", "1995"]].to_dict("records")[:20])
