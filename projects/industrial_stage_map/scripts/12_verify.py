# -*- coding: utf-8 -*-
"""独立复核（第二实现）：纯csv读入、手写公式，不依赖11脚本的任何中间对象。
逐国比对 data/final.csv 分类，并做手工抽验与边界检查。输出 out/verify.txt"""
import csv
import os
from decimal import Decimal

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
ELEC = os.path.join(BASE, "..", "productivity_compare", "raw", "owid_electricity.csv")
out = []
w = out.append


def rd(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# ---- 1. 人口 ----
pop = {r["code"]: r for r in rd(os.path.join(DATA, "pop_panel.csv")) if r["is_country"] == "True"}
chn = pop["CHN"]
P = {y: float(chn[f"pop{y}"]) for y in (1990, 2000, 2012)}
# 中国总量：钢 Mt，电 TWh
CN_S = {1990: 66.4, 2000: 128.5, 2012: 724.7}
CN_E = {1990: 621.20, 2000: 1355.60, 2012: 4987.54}
base_pc_s = {y: CN_S[y] * 1e9 / P[y] for y in P}
base_pc_e = {y: CN_E[y] * 1e9 / P[y] for y in P}
w("== 中国基准（独立重算）==")
for y in (1990, 2000, 2012):
    w(f"{y}: pop={P[y]:,.0f} 人均钢={base_pc_s[y]:.4f}kg 人均电={base_pc_e[y]:.4f}kWh")

# ---- 2. 电力(2024) ----
elec = {}
for r in rd(ELEC):
    if r["Year"] == "2024" and r["Code"] and r["Total electricity"]:
        elec[r["Code"]] = float(r["Total electricity"])
elec["UKR"] = 96.9  # EIA 修正

# ---- 3. 钢铁 2024 (kt) ----
WS = {"Algeria": "DZA", "Argentina": "ARG", "Australia": "AUS", "Austria": "AUT", "Bahrain": "BHR",
      "Bangladesh": "BGD", "Belarus": "BLR", "Belgium": "BEL", "Brazil": "BRA", "Bulgaria": "BGR",
      "Canada": "CAN", "Chile": "CHL", "China": "CHN", "Colombia": "COL", "Czech Republic": "CZE",
      "Egypt": "EGY", "Finland": "FIN", "France": "FRA", "Germany": "DEU", "Greece": "GRC",
      "Hungary": "HUN", "India": "IND", "Indonesia": "IDN", "Iran": "IRN", "Iraq": "IRQ",
      "Italy": "ITA", "Japan": "JPN", "Kazakhstan": "KAZ", "Kenya": "KEN", "Kuwait": "KWT",
      "Libya": "LBY", "Luxembourg": "LUX", "Malaysia": "MYS", "Mexico": "MEX", "Morocco": "MAR",
      "Netherlands": "NLD", "Nigeria": "NGA", "North Korea": "PRK", "Oman": "OMN", "Pakistan": "PAK",
      "Peru": "PER", "Philippines": "PHL", "Poland": "POL", "Portugal": "PRT", "Qatar": "QAT",
      "Romania": "ROU", "Russia": "RUS", "Saudi Arabia": "SAU", "Serbia": "SRB", "Slovakia": "SVK",
      "South Africa": "ZAF", "South Korea": "KOR", "Spain": "ESP", "Sweden": "SWE",
      "Switzerland": "CHE", "Taiwan": "TWN", "Thailand": "THA", "Turkey": "TUR", "Ukraine": "UKR",
      "United Arab Emirates": "ARE", "United Kingdom": "GBR", "United States": "USA",
      "Uzbekistan": "UZB", "Vietnam": "VNM"}
steel_kt = {}
for r in rd(os.path.join(DATA, "steel_countries.csv")):
    if r["name"] in WS and r["2024"]:
        steel_kt[WS[r["name"]]] = float(r["2024"]) * 1000
BGS = {"Azerbaijan": "AZE", "Angola": "AGO", "Congo, Democratic Republic": "COD", "Ghana": "GHA",
       "Tunisia": "TUN", "Uganda": "UGA", "Zimbabwe": "ZWE", "Cuba": "CUB",
       "Dominican Republic": "DOM", "Guatemala": "GTM", "Ecuador": "ECU", "Venezuela": "VEN",
       "Jordan": "JOR", "Myanmar": "MMR", "Sri Lanka": "LKA",
       "Korea, Dem. P.R. of": "PRK"}
for r in rd(os.path.join(DATA, "bgs_crude_steel.csv")):
    nm = r["name"].strip()
    if nm in ("Syria",):
        steel_kt["SYR"] = 5.0
        continue
    if nm in BGS and r["2024"]:
        steel_kt.setdefault(BGS[nm], float(r["2024"]) / 1000)

# ---- 4. 分类 ----
IMF = {"AUS", "AUT", "BEL", "CAN", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HKG",
       "ISL", "IRL", "ISR", "ITA", "JPN", "KOR", "LVA", "LTU", "LUX", "MAC", "MLT", "NLD", "NZL",
       "NOR", "PRT", "PRI", "SMR", "SGP", "SVK", "SVN", "ESP", "SWE", "CHE", "TWN", "GBR", "USA"}


def score(code, y):
    p = float(pop[code]["pop2024"])
    s = steel_kt.get(code, 0.0) * 1e6 / p        # kg
    e = elec.get(code)
    if e is None:
        return None
    e = e * 1e9 / p                              # kWh
    return s / base_pc_s[y] + e / base_pc_e[y]


cat = {}
for code, r in pop.items():
    if float(r["pop2024"]) < 1e7:
        continue
    if code in ("CHN", "TWN"):
        cat[code] = "中国"
        continue
    if code in IMF:
        cat[code] = "发达国家"
        continue
    s12, s00, s90 = score(code, 2012), score(code, 2000), score(code, 1990)
    cat[code] = ("工业化国家" if s12 > 2 else "工业化中期国家" if s00 > 2
                 else "工业化起步国家" if s90 > 2 else "准备工业化国家")

# ---- 5. 比对 ----
fin = {r["code"]: r for r in rd(os.path.join(DATA, "final.csv"))}
w(f"\n== 比对 final.csv ({len(fin)}国) vs 独立重算 ({len(cat)}国) ==")
mis = 0
for code, c in sorted(cat.items(), key=lambda kv: -float(pop[kv[0]]["pop2024"])):
    fc = fin.get(code, {}).get("category")
    if fc != c:
        mis += 1
        w(f"  不一致 {code} {pop[code]['entity']}: final={fc} verify={c}")
w(f"不一致数 = {mis}")

# ---- 6. 边界国家(人口) ----
w("\n== 人口边界检查(9.5M~10.5M) ==")
for code, r in sorted(pop.items(), key=lambda kv: float(kv[1]["pop2024"])):
    p = float(r["pop2024"])
    if 9.5e6 <= p <= 10.5e6:
        w(f"  {r['entity']:<20} {p/1e6:.3f}M  {'入选' if p>=1e7 else '排除'}")

# ---- 7. 手工抽验 ----
w("\n== 手工抽验 ==")
checks = [("IND", 149.4e9, 2036.52e9, "1450935785"), ("JOR", 300e3 * 1e3, 23.7e9, None),
          ("ECU", 492600e3, 32.7e9, None), ("TJK", 0.0, 22.2e9, None),
          ("USA", 79.5e9, 4302.0e9, None)]
for code, st_kg, el_kwh, popx in checks:
    p = float(pop[code]["pop2024"])
    pcs = st_kg / p
    pce = el_kwh / p
    s12 = pcs / base_pc_s[2012] + pce / base_pc_e[2012]
    s00 = pcs / base_pc_s[2000] + pce / base_pc_e[2000]
    s90 = pcs / base_pc_s[1990] + pce / base_pc_e[1990]
    w(f"  {pop[code]['entity']:<14} pop={p/1e6:.2f}M 人均钢={pcs:.2f}kg 人均电={pce:.1f}kWh "
      f"score2000={s00:.3f} score2012={s12:.3f} -> {cat[code]}")

# ---- 8. 全球人口分母 ----
w("\n== 全球总人口(UN WPP2024, World实体) ==")
KEY = "Population (projections) (Projected)"
for r in rd(os.path.join(BASE, "raw", "owid_pop_lr.csv")):
    if r.get("Year") != "2024" or r.get("Entity") not in ("World", "China"):
        continue
    v = r.get("Population") or r.get(KEY)
    w(f"  {r['Entity']} 2024 = {float(v):,.0f}  (人口列='Population'={'有' if r.get('Population') else '空'})")

with open(os.path.join(BASE, "out", "verify.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("done", len(out))
