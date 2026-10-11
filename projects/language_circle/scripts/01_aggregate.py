# -*- coding: utf-8 -*-
"""01_aggregate.py — 人口与出生提取、按圈层聚合
数据: UN WPP2024 中方案（沿用 language 项目缓存, 未重新下载）
输出: data/country_panel.csv, data/circle_stats.csv
"""
import csv
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
sys.path.insert(0, os.path.join(BASE, "scripts"))
from circles_def import COUNTRIES, SUBS, TOPS, AGG, country_tops

YEARS = ("2025", "2050", "2055")

# ---- 读人口 ----
pop = {}  # iso -> {year: thousands}
with open(os.path.join(DATA, "pop_by_country_2015_2070.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        pop.setdefault(r["iso3"], {})[r["year"]] = float(r["pop_total"])

# ---- 读出生 ----
births = {}  # iso -> {year: thousands}
with open(os.path.join(DATA, "births_1950_2055.csv"), encoding="utf-8-sig") as f:
    rd = csv.DictReader(f)
    for r in rd:
        births[r["iso3"]] = r

# ---- 世界总量 ----
world = {}
with open(os.path.join(DATA, "world_totals_2015_2070.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        world[r["year"]] = float(r["pop_total"])
world_births_2025 = sum(float(r["2025"]) for r in births.values())

# ---- 校验: 圈内国家数据齐备 ----
missing = []
for iso in COUNTRIES:
    if iso == "CYN":
        continue
    if iso not in pop or iso not in births:
        missing.append(iso)
assert not missing, f"缺数据: {missing}"

# ---- 国家面板（含中国=CHN+HKG+MAC+TWN 聚合）----
panel = {}  # iso -> dict
for iso, (cn, en, subs) in COUNTRIES.items():
    if iso == "CYN":
        continue
    comps = AGG.get(iso, [iso])
    rec = {"iso3": iso, "name_cn": cn, "name_en": en, "subs": " ".join(subs)}
    for y in YEARS:
        rec["pop" + y] = sum(pop[c][y] for c in comps)
    rec["births2025"] = sum(float(births[c]["2025"]) for c in comps)
    panel[iso] = rec

# 自查: CHN 聚合 = 四部分
s = sum(pop[c]["2025"] for c in ["CHN", "HKG", "MAC", "TWN"])
assert abs(panel["CHN"]["pop2025"] - s) < 1e-6

# ---- 聚合函数 ----
def agg(members):
    r = {"n": len(members)}
    for y in YEARS:
        r["pop" + y] = sum(panel[i]["pop" + y] for i in members)
    r["births2025"] = sum(panel[i]["births2025"] for i in members)
    return r


def shares(r):
    for y in YEARS:
        r["share" + y] = r["pop" + y] / world[y] * 100
    r["bshare2025"] = r["births2025"] / world_births_2025 * 100
    return r


# 子圈
stats = {}
for sub, (cn, en, top) in SUBS.items():
    members = [i for i in COUNTRIES if sub in COUNTRIES[i][2] and i != "CYN"]
    stats[sub] = dict(agg(members), level="sub", name_cn=cn, name_en=en, top=top, shares_=None)
    shares(stats[sub])

# 大圈 = 成员并集(去重)
for top, (cn, en) in TOPS.items():
    members = [i for i in COUNTRIES if top in country_tops(COUNTRIES[i][2]) and i != "CYN"]
    stats[top] = dict(agg(members), level="top", name_cn=cn, name_en=en, top=top)
    shares(stats[top])

# 全体覆盖（任一圈）
allc = [i for i in COUNTRIES if i != "CYN"]
stats["ALL"] = dict(agg(allc), level="all", name_cn="任一文化圈合计（去重）",
                    name_en="Any Sphere (deduplicated)", top="ALL")
shares(stats["ALL"])
rest = {y: world[y] - stats["ALL"]["pop" + y] for y in YEARS}
stats["REST"] = dict(n=None, level="rest", name_cn="未列入圈层国家",
                     name_en="Not in listed spheres", top="REST",
                     **{"pop" + y: rest[y] for y in YEARS},
                     births2025=world_births_2025 - stats["ALL"]["births2025"])
shares(stats["REST"])

# ---- 写出 ----
os.makedirs(DATA, exist_ok=True)
with open(os.path.join(DATA, "country_panel.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["iso3", "name_cn", "name_en", "subs", "pop2025", "pop2050", "pop2055", "births2025"])
    for iso in COUNTRIES:
        if iso == "CYN":
            continue
        r = panel[iso]
        w.writerow([r["iso3"], r["name_cn"], r["name_en"], r["subs"],
                    f"{r['pop2025']:.3f}", f"{r['pop2050']:.3f}", f"{r['pop2055']:.3f}",
                    f"{r['births2025']:.3f}"])

COLS = ["code", "level", "name_cn", "name_en", "top", "n",
        "pop2025", "pop2050", "pop2055", "births2025",
        "share2025", "share2050", "share2055", "bshare2025"]
with open(os.path.join(DATA, "circle_stats.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(COLS)
    # 先大圈后子圈
    for top in TOPS:
        for code in [top] + [s for s in SUBS if SUBS[s][2] == top]:
            r = stats[code]
            w.writerow([code, r["level"], r["name_cn"], r["name_en"], r["top"], r["n"],
                        f"{r['pop2025']:.3f}", f"{r['pop2050']:.3f}", f"{r['pop2055']:.3f}",
                        f"{r['births2025']:.3f}", f"{r['share2025']:.4f}", f"{r['share2050']:.4f}",
                        f"{r['share2055']:.4f}", f"{r['bshare2025']:.4f}"])
    for code in ("ALL", "REST"):
        r = stats[code]
        w.writerow([code, r["level"], r["name_cn"], r["name_en"], r["top"], r["n"] or "",
                    f"{r['pop2025']:.3f}", f"{r['pop2050']:.3f}", f"{r['pop2055']:.3f}",
                    f"{r['births2025']:.3f}", f"{r['share2025']:.4f}", f"{r['share2050']:.4f}",
                    f"{r['share2055']:.4f}", f"{r['bshare2025']:.4f}"])

print("世界人口(千人):", {y: f"{world[y]:,.0f}" for y in YEARS})
print("世界出生2025(千人):", f"{world_births_2025:,.1f}")
print("\n=== 大圈 ===")
for top in TOPS:
    r = stats[top]
    print(f"{top:3s} {r['name_cn']:12s} n={r['n']:3d} 2025:{r['pop2025']/1e5:7.2f}亿({r['share2025']:5.2f}%) "
          f"2050:{r['pop2050']/1e5:7.2f}亿({r['share2050']:5.2f}%) 2055:{r['pop2055']/1e5:7.2f}亿({r['share2055']:5.2f}%) "
          f"出生:{r['births2025']/10:8.0f}万({r['bshare2025']:5.2f}%)")
print("\n=== 子圈 ===")
for sub in SUBS:
    r = stats[sub]
    print(f"{sub:7s} {r['name_cn'][:20]:22s} n={r['n']:3d} 2025:{r['pop2025']/1e5:7.2f}亿({r['share2025']:5.2f}%) "
          f"2055:{r['pop2055']/1e5:7.2f}亿({r['share2055']:5.2f}%) 出生:{r['births2025']/10:8.0f}万({r['bshare2025']:5.2f}%)")
r = stats["ALL"]
print(f"\n任一圈合计: n={r['n']} 2025:{r['pop2025']/1e5:.2f}亿({r['share2025']:.2f}%) 出生:{r['births2025']/10:.0f}万({r['bshare2025']:.2f}%)")
r = stats["REST"]
print(f"未列入:     2025:{r['pop2025']/1e5:.2f}亿({r['share2025']:.2f}%) 出生:{r['births2025']/10:.0f}万({r['bshare2025']:.2f}%)")
