# -*- coding: utf-8 -*-
"""交叉校验：data/steel_countries.csv(worldsteel/维基) vs data/bgs_crude_steel.csv(BGS)。
输出 out/steel_crosscheck.txt，并列出BGS独有的国家。"""
import os
import re
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

steel = pd.read_csv(os.path.join(DATA, "steel_countries.csv"))
bgs = pd.read_csv(os.path.join(DATA, "bgs_crude_steel.csv"))

ALIAS = {
    "Czech Republic": "Czech Republic", "Czechia": "Czech Republic",
    "South Korea": "Korea (Rep. of)", "North Korea": "Korea, Dem. P.R. of",
    "United States": "USA", "Turkey": "Turkey", "Russia": "Russia",
    "Bosnia & Herzegovina": "Bosnia & Herzegovina",
    "United Kingdom": "United Kingdom", "Taiwan": "Taiwan",
}
bgs["k"] = bgs["name"].str.strip()
out = []
w = out.append
w(f"{'country':<24}{'ws2024':>10}{'bgs2024':>12}{'diff%':>9}")
bgsmap = {r["k"]: r for _, r in bgs.iterrows()}
matched = set()
for _, r in steel.iterrows():
    nm = r["name"]
    k = ALIAS.get(nm, nm)
    if k in bgsmap:
        b = bgsmap[k]
        v = b["2024"]
        matched.add(k)
        if pd.isna(v):
            w(f"{nm:<24}{r['2024']:>10.1f}{'NaN':>12}{'-':>9}")
        else:
            diff = (r["2024"] - v / 1e6) / (v / 1e6) * 100
            mark = "  <<<" if abs(diff) > 5 else ""
            w(f"{nm:<24}{r['2024']:>10.1f}{v/1e6:>12.2f}{diff:>8.1f}%{mark}")
    else:
        w(f"{nm:<24}{r['2024']:>10.1f}{'--未收录--':>12}")

w("\n=== BGS 独有（未在worldsteel表中）===")
for _, b in bgs.iterrows():
    if b["k"] not in matched and not str(b["k"]).startswith("World"):
        w(f"{b['k']:<28} 2023={b['2023']} 2024={b['2024']} est2024={b['est2024']}")

with open(os.path.join(BASE, "out", "steel_crosscheck.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("done", len(out))
