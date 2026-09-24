# -*- coding: utf-8 -*-
"""诊断1995年三套数据（电力/钢铁/人口）对 final_v2.csv 96国名单的覆盖情况。"""
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
RAW = os.path.join(BASE, "raw")

v2 = pd.read_csv(os.path.join(DATA, "final_v2.csv"))
codes = list(v2["code"])
name = dict(zip(v2["code"], v2["entity"]))

# 电力
ele = pd.read_csv(os.path.join(RAW, "owid_elec_gen.csv"))
e95 = ele[(ele["year"] == 1995) & (ele["code"].notna())].set_index("code")["total_generation__twh"]
ele_codes = set(e95.index)

# 钢铁（解析结果，仅国家行）
steel = pd.read_csv(os.path.join(DATA, "steel_1995_raw.csv"))
bad = steel["name"].str.contains("Steel Statistical Yearbook", na=False)
steel = steel[~bad]

# 人口
pop = pd.read_csv(os.path.join(RAW, "owid_pop_lr.csv"))
p95 = pop[(pop["Year"] == 1995) & (pop["Code"].notna())].set_index("Code")["Population"]
pop_codes = set(p95.index)

print(f"名单国家数={len(codes)}")
print(f"1995 电力数据国家数={len(ele_codes & set(codes))} 缺失={len([c for c in codes if c not in ele_codes])}")
print(f"1995 人口数据国家数={len(pop_codes & set(codes))} 缺失={len([c for c in codes if c not in pop_codes])}")

miss_e = [f"{c}({name[c]})" for c in codes if c not in ele_codes]
print("\n=== 缺1995电力 ===")
print(", ".join(miss_e) if miss_e else "无")
miss_p = [f"{c}({name[c]})" for c in codes if c not in pop_codes]
print("\n=== 缺1995人口 ===")
print(", ".join(miss_p) if miss_p else "无")

print("\n=== 1995电力值预览（部分） ===")
print(e95.reindex([c for c in codes if c in ele_codes]).dropna().sort_values(ascending=False).head(25).to_string())
