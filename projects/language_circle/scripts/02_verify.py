# -*- coding: utf-8 -*-
"""02_verify.py — 独立复核
方法独立于01: 直接重读原始csv与WPP demo原始行, 不以01的中间产物为准。
"""
import csv
import os
import sys

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
DEMO = r"C:\Users\Administrator\Desktop\zhihu\task\language\data\raw\wpp2024_demo.csv"
sys.path.insert(0, os.path.join(BASE, "scripts"))
from circles_def import COUNTRIES, SUBS, TOPS, AGG

errors = []


def check(name, a, b, tol=0.01):
    ok = abs(a - b) <= tol * max(1.0, abs(b))
    print(f"[{'OK ' if ok else 'FAIL'}] {name}: {a:,.4f} vs {b:,.4f}")
    if not ok:
        errors.append(name)


# ---- 1) 各国人口加总 = world_totals ----
tot = {y: 0.0 for y in ("2025", "2050", "2055")}
with open(os.path.join(DATA, "pop_by_country_2015_2070.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        if r["year"] in tot:
            tot[r["year"]] += float(r["pop_total"])
wt = {}
with open(os.path.join(DATA, "world_totals_2015_2070.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        wt[r["year"]] = float(r["pop_total"])
for y in ("2025", "2050", "2055"):
    check(f"各国加总=全球 {y}", tot[y], wt[y], tol=0.001)

# ---- 2) WPP demo 原始 World 行 (独立来源) ----
df = pd.read_csv(DEMO, usecols=["LocTypeName", "Variant", "Time", "Births", "TPopulation1July"],
                 low_memory=False)
w = df[(df["LocTypeName"] == "World") & (df["Variant"] == "Medium")]
for y in (2025, 2050, 2055):
    row = w[w["Time"] == y]
    if len(row):
        check(f"WPP demo World 人口 {y}", float(row["TPopulation1July"].iloc[0]), wt[str(y)], 0.001)
b25 = float(w[w["Time"] == 2025]["Births"].iloc[0])
bsum = 0.0
with open(os.path.join(DATA, "births_1950_2055.csv"), encoding="utf-8-sig") as f:
    rd = csv.DictReader(f)
    for r in rd:
        bsum += float(r["2025"])
check("237国出生加总=WPP World出生 2025", bsum, b25, 0.001)

# ---- 3) 与01输出对照 ----
stats = {}
with open(os.path.join(DATA, "circle_stats.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        stats[r["code"]] = r

pop = {}
with open(os.path.join(DATA, "pop_by_country_2015_2070.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        pop.setdefault(r["iso3"], {})[r["year"]] = float(r["pop_total"])
br = {}
with open(os.path.join(DATA, "births_1950_2055.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        br[r["iso3"]] = float(r["2025"])


def p25(iso):
    comps = AGG.get(iso, [iso])
    return sum(pop[c]["2025"] for c in comps)


# 大圈重算 (显式写出成员, 不走circles_def的聚合逻辑)
E = ["GBR","USA","CAN","NLD","NOR","SWE","DNK","FIN","ISL","DEU","AUT","IRL","CYP","AUS","NZL",
     "SGP","PHL","ZAF","NGA","MWI","GHA","BWA","ZWE","LBR","JAM","ISR","PAK","IND","BGD","NPL",
     "KEN","TZA","UGA","RWA","BDI","COM","ETH","SSD","VNM"]
A = ["SAU","DZA","EGY","IRQ","MAR","SDN","YEM","SYR","TUN","JOR","LBY","ARE","LBN","OMN","KWT",
     "MRT","QAT","BHR","DJI","COM","PSE","TCD"]
C = ["CHN","PRK","KOR","JPN","SGP","MYS","VNM","LAO","KHM","MMR"]
check("E圈2025重算", sum(p25(i) for i in E), float(stats["E"]["pop2025"]), 1e-9)
check("A圈2025重算", sum(p25(i) for i in A), float(stats["A"]["pop2025"]), 1e-9)
check("C圈2025重算", sum(p25(i) for i in C), float(stats["C"]["pop2025"]), 1e-9)

# 子圈成员数
n_e1 = len([i for i in COUNTRIES if "E1" in COUNTRIES[i][2]])
check("E1国家数", n_e1, float(stats["E1"]["n"]), 0)
n_a = len(A)
check("A圈国家数", n_a, float(stats["A"]["n"]), 0)

# 中国聚合
check("中国=CHN+HKG+MAC+TWN 2025",
      pop["CHN"]["2025"] + pop["HKG"]["2025"] + pop["MAC"]["2025"] + pop["TWN"]["2025"],
      float([r for r in csv.DictReader(open(os.path.join(DATA, "country_panel.csv"), encoding="utf-8-sig")) if r["iso3"] == "CHN"][0]["pop2025"]), 1e-9)

# ---- 4) 重点国家对照WPP已知值 ----
spot = {"IND": (2025, 1463865.527), "CHN": (2025, 1416096.093), "USA": (2025, 347275.811),
        "NGA": (2025, 237527.788), "IDN": (2025, 285721.236), "BRA": (2025, 212812.397)}
for iso, (y, v) in spot.items():
    check(f"{iso} {y} 人口(千)", pop[iso][str(y)], v, 1e-6)

# ---- 5) 占比重算（CSV存4位小数, 容差放宽至5e-4%）----
for code in ("E", "C", "A", "ALL"):
    s = stats[code]
    check(f"{code}占比2025重算", float(s["pop2025"]) / wt["2025"] * 100, float(s["share2025"]), 1e-4)
    check(f"{code}出生占比重算", float(s["births2025"]) / b25 * 100, float(s["bshare2025"]), 1e-4)

# ALL = 世界 - REST
check("ALL+REST=世界 2025", float(stats["ALL"]["pop2025"]) + float(stats["REST"]["pop2025"]), wt["2025"], 1e-6)
check("ALL+REST=世界 出生", float(stats["ALL"]["births2025"]) + float(stats["REST"]["births2025"]), b25, 1e-6)

print("\n" + ("全部通过 ✓" if not errors else f"发现 {len(errors)} 处错误: {errors}"))
