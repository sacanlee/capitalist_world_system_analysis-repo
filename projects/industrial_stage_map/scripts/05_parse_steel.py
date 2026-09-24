# -*- coding: utf-8 -*-
"""解析维基钢铁表(表0=2015-2025, 表1=1980/1990/2000/2010-2015)，输出 data/steel.csv。"""
import os
import re

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEEL_HTML = os.path.join(BASE, "..", "productivity_compare", "raw", "wiki_steel.html")
DATA = os.path.join(BASE, "data")

tabs = pd.read_html(STEEL_HTML)
t0, t1 = tabs[0], tabs[1]
print("t0 cols:", t0.columns.tolist())
print("t1 cols:", t1.columns.tolist())

# 提取年份列名中的数字
def year_cols(t):
    m = {}
    for c in t.columns:
        mm = re.match(r"^(\d{4})", str(c).strip())
        if mm:
            m[int(mm.group(1))] = c
    return m

y0, y1 = year_cols(t0), year_cols(t1)
print("t0 years:", sorted(y0), "\nt1 years:", sorted(y1))

frames = []
for t, ym in ((t0, y0), (t1, y1)):
    cc = t.columns[0]
    d = t[[cc]].copy()
    d.columns = ["name"]
    for year, col in ym.items():
        d[year] = pd.to_numeric(
            t[col].astype(str).str.replace(r"\[.*?\]", "", regex=True).str.replace(",", "").str.strip(),
            errors="coerce",
        )
    frames.append(d)

steel = frames[0].merge(frames[1], on="name", how="outer")
steel = steel[steel["name"].notna()]
steel = steel[steel["name"].str.lower() != "world"]

out = steel[["name", 1980, 1990, 2000, 2010, 2011, 2012, 2023, 2024, 2025]].dropna(subset=[2024, 2025, 1990], how="all")
out.to_csv(os.path.join(DATA, "steel_countries.csv"), index=False, encoding="utf-8-sig")
print("\ncountries in steel table:", len(out))
print(out.to_string(index=False))
