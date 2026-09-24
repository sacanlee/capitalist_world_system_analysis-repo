# -*- coding: utf-8 -*-
"""诊断：列出电力缺失国、0钢国及其翻转潜力。"""
import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
ELEC = os.path.join(BASE, "..", "productivity_compare", "raw", "owid_electricity.csv")

df = pd.read_csv(os.path.join(DATA, "analysis.csv"))
out = []
w = out.append

w("=== 电力缺失 (elec isna) ===")
mis = df[df["elec"].isna()]
for _, r in mis.iterrows():
    w(f"{r['entity']} ({r['code']}) pop={r['pop2024_m']:.2f}M steel2024={r['s2024']}")

# 检查OWID中这些国家的可用年份
ele = pd.read_csv(ELEC)
if len(mis):
    for _, r in mis.iterrows():
        sub = ele[ele["Code"] == r["code"]].sort_values("Year")
        last = sub.tail(3)
        w(f"  OWID {r['code']} 最近3年: " + ", ".join(f"{int(y)}={v}" for y, v in zip(last["Year"], last["Total electricity"])))

w("")
w("=== 0钢国家 (s2024==0) 及其score2000/1990 ===")
z = df[df["s2024"] == 0].copy()
z = z.sort_values("r_elec2000", ascending=False)
for _, r in z.iterrows():
    # 翻转到"工业化中期"需要的钢产量(kT)：r_elec2000 + steel_kt*1e6/pop / base2000_pc_steel > 2
    # base2000_pc_steel=101.21 kg
    base2000 = 101.21
    need_mid = max(0.0, (2 - r["r_elec2000"]) * base2000 * r["pop2024"] / 1e6)  # kg->kt: kg*pop/1e6 = kt
    base1990 = 57.56
    need_beg = max(0.0, (2 - r["r_elec1990"]) * base1990 * r["pop2024"] / 1e6)
    w(f"{r['entity']:<22} pop={r['pop2024_m']:6.2f}M r_e2000={r['r_elec2000']:5.3f} r_e1990={r['r_elec1990']:5.3f} "
      f"翻中期需钢={need_mid:8.1f} kt  升起步需钢={need_beg:8.1f} kt  当前类别={r['category']}")

w("")
w("=== 全部国家 score 一览（按类别） ===")
for cat, g in df.groupby("category"):
    w(f"-- {cat}: {len(g)}国")
    for _, r in g.sort_values("pop2024", ascending=False).iterrows():
        w(f"   {r['entity']:<24} s2012={r['score2012']:6.2f} s2000={r['score2000']:6.2f} s1990={r['score1990']:6.2f}")

with open(os.path.join(BASE, "out", "diag.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("done", len(out), "lines")
