# -*- coding: utf-8 -*-
"""2010年粗钢产量：SSY2012 解析结果 -> ISO3，剔除汇总行，输出 data/steel_2010.csv。
核对：国家合计 vs worldsteel 公布的 2010 年世界产量 1,433 Mt；并与本项目 steel_countries.csv 的 2010 列交叉核对。"""
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
RAWCSV = os.path.join(DATA, "steel_2010_raw.csv")
OUT = os.path.join(DATA, "steel_2010.csv")

SSY2ISO = {
    "Austria": "AUT", "Belgium": "BEL", "Bulgaria": "BGR", "Czech Republic": "CZE",
    "Denmark": "DNK", "Germany": "DEU", "Finland": "FIN", "France": "FRA", "Greece": "GRC",
    "Hungary": "HUN", "Italy": "ITA", "Latvia": "LVA", "Luxembourg": "LUX",
    "Netherlands": "NLD", "Poland": "POL", "Portugal": "PRT", "Romania": "ROU",
    "Slovak Republic": "SVK", "Slovenia": "SVN", "Spain": "ESP", "Sweden": "SWE",
    "United Kingdom": "GBR", "Albania": "ALB", "Bosnia-Herzegovina": "BIH", "Croatia": "HRV",
    "Macedonia": "MKD", "Montenegro": "MNE", "Norway": "NOR", "Serbia": "SRB",
    "Switzerland": "CHE", "Turkey": "TUR", "Azerbaijan": "AZE", "Byelorussia": "BLR",
    "Kazakhstan": "KAZ", "Moldova": "MDA", "Russia": "RUS", "Ukraine": "UKR",
    "Uzbekistan": "UZB", "Canada": "CAN", "Cuba": "CUB", "El Salvador": "SLV",
    "Guatemala": "GTM", "Mexico": "MEX", "Trinidad and Tobago": "TTO",
    "United States": "USA", "Argentina": "ARG", "Brazil": "BRA", "Chile": "CHL",
    "Colombia": "COL", "Ecuador": "ECU", "Paraguay": "PRY", "Peru": "PER", "Uruguay": "URY",
    "Venezuela": "VEN", "Algeria": "DZA", "Egypt": "EGY", "Ghana": "GHA", "Kenya": "KEN",
    "Libya": "LBY", "Mauritania": "MRT", "Morocco": "MAR", "Nigeria": "NGA",
    "South Africa": "ZAF", "Tunisia": "TUN", "Zimbabwe": "ZWE", "Iran": "IRN",
    "Israel": "ISR", "Jordan": "JOR", "Qatar": "QAT", "Saudi Arabia": "SAU", "Syria": "SYR",
    "United Arab Emirates": "ARE", "China": "CHN", "India": "IND", "Indonesia": "IDN",
    "Japan": "JPN", "DPR Korea (e)": "PRK", "South Korea": "KOR", "Malaysia": "MYS",
    "Mongolia": "MNG", "Myanmar": "MMR", "Pakistan": "PAK", "Philippines": "PHL",
    "Singapore": "SGP", "Sri Lanka": "LKA", "Taiwan, China": "TWN", "Thailand": "THA",
    "Viet Nam": "VNM", "Australia": "AUS", "New Zealand": "NZL",
    "Uganda": "UGA", "Zaire": "COD",
}
AGGREGATES = {"European Union (27)", "Other Europe", "CIS", "North America",
              "South America", "Middle East", "Africa", "Asia", "Oceania", "World",
              "Serbia and Montenegro"}

raw = pd.read_csv(RAWCSV)
raw = raw[~raw["name"].astype(str).str.contains("Steel Statistical Yearbook", na=False)].copy()
raw["name"] = raw["name"].astype(str).str.strip()
raw["code"] = raw["name"].map(SSY2ISO)

num = raw.copy()
ycols = [c for c in num.columns if str(c).isdigit()]
for c in ycols:
    num[c] = pd.to_numeric(num[c], errors="coerce")

country = num[num["code"].notna()]
unmapped = raw[raw["code"].isna() & ~raw["name"].isin(AGGREGATES)]["name"].tolist()
print("未映射行:", unmapped or "无")
agg = num[num["name"].isin(AGGREGATES) & (num["name"] != "World")]

sum2010 = country["2010"].sum()
print(f"\n国家行={len(country)}   2010国家合计={sum2010:,.0f} kt = {sum2010/1000:,.0f} Mt")
print(f"worldsteel 公布 2010 世界产量 = 1,433 Mt；差额 = {(1433000 - sum2010)/1000:,.1f} Mt（未报告国家）")

print("\n2010锚点核对:")
for c, exp in {"CHN": 638743, "JPN": 109599, "USA": 80495, "IND": 68976, "RUS": 66942,
               "KOR": 58914, "DEU": 43830, "UKR": 33432, "BRA": 32948, "TUR": 29143}.items():
    got = float(country[country["code"] == c]["2010"].iloc[0])
    print(f"  {c}: 解析={got:,.0f} 预期={exp:,} {'OK' if abs(got-exp) < 1 else 'DIFF'}")

# 与 steel_countries.csv 的2010列交叉核对
wk = pd.read_csv(os.path.join(DATA, "steel_countries.csv"))
steel_iso = {}
for _, r in wk.iterrows():
    if pd.notna(r["2010"]):
        steel_iso[r["name"].strip()] = float(r["2010"])  # 单位 Mt
ISO_OF_WIKI = {"Algeria": "DZA", "Argentina": "ARG", "Australia": "AUS", "Austria": "AUT",
               "Belgium": "BEL", "Brazil": "BRA", "Canada": "CAN", "Chile": "CHL",
               "China": "CHN", "Colombia": "COL", "Czech Republic": "CZE", "Egypt": "EGY",
               "Finland": "FIN", "France": "FRA", "Germany": "DEU", "Greece": "GRC",
               "India": "IND", "Indonesia": "IDN", "Iran": "IRN", "Italy": "ITA",
               "Japan": "JPN", "Kazakhstan": "KAZ", "Malaysia": "MYS", "Mexico": "MEX",
               "Netherlands": "NLD", "Poland": "POL", "Portugal": "PRT", "Romania": "ROU",
               "Russia": "RUS", "Saudi Arabia": "SAU", "Slovakia": "SVK", "South Africa": "ZAF",
               "South Korea": "KOR", "Spain": "ESP", "Sweden": "SWE", "Taiwan": "TWN",
               "Thailand": "THA", "Turkey": "TUR", "Ukraine": "UKR", "United Kingdom": "GBR",
               "United States": "USA", "Vietnam": "VNM"}
print("\n与 steel_countries.csv(2010列, Mt) 交叉核对:")
diff = 0
for nm, mt in steel_iso.items():
    iso = ISO_OF_WIKI.get(nm)
    if not iso:
        continue
    row = country[country["code"] == iso]
    if row.empty:
        continue
    got = float(row["2010"].iloc[0]) / 1000.0
    if abs(got - mt) > 0.05:
        print(f"  DIFF {nm}: SSY={got:.1f} wiki={mt:.1f}")
        diff += 1
print(f"  差异国家数={diff}")

v2 = pd.read_csv(os.path.join(DATA, "final_v2.csv"))
need = set(v2["code"])
have = set(country["code"])
print("\n96实体中无SSY2010行(=无产量):", sorted(need - have))
out = country[["name", "code", "2010"]].rename(columns={"name": "ssy_name", "2010": "steel_kt_2010"})
out = out[out["code"].isin(need)].sort_values("steel_kt_2010", ascending=False)
out.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"\n写入 {OUT} 行数={len(out)}")
