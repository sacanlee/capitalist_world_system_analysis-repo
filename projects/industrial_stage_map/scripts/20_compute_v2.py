# -*- coding: utf-8 -*-
"""V2计算：新六档标准（成熟/中后期/中期/起步/准备）+ 发达国家→后工业化国家 + 以色列列入。
记分 score(stage) = 人均发电量/标准发电量 + 人均钢产量/标准钢产量，score > 2 视为达到该阶段。
从原始源数据重算（人口/电力/钢铁），输出 data/final_v2.csv。"""
import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
ELEC = os.path.join(BASE, "..", "productivity_compare", "raw", "owid_electricity.csv")
YEAR = 2024

# 阶段标准（人均发电量 kWh / 人均钢产量 kg），由高到低
STANDARDS = [
    ("成熟工业化国家", 4000.0, 400.0),
    ("工业化中后期国家", 3000.0, 300.0),
    ("工业化中期国家", 1000.0, 100.0),
    ("工业化起步国家", 500.0, 50.0),
]
PREPARE = "准备工业化国家"

FIX_ELEC = {"UKR": (96.9, "EIA 2024 (OWID/Ember 只到2022)")}
FIX_STEEL = {
    "PRK": (350.0, "BGS 2024 est (worldsteel表只到2012)"),
    "DOM": (60.0, "BGS 2024 est"), "JOR": (300.0, "BGS 2024 est"),
    "TUN": (60.0, "BGS 2024"), "CUB": (178.7, "BGS 2024"),
    "ECU": (492.6, "BGS 2024"), "VEN": (28.8, "BGS 2024"),
    "AZE": (352.406, "BGS 2024"), "MMR": (500.0, "BGS 2024 est"),
    "LKA": (30.0, "BGS 2024 est"), "SYR": (5.0, "BGS 2021 est (2022+无)"),
    "COD": (30.0, "BGS 2024 est"), "UGA": (30.0, "BGS 2024 est"),
    "GHA": (245.0, "BGS 2024"), "AGO": (285.0, "BGS 2024"),
    "ZWE": (60.0, "BGS 2024 est"), "GTM": (249.5, "BGS 2024"),
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

IMF = {"AUS", "AUT", "BEL", "CAN", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HKG",
       "ISL", "IRL", "ISR", "ITA", "JPN", "KOR", "LVA", "LTU", "LUX", "MAC", "MLT", "NLD", "NZL",
       "NOR", "PRT", "PRI", "SMR", "SGP", "SVK", "SVN", "ESP", "SWE", "CHE", "TWN", "GBR", "USA"}
# 以色列UN WPP2024人口938.7万（<1000万），但按用户要求列入；以色列中央统计局口径已超1000万
FORCE_INCLUDE = {"ISR"}

# ---------- 人口 ----------
pop = pd.read_csv(os.path.join(DATA, "pop_panel.csv"))
pop = pop[pop["is_country"]].copy()

# ---------- 钢铁（kt） ----------
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
    if popv < 10_000_000 and code not in FORCE_INCLUDE:
        continue
    st_kt, st_src = steel_final[code]
    el_twh, el_src = elec_final[code]
    pc_s = st_kt * 1e6 / popv              # kg
    pc_e = el_twh * 1e9 / popv             # kWh
    sc = {}
    for name, se, ss in STANDARDS:
        sc[name] = pc_e / se + pc_s / ss
    rows.append({"entity": r["entity"], "code": code, "pop2024": popv,
                 "steel_kt": st_kt, "steel_src": st_src, "elec_twh": el_twh, "elec_src": el_src,
                 "pc_steel_kg": pc_s, "pc_elec_kwh": pc_e,
                 "s_mature": sc["成熟工业化国家"], "s_late": sc["工业化中后期国家"],
                 "s_mid": sc["工业化中期国家"], "s_start": sc["工业化起步国家"]})
df = pd.DataFrame(rows)


SCORE_KEYS = ["s_mature", "s_late", "s_mid", "s_start"]
STAGE_OF = {"s_mature": "成熟工业化国家", "s_late": "工业化中后期国家",
            "s_mid": "工业化中期国家", "s_start": "工业化起步国家"}


def classify(row):
    # 中国按记分归入成熟工业化国家；台湾在IMF发达经济体名单内，归后工业化国家（2026-09-23 用户更正）
    if row["code"] in IMF:
        return "后工业化国家"
    for k in SCORE_KEYS:
        if row[k] > 2:
            return STAGE_OF[k]
    return PREPARE


df["category"] = df.apply(classify, axis=1)
df = df.sort_values("pop2024", ascending=False)
df.to_csv(os.path.join(DATA, "final_v2.csv"), index=False, encoding="utf-8-sig")

print(f"国家数={len(df)}  人口合计={df['pop2024'].sum():,.0f}")
print("\n=== 分类汇总 ===")
g = df.groupby("category").agg(n=("code", "size"), pop=("pop2024", "sum"))
print(g.sort_values("pop", ascending=False).to_string())
print("\n电力缺失:", df[df["elec_twh"].isna()]["entity"].tolist())
print("\n=== 各档国家名单 ===")
for name in ["后工业化国家", "中国", "成熟工业化国家", "工业化中后期国家", "工业化中期国家",
             "工业化起步国家", "准备工业化国家"]:
    sub = df[df["category"] == name]
    print(f"\n[{name}] {len(sub)}国  {sub['pop2024'].sum()/1e8:.2f}亿")
    print("  " + "、".join(f"{r['entity']}({r['s_mature']:.2f}/{r['s_late']:.2f}/{r['s_mid']:.2f}/{r['s_start']:.2f})"
                          for _, r in sub.iterrows()))
print("\n=== 临界国家（某档得分1.8~2.2）===")
for _, r in df.iterrows():
    for k, lbl in [("s_mature", "成熟"), ("s_late", "中后期"), ("s_mid", "中期"), ("s_start", "起步")]:
        if 1.8 < r[k] < 2.2:
            print(f"{r['entity']:<16} {lbl}档得分={r[k]:.3f} -> {r['category']}")
