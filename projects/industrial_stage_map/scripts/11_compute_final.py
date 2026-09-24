# -*- coding: utf-8 -*-
"""最终计算：人口(UN WPP2024) + 电力(OWID/Ember2024, 乌克兰用EIA) + 钢铁(worldsteel表→BGS补充)
按中国1990/2000/2012基准分类，输出 data/final.csv。"""
import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
ELEC = os.path.join(BASE, "..", "productivity_compare", "raw", "owid_electricity.csv")
YEAR = 2024

# 中国基准总量（worldsteel 粗钢 Mt / Ember 发电 TWh），人口取 UN WPP2024
CHN_TOTAL = {"steel_Mt": {1990: 66.4, 2000: 128.5, 2012: 724.7},
             "elec_TWh": {1990: 621.20, 2000: 1355.60, 2012: 4987.54}}

# ---- 人工修正（每条注明来源，见 out/ 说明）----
FIX_ELEC = {  # code -> (TWh, source)
    "UKR": (96.9, "EIA 2024 (OWID/Ember 只到2022)"),
}
# 钢铁优先用 worldsteel 63国表；缺者用 BGS WMP 2020-2024（同源世界钢协+各国统计局）
FIX_STEEL = {  # code -> (kt, source)  —— 仅当 worldsteel 表无2024值时生效
    "PRK": (350.0, "BGS 2024 est (worldsteel表只到2012)"),
    "DOM": (60.0, "BGS 2024 est"),
    "JOR": (300.0, "BGS 2024 est"),
    "TUN": (60.0, "BGS 2024"),
    "CUB": (178.7, "BGS 2024"),
    "ECU": (492.6, "BGS 2024"),
    "VEN": (28.8, "BGS 2024"),
    "AZE": (352.406, "BGS 2024"),
    "MMR": (500.0, "BGS 2024 est"),
    "LKA": (30.0, "BGS 2024 est"),
    "SYR": (5.0, "BGS 2021 est (2022+无)"),
    "COD": (30.0, "BGS 2024 est"),
    "UGA": (30.0, "BGS 2024 est"),
    "GHA": (245.0, "BGS 2024"),
    "AGO": (285.0, "BGS 2024"),
    "ZWE": (60.0, "BGS 2024 est"),
    "GTM": (249.5, "BGS 2024"),
}

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
BGS_ISO = {
    "Azerbaijan": "AZE", "Angola": "AGO", "Congo, Democratic Republic": "COD", "Ghana": "GHA",
    "Mauritania": "MRT", "Tunisia": "TUN", "Uganda": "UGA", "Zimbabwe": "ZWE", "Cuba": "CUB",
    "Dominican Republic": "DOM", "El Salvador": "SLV", "Guatemala": "GTM", "Ecuador": "ECU",
    "Paraguay": "PRY", "Uruguay": "URY", "Venezuela": "VEN", "Israel": "ISR", "Jordan": "JOR",
    "Mongolia": "MNG", "Myanmar": "MMR", "Singapore": "SGP", "Sri Lanka": "LKA", "Syria": "SYR",
    "Korea, Dem. P.R. of": "PRK", "New Zealand": "NZL", "Bosnia Herzegovina": "BIH",
    "Croatia": "HRV", "Moldova (a)": "MDA", "Montenegro": "MNE", "North Macedonia": "MKD",
    "Norway": "NOR", "Slovenia": "SVN", "Iran (b)": "IRN", "Bulgaria": "BGR", "Belarus": "BLR",
}

# ---------- 中国基准 ----------
pop = pd.read_csv(os.path.join(DATA, "pop_panel.csv"))
pop = pop[pop["is_country"]].copy()
chn_pop = pop[pop["code"] == "CHN"].iloc[0]
base = {}
for y in (1990, 2000, 2012):
    p = float(chn_pop[f"pop{y}"])
    base[y] = {"pop": p,
               "pc_steel_kg": CHN_TOTAL["steel_Mt"][y] * 1e9 / p,
               "pc_elec_kwh": CHN_TOTAL["elec_TWh"][y] * 1e9 / p}
print("=== 中国基准 ===")
for y, b in base.items():
    print(f"{y}: pop={b['pop']:,.0f}  人均钢={b['pc_steel_kg']:.2f}kg  人均电={b['pc_elec_kwh']:.1f}kWh")

# ---------- 各国钢铁（kt）+ 来源 ----------
steel = pd.read_csv(os.path.join(DATA, "steel_countries.csv"))
steel = steel[~steel["name"].str.contains("Other", na=False)].copy()
steel["code"] = steel["name"].map(STEEL_ISO)
assert steel["code"].notna().all()
ws = {}
for _, r in steel.iterrows():
    if pd.notna(r["2024"]):
        ws[r["code"]] = (float(r["2024"]) * 1000.0, "worldsteel2024")

bgs = pd.read_csv(os.path.join(DATA, "bgs_crude_steel.csv"))
bgs["code"] = bgs["name"].str.strip().map(BGS_ISO)
bgsmap = {}
for _, r in bgs.iterrows():
    if pd.isna(r["code"]):
        continue
    v = r["2024"] if pd.notna(r["2024"]) else (r["2021"] if (r["name"].strip() == "Syria") else None)
    if v is not None and pd.notna(v):
        bgsmap[r["code"]] = (float(v) / 1000.0, f"BGS2024{' est' if r['est2024'] else ''}")

steel_final = {}
for code in pop["code"]:
    if code in ws:
        steel_final[code] = ws[code]
    elif code in FIX_STEEL:
        steel_final[code] = FIX_STEEL[code]
    elif code in bgsmap:
        steel_final[code] = bgsmap[code]
    else:
        steel_final[code] = (0.0, "无产量(两源均无)")

# ---------- 电力 ----------
ele = pd.read_csv(ELEC).rename(columns={"Entity": "entity", "Code": "code", "Year": "year",
                                        "Total electricity": "elec"})
ele24 = ele[ele["year"] == YEAR][["code", "elec"]].dropna().set_index("code")["elec"].to_dict()
elec_final = {}
for code in pop["code"]:
    if code == "UKR":
        elec_final[code] = (96.9, "EIA2024")
    elif code in ele24:
        elec_final[code] = (float(ele24[code]), "OWID2024")
    else:
        elec_final[code] = (float("nan"), "缺")

# ---------- 计算 ----------
rows = []
for _, r in pop.iterrows():
    code = r["code"]
    popv = float(r["pop2024"])
    if popv < 10_000_000:
        continue
    st_kt, st_src = steel_final[code]
    el_twh, el_src = elec_final[code]
    pc_s = st_kt * 1e6 / popv              # kg (1 kt = 1e6 kg)
    pc_e = el_twh * 1e9 / popv             # kWh
    sc = {}
    for y in (1990, 2000, 2012):
        rs = pc_s / base[y]["pc_steel_kg"]
        re_ = pc_e / base[y]["pc_elec_kwh"]
        sc[y] = (rs, re_, rs + re_)
    rows.append({"entity": r["entity"], "code": code, "pop2024": popv,
                 "steel_kt": st_kt, "steel_src": st_src, "elec_twh": el_twh, "elec_src": el_src,
                 "pc_steel_kg": pc_s, "pc_elec_kwh": pc_e,
                 "score2012": sc[2012][2], "score2000": sc[2000][2], "score1990": sc[1990][2],
                 "r_s2012": sc[2012][0], "r_s2000": sc[2000][0], "r_s1990": sc[1990][0],
                 "r_e2012": sc[2012][1], "r_e2000": sc[2000][1], "r_e1990": sc[1990][1]})
df = pd.DataFrame(rows)

IMF = {"AUS", "AUT", "BEL", "CAN", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HKG",
       "ISL", "IRL", "ISR", "ITA", "JPN", "KOR", "LVA", "LTU", "LUX", "MAC", "MLT", "NLD", "NZL",
       "NOR", "PRT", "PRI", "SMR", "SGP", "SVK", "SVN", "ESP", "SWE", "CHE", "TWN", "GBR", "USA"}


def classify(row):
    if row["code"] in ("CHN", "TWN"):
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
df = df.sort_values("pop2024", ascending=False)
df.to_csv(os.path.join(DATA, "final.csv"), index=False, encoding="utf-8-sig")

print(f"\n国家数(≥1000万)={len(df)}  人口合计={df['pop2024'].sum():,.0f}")
print("\n=== 分类汇总 ===")
g = df.groupby("category").agg(n=("code", "size"), pop=("pop2024", "sum"))
print(g.sort_values("pop", ascending=False).to_string())
print("\n电力缺失:", df[df["elec_twh"].isna()]["entity"].tolist())
print("钢铁来源分布:", df["steel_src"].value_counts().to_dict())
print("\n=== 翻转/临界国家 ===")
for _, r in df[df["code"].isin(["DOM", "JOR", "TUN", "CUB", "ECU", "TJK", "VEN", "AZE", "PRK", "UKR"])].iterrows():
    print(f"{r['entity']:<20} score2000={r['score2000']:.3f} score1990={r['score1990']:.3f} "
          f"钢={r['steel_kt']:.1f}kt({r['steel_src']}) 电={r['elec_twh']:.1f}TWh -> {r['category']}")
