# -*- coding: utf-8 -*-
"""合并人口/钢铁/电力，计算中国基准、各国得分并分类。输出 data/analysis.csv。"""
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw")
DATA = os.path.join(BASE, "data")
ELEC = os.path.join(BASE, "..", "productivity_compare", "raw", "owid_electricity.csv")

YEAR = 2024

# ---------- 中国基准 ----------
CHN = {"steel": {1990: 66.4, 2000: 128.5, 2012: 724.7}, "elec": {1990: 621.20, 2000: 1355.60, 2012: 4987.54}}

pop = pd.read_csv(os.path.join(DATA, "pop_panel.csv"))
pop = pop[pop["is_country"]]
chn_pop = pop[pop["code"] == "CHN"].iloc[0]
base = {}
for y in (1990, 2000, 2012):
    p = float(chn_pop[f"pop{y}"])
    base[y] = {
        "pop": p,
        "pc_steel_kg": CHN["steel"][y] * 1e9 / p,
        "pc_elec_kwh": CHN["elec"][y] * 1e9 / p,
    }
print("=== 中国基准（UN WPP2024人口）===")
for y, b in base.items():
    print(f"{y}: pop={b['pop']:,.0f}  人均钢={b['pc_steel_kg']:.2f} kg  人均电={b['pc_elec_kwh']:.1f} kWh")

# ---------- 各国数据 ----------
steel = pd.read_csv(os.path.join(DATA, "steel_countries.csv"))
SUM2024 = steel["2024"].sum()
print(f"\n钢铁表2024年合计(不含Others行)={SUM2024:.1f} Mt, worldsteel世界总产1886.3, Others行={steel[steel['name'].str.contains('Other')]['2024'].values}")

STEEL_ISO = {
    "Algeria": "DZA", "Argentina": "ARG", "Australia": "AUS", "Austria": "AUT", "Bahrain": "BHR",
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
    "Uzbekistan": "UZB", "Vietnam": "VNM",
}
steel = steel[~steel["name"].str.contains("Other", na=False)].copy()
steel["code"] = steel["name"].map(STEEL_ISO)
assert steel["code"].notna().all(), steel[steel["code"].isna()]["name"].tolist()
steel = steel[["code", "name", "1990", "2000", "2012", "2023", "2024", "2025"]].rename(
    columns={"name": "steel_name", "1990": "s1990", "2000": "s2000", "2012": "s2012", "2023": "s2023", "2024": "s2024", "2025": "s2025"}
)

ele = pd.read_csv(ELEC).rename(columns={"Entity": "entity", "Code": "code", "Year": "year", "Total electricity": "elec"})
ele24 = ele[ele["year"] == YEAR][["code", "entity", "elec"]].dropna(subset=["code"])
print("电力2024实体数:", len(ele24))

df = pop.merge(ele24[["code", "elec"]], on="code", how="left").merge(steel, on="code", how="left")
df["s2024"] = df["s2024"].fillna(0.0)

df["pop2024_m"] = df["pop2024"] / 1e6
df["pc_steel_kg"] = df["s2024"] * 1e9 / df["pop2024"]
df["pc_elec_kwh"] = df["elec"] * 1e9 / df["pop2024"]

for y in (1990, 2000, 2012):
    df[f"r_steel{y}"] = df["pc_steel_kg"] / base[y]["pc_steel_kg"]
    df[f"r_elec{y}"] = df["pc_elec_kwh"] / base[y]["pc_elec_kwh"]
    df[f"score{y}"] = df[f"r_steel{y}"] + df[f"r_elec{y}"]

IMF = {
    "AUS", "AUT", "BEL", "CAN", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HKG",
    "ISL", "IRL", "ISR", "ITA", "JPN", "KOR", "LVA", "LTU", "LUX", "MAC", "MLT", "NLD", "NZL",
    "NOR", "PRT", "PRI", "SMR", "SGP", "SVK", "SVN", "ESP", "SWE", "CHE", "TWN", "GBR", "USA", "AND",
}

def classify(row):
    if row["code"] == "CHN":
        return "中国"
    if row["code"] in IMF:
        return "发达国家"
    if row["score2012"] > 2:
        return "工业化国家"
    if row["score2000"] > 2:
        return "工业化中期国家"
    if row["score1990"] > 2:
        return "工业化起步国家"
    return "准备工业化国家"

df["category"] = df.apply(classify, axis=1)
df = df[df["pop2024"] >= 10_000_000].sort_values("pop2024", ascending=False)
df.to_csv(os.path.join(DATA, "analysis.csv"), index=False, encoding="utf-8-sig")

cols = ["entity", "code", "pop2024_m", "s2024", "elec", "pc_steel_kg", "pc_elec_kwh", "score2012", "score2000", "score1990", "category"]
pd.set_option("display.width", 220)
print(df[cols].to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
print("\n=== 分类汇总 ===")
print(df.groupby("category").agg(n=("code", "size"), pop=("pop2024", "sum")).sort_values("pop", ascending=False).to_string())
print("\n电力缺失:", df[df["elec"].isna()]["entity"].tolist())
