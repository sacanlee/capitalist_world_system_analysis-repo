# -*- coding: utf-8 -*-
"""解析维基最低工资表 -> data/minwage2024.csv，并与2024年分类合并。"""
import csv
import os
import re

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
raw = os.path.join(BASE, "raw", "wiki_minwage.html")

t = pd.read_html(raw)[2]
t.columns = ["country", "notes", "annual_nom", "annual_ppp", "workweek", "hourly_nom", "hourly_ppp",
             "pct_gdp", "eff_date"]
t = t[t["country"].notna() & (t["country"] != "Country&Region")]
print("行数:", len(t))


def num(x):
    if pd.isna(x):
        return None
    s = str(x)
    m = re.search(r"([\d,]+(?:\.\d+)?)", s.replace("\u00a0", " "))
    if not m:
        return None
    v = float(m.group(1).replace(",", ""))
    return v


rows = []
for _, r in t.iterrows():
    name = str(r["country"]).strip()
    name = re.sub(r"\[.*?\]", "", name).strip()
    rows.append({"wiki_name": name, "annual_nom": num(r["annual_nom"]), "annual_ppp": num(r["annual_ppp"]),
                 "workweek": num(r["workweek"]), "eff": str(r["eff_date"])[:40]})
mw = pd.DataFrame(rows)
mw.to_csv(os.path.join(DATA, "minwage_raw.csv"), index=False, encoding="utf-8-sig")
print("有年度名义值的国家数:", mw["annual_nom"].notna().sum())
print("有PPP值的国家数:", mw["annual_ppp"].notna().sum())

print("\n=== 维基表中出现的名称（前80）===")
print(" | ".join(mw["wiki_name"].tolist()[:80]))
print("\n=== 后80 ===")
print(" | ".join(mw["wiki_name"].tolist()[80:]))

print("\n=== 2024分类国家（96）===")
with open(os.path.join(DATA, "final_v2.csv"), encoding="utf-8-sig") as f:
    d = list(csv.DictReader(f))
print(" | ".join(r["entity"] for r in d))
