# -*- coding: utf-8 -*-
"""检查人口CSV与USGS PDF内容。"""
import os

import pandas as pd

RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")

pop = pd.read_csv(os.path.join(RAW, "owid_pop_wpp2024.csv"))
print("pop cols:", pop.columns.tolist())
print("pop years:", pop["Year"].min(), pop["Year"].max(), "rows:", len(pop))
y = 2024
sub = pop[pop["Year"] == y]
print("entities 2024:", sub.shape[0], "with code:", sub["Code"].notna().sum())
for c in ["China", "United States", "India", "Germany", "Taiwan", "Israel", "Poland", "Russia"]:
    r = sub[sub["Entity"] == c]
    if len(r):
        print(c, r.iloc[0]["Code"], int(r.iloc[0].iloc[-1]))
    else:
        print(c, "NOT FOUND")

print()
for f in ["usgs_mcs2025-iron-steel.pdf", "usgs_mcs2026-iron-steel.pdf"]:
    path = os.path.join(RAW, f)
    try:
        from pypdf import PdfReader

        rd = PdfReader(path)
        txt = "\n".join((p.extract_text() or "") for p in rd.pages)
        print("===", f, "pages:", len(rd.pages), "chars:", len(txt))
        print(txt[:1500])
    except Exception as e:
        print("===", f, "ERR", repr(e)[:200])
