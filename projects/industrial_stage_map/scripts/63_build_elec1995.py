# -*- coding: utf-8 -*-
"""1995年人均发电量数据：EIA《International Energy Annual 2005》Table 6.3
（World Total Net Electricity Generation 1980-2005，十亿kWh）→ data/elec_1995_eia.csv。
并与 OWID(EI/Ember) 1995 年数据对比，检查两源一致性。"""
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
RAW = os.path.join(BASE, "raw")
XLS = os.path.join(RAW, "iea2005", "table63.xls")
OUT = os.path.join(DATA, "elec_1995_eia.csv")

# EIA 国名 -> ISO3（只列本项目96实体所需；EIA 用 FIPS 码，此处按国名映射更稳）
EIA_NAME2ISO = {
    "India": "IND", "China": "CHN", "United States": "USA", "Indonesia": "IDN",
    "Pakistan": "PAK", "Nigeria": "NGA", "Brazil": "BRA", "Bangladesh": "BGD",
    "Russia": "RUS", "Ethiopia": "ETH", "Mexico": "MEX", "Japan": "JPN", "Egypt": "EGY",
    "Philippines": "PHL", "Congo (Kinshasa)": "COD", "Vietnam": "VNM", "Iran": "IRN",
    "Turkey": "TUR", "Germany": "DEU", "Thailand": "THA", "United Kingdom": "GBR",
    "Tanzania": "TZA", "France": "FRA", "South Africa": "ZAF", "Italy": "ITA",
    "Kenya": "KEN", "Burma": "MMR", "Colombia": "COL", "Korea, South": "KOR",
    "Sudan": "SDN", "Uganda": "UGA", "Spain": "ESP", "Algeria": "DZA", "Iraq": "IRQ",
    "Argentina": "ARG", "Afghanistan": "AFG", "Yemen": "YEM", "Canada": "CAN",
    "Poland": "POL", "Morocco": "MAR", "Angola": "AGO", "Ukraine": "UKR",
    "Uzbekistan": "UZB", "Malaysia": "MYS", "Mozambique": "MOZ", "Ghana": "GHA",
    "Peru": "PER", "Saudi Arabia": "SAU", "Madagascar": "MDG",
    "Cote d'Ivoire (IvoryCoast)": "CIV", "Nepal": "NPL", "Cameroon": "CMR",
    "Venezuela": "VEN", "Niger": "NER", "Australia": "AUS", "Korea, North": "PRK",
    "Syria": "SYR", "Mali": "MLI", "Burkina Faso": "BFA", "Taiwan": "TWN",
    "Sri Lanka": "LKA", "Malawi": "MWI", "Zambia": "ZMB", "Kazakhstan": "KAZ",
    "Chad": "TCD", "Chile": "CHI_", "Romania": "ROU", "Somalia": "SOM", "Senegal": "SEN",
    "Guatemala": "GTM", "Netherlands": "NLD", "Ecuador": "ECU", "Cambodia": "KHM",
    "Zimbabwe": "ZWE", "Guinea": "GIN", "Benin": "BEN", "Rwanda": "RWA",
    "Burundi": "BDI", "Bolivia": "BOL", "Tunisia": "TUN", "Haiti": "HTI",
    "Belgium": "BEL", "Jordan": "JOR", "Dominican Republic": "DOM",
    "United Arab Emirates": "ARE", "Cuba": "CUB", "Honduras": "HND",
    "Czech Republic": "CZE", "Sweden": "SWE", "Tajikistan": "TJK",
    "Papua New Guinea": "PNG", "Portugal": "PRT", "Azerbaijan": "AZE",
    "Greece": "GRC", "Israel": "ISR",
}
EIA_NAME2ISO["Chile"] = "CHL"

d = pd.read_excel(XLS, header=None)
body = d.iloc[12:]  # 前12行为标题块
hdr = d.iloc[11].tolist()
year_cols = {}
for ci, h in enumerate(hdr):
    if isinstance(h, (int, float)) and not pd.isna(h) and 1980 <= int(h) <= 2005:
        year_cols[int(h)] = ci
print("年份列:", sorted(year_cols))

recs = {}
for _, r in body.iterrows():
    nm = r[1]
    if not isinstance(nm, str):
        continue
    nm = nm.strip()
    iso = EIA_NAME2ISO.get(nm)
    if not iso:
        continue
    vals = {}
    for y, ci in year_cols.items():
        v = r[ci]
        vals[y] = float(v) if isinstance(v, (int, float)) and not pd.isna(v) else None
    recs[iso] = {"eia_name": nm, **{f"eia_{y}": vals[y] for y in year_cols}}

df = pd.DataFrame.from_dict(recs, orient="index").reset_index().rename(columns={"index": "code"})
df.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"\n写入 {OUT}  国家数={len(df)}")

v2 = pd.read_csv(os.path.join(DATA, "final_v2.csv"))
need = set(v2["code"])
have = set(df["code"])
print("所需96实体中缺EIA数据:", sorted(need - have) or "无")
print("多余映射(不在96内):", sorted(have - need) or "无")

# ---- 与 OWID 对比 ----
ele = pd.read_csv(os.path.join(RAW, "owid_elec_gen.csv"))
e95 = ele[(ele["year"] == 1995) & (ele["code"].notna())].set_index("code")["total_generation__twh"]
cmp_rows = []
for _, r in df.iterrows():
    c = r["code"]
    if c in e95.index:
        eia = r["eia_1995"]
        owid = float(e95[c])
        cmp_rows.append({"code": c, "eia1995": eia, "owid1995": owid,
                         "ratio_owid_eia": owid / eia if eia else None})
cmpdf = pd.DataFrame(cmp_rows)
print(f"\n=== EIA vs OWID 1995 重合国家数={len(cmpdf)} ===")
print(cmpdf.sort_values("ratio_owid_eia").to_string(index=False))
print("\n比值统计: 中位数=%.3f  均值=%.3f  (min=%.3f max=%.3f)" %
      (cmpdf["ratio_owid_eia"].median(), cmpdf["ratio_owid_eia"].mean(),
       cmpdf["ratio_owid_eia"].min(), cmpdf["ratio_owid_eia"].max()))
