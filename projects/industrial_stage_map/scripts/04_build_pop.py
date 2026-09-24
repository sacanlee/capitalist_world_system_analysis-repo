# -*- coding: utf-8 -*-
"""从 owid_pop_lr.csv 提取2024年人口及中国基准年人口，输出 data/pop_panel.csv。"""
import json
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw")
DATA = os.path.join(BASE, "data")

df = pd.read_csv(os.path.join(RAW, "owid_pop_lr.csv"))
df = df.rename(columns={"Entity": "entity", "Code": "code", "Year": "year"})
df["pop"] = df["Population"].fillna(df["Population (projections) (Projected)"])
print("raw rows:", len(df), "| dup (entity,code,year):", df.duplicated(["entity", "code", "year"]).sum())

df = df.dropna(subset=["pop"])
g = df.groupby(["entity", "code", "year"], as_index=False)["pop"].max()

need_years = [1990, 2000, 2012, 2024]
sub = g[g["year"].isin(need_years)]
out = sub.pivot(index=["entity", "code"], columns="year", values="pop").reset_index()
out.columns = ["entity", "code", "pop1990", "pop2000", "pop2012", "pop2024"]
print("pivot rows:", len(out))

# 只保留真实国家/地区：code 出现在 Natural Earth ADM0_A3 或 ISO_A3 集合
geo = json.load(open(os.path.join(RAW, "ne_110m_countries.geojson"), encoding="utf-8"))
iso = set()
for f in geo["features"]:
    p = f["properties"]
    for k in ("ADM0_A3", "ISO_A3", "ISO_A3_EH", "BRK_A3", "SOV_A3"):
        v = p.get(k)
        if v and v != "-99":
            iso.add(v)
iso |= {"TWN"}

out["is_country"] = out["code"].isin(iso)
out.to_csv(os.path.join(DATA, "pop_panel.csv"), index=False, encoding="utf-8-sig")

for c in ["China", "Taiwan", "India", "United States", "Indonesia", "Nigeria", "Poland", "Russia", "Ethiopia"]:
    r = out[out["entity"] == c]
    print(c, r[["code", "pop1990", "pop2000", "pop2012", "pop2024"]].values.tolist())

big = out[(out["is_country"]) & (out["pop2024"] >= 10_000_000)].sort_values("pop2024", ascending=False)
print("\n真实国家 pop>=10M 数量:", len(big))
print(big[["entity", "code", "pop2024"]].to_string(index=False))
