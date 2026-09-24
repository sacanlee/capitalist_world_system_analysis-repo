# -*- coding: utf-8 -*-
"""1995年粗钢产量：由 SSY2003 解析结果（data/steel_1995_raw.csv）映射到 ISO3，
剔除汇总行，输出 data/steel_1995.csv；并用 SSY 世界合计与已知锚点核对。"""
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
SRC = os.path.join(DATA, "steel_1995_raw.csv")
OUT = os.path.join(DATA, "steel_1995.csv")

SSY2ISO = {
    "Austria": "AUT", "Belgium": "BEL", "Denmark": "DNK", "Finland": "FIN", "France": "FRA",
    "F.R. Germany": "DEU", "Greece": "GRC", "Ireland": "IRL", "Italy": "ITA",
    "Luxembourg": "LUX", "Netherlands": "NLD", "Portugal": "PRT", "Spain": "ESP",
    "Sweden": "SWE", "United Kingdom": "GBR", "Albania": "ALB", "Bosnia-Herzegovina": "BIH",
    "Bulgaria": "BGR", "Croatia": "HRV", "Czech Republic": "CZE", "Hungary": "HUN",
    "Macedonia": "MKD", "Norway": "NOR", "Poland": "POL", "Romania": "ROU",
    "Slovak Republic": "SVK", "Slovenia": "SVN", "Switzerland": "CHE", "Turkey": "TUR",
    "Byelorussia": "BLR", "Armenia": "ARM", "Azerbaijan": "AZE", "Georgia": "GEO",
    "Kazakhstan": "KAZ", "Moldova": "MDA", "Russia": "RUS", "Ukraine": "UKR",
    "Uzbekistan": "UZB", "Estonia": "EST", "Latvia": "LVA", "Lithuania": "LTU",
    "Canada": "CAN", "Cuba": "CUB", "Dominican Republic": "DOM", "El Salvador": "SLV",
    "Guatemala": "GTM", "Mexico": "MEX", "Trinidad and Tobago": "TTO",
    "United States": "USA", "Argentina": "ARG", "Brazil": "BRA", "Chile": "CHL",
    "Colombia": "COL", "Ecuador": "ECU", "Paraguay": "PRY", "Peru": "PER", "Uruguay": "URY",
    "Venezuela": "VEN", "Algeria": "DZA", "Angola (e)": "AGO", "Egypt": "EGY",
    "Ghana": "GHA", "Kenya": "KEN", "Libya": "LBY", "Mauritania": "MRT", "Morocco": "MAR",
    "Nigeria": "NGA", "South Africa": "ZAF", "Tunisia": "TUN", "Uganda (e)": "UGA",
    "Zaire (e)": "COD", "Zimbabwe": "ZWE", "Iran": "IRN", "Israel": "ISR", "Jordan": "JOR",
    "Qatar": "QAT", "Saudi Arabia": "SAU", "Syria": "SYR", "United Arab Emirates": "ARE",
    "Bangladesh": "BGD", "China": "CHN", "Hong Kong (e)": "HKG", "India": "IND",
    "Indonesia": "IDN", "Japan": "JPN", "D.P.R. Korea (e)": "PRK", "South Korea": "KOR",
    "Malaysia": "MYS", "Myanmar (e)": "MMR", "Pakistan": "PAK", "Philippines": "PHL",
    "Singapore": "SGP", "Sri Lanka (e)": "LKA", "Chinese Taipei": "TWN", "Thailand": "THA",
    "Viet Nam": "VNM", "Australia": "AUS", "New Zealand": "NZL",
}
AGGREGATES = {"European Union (15)", "Other Europe", "C.I.S.", "Baltic States",
              "former U.S.S.R.", "North America", "South America", "Africa",
              "Middle East", "Asia", "Oceania", "World", "F.R. Yugoslavia"}

raw = pd.read_csv(SRC)
raw = raw[~raw["name"].str.contains("Steel Statistical Yearbook", na=False)].copy()
raw["name"] = raw["name"].str.strip()
raw["code"] = raw["name"].map(SSY2ISO)

agg_rows = raw[raw["name"].isin(AGGREGATES)]
country_rows = raw[raw["code"].notna()].copy()
unmapped = raw[raw["code"].isna() & ~raw["name"].isin(AGGREGATES)]["name"].tolist()
print("未映射行(既非国家也非汇总):", unmapped or "无")

num = country_rows.copy()
for c in [c for c in num.columns if c.isdigit()]:
    num[c] = pd.to_numeric(num[c], errors="coerce")

print(f"\n国家行={len(num)}")
print("世界合计核对(kt): 解析国家合计=%.0f  SSY表World行=%.0f" % (
    num["1995"].sum(), agg_rows[agg_rows["name"] == "World"]["1995"].astype(float).iloc[0]))
print("            差异=%.1f%% (国家合计与世界行的差=未报告国家/估计)" % (
    (num['1995'].sum() / float(agg_rows[agg_rows['name'] == 'World']['1995'].iloc[0]) - 1) * 100))

anchors = {"CHN": 95360, "JPN": 101640, "USA": 95191, "RUS": 51589, "IND": 22003,
           "KOR": 36772, "DEU": 42051, "UKR": 22309, "BRA": 25076, "ITA": 27766}
print("\n1995锚点核对:")
for c, exp in anchors.items():
    got = float(num[num["code"] == c]["1995"].iloc[0])
    print(f"  {c}: 解析={got:,.0f}  预期={exp:,}  {'OK' if abs(got - exp) < 1 else 'DIFF'}")

v2 = pd.read_csv(os.path.join(DATA, "final_v2.csv"))
need = set(v2["code"])
have = set(num["code"])
print("\n96实体中无SSY行(=1995无产量):", sorted(need - have))
print("映射到但不在96内:", sorted(have - need))

out = num[["name", "code", "1995"]].rename(columns={"name": "ssy_name", "1995": "steel_kt_1995"})
out = out[out["code"].isin(need)].sort_values("steel_kt_1995", ascending=False)
out.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"\n写入 {OUT}  行数={len(out)}")
print(out.head(20).to_string(index=False))
