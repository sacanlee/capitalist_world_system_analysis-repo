# -*- coding: utf-8 -*-
"""1995年结果独立复核：不复用 65_compute_1995.py 的任何映射/中间文件，
直接从 EIA xls（按 FIPS 码定位）+ SSY2003 解析表 + UN人口 重算，逐国比对 data/final_1995.csv。
另做敏感性：把 OWID(毛发电量) 替换 EIA(净发电量)，看有多少国家跨档。"""
import csv
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
RAW = os.path.join(BASE, "raw")

# ---- 独立的 FIPS -> ISO3 映射（EIA 表用 FIPS 码，与 63/65 的按国名映射相互独立）----
FIPS = {
    "IN": "IND", "CH": "CHN", "US": "USA", "ID": "IDN", "PK": "PAK", "NI": "NGA",
    "BR": "BRA", "BG": "BGD", "RS": "RUS", "ET": "ETH", "MX": "MEX", "JA": "JPN",
    "EG": "EGY", "RP": "PHL", "CG": "COD", "VM": "VNM", "IR": "IRN", "TU": "TUR",
    "GM": "DEU", "TH": "THA", "UK": "GBR", "TZ": "TZA", "FR": "FRA", "SF": "ZAF",
    "IT": "ITA", "KE": "KEN", "BM": "MMR", "CO": "COL", "KS": "KOR", "SU": "SDN",
    "UG": "UGA", "SP": "ESP", "AG": "DZA", "IZ": "IRQ", "AR": "ARG", "AF": "AFG",
    "YM": "YEM", "CA": "CAN", "PL": "POL", "MO": "MAR", "AO": "AGO", "UP": "UKR",
    "UZ": "UZB", "MY": "MYS", "MZ": "MOZ", "GH": "GHA", "PE": "PER", "SA": "SAU",
    "MA": "MDG", "IV": "CIV", "NP": "NPL", "CM": "CMR", "VE": "VEN", "NG": "NER",
    "AS": "AUS", "KN": "PRK", "SY": "SYR", "ML": "MLI", "UV": "BFA", "TW": "TWN",
    "CE": "LKA", "MI": "MWI", "ZA": "ZMB", "KZ": "KAZ", "CD": "TCD", "CI": "CHL",
    "RO": "ROU", "SO": "SOM", "SG": "SEN", "GT": "GTM", "NL": "NLD", "EC": "ECU",
    "CB": "KHM", "ZI": "ZWE", "GV": "GIN", "BN": "BEN", "RW": "RWA", "BY": "BDI",
    "BL": "BOL", "TS": "TUN", "HA": "HTI", "BE": "BEL", "JO": "JOR", "DR": "DOM",
    "TC": "ARE", "CU": "CUB", "HO": "HND", "EZ": "CZE", "SW": "SWE", "TI": "TJK",
    "PP": "PNG", "PO": "PRT", "AJ": "AZE", "GR": "GRC", "IS": "ISR",
}

# ---- 电力：直接从 xls 按 FIPS 定位 1995 列 ----
xl = pd.read_excel(os.path.join(RAW, "iea2005", "table63.xls"), header=None)
hdr_row = None
for i in range(len(xl)):
    vals = xl.iloc[i].tolist()
    if 1995 in [int(v) for v in vals if isinstance(v, (int, float)) and not pd.isna(v)]:
        hdr_row = i
        break
assert hdr_row is not None, "未找到表头行"
c95 = [j for j, v in enumerate(xl.iloc[hdr_row].tolist())
       if isinstance(v, (int, float)) and v == 1995][0]
elec95 = {}
for i in range(hdr_row + 1, len(xl)):
    f = xl.iloc[i, 2]
    if isinstance(f, str) and f.strip() in FIPS:
        v = xl.iloc[i, c95]
        elec95[FIPS[f.strip()]] = float(v) if isinstance(v, (int, float)) and not pd.isna(v) else None

# ---- 钢铁：直接用 SSY2003 解析表（按英文名独立映射）----
NAME2ISO = {"Japan": "JPN", "China": "CHN", "United States": "USA", "Russia": "RUS",
            "F.R. Germany": "DEU", "South Korea": "KOR", "Italy": "ITA", "Brazil": "BRA",
            "Ukraine": "UKR", "India": "IND", "France": "FRA", "United Kingdom": "GBR",
            "Canada": "CAN", "Spain": "ESP", "Turkey": "TUR", "Mexico": "MEX", "Poland": "POL",
            "Belgium": "BEL", "Chinese Taipei": "TWN", "South Africa": "ZAF", "Australia": "AUS",
            "Netherlands": "NLD", "Czech Republic": "CZE", "Romania": "ROU", "Sweden": "SWE",
            "Kazakhstan": "KAZ", "Argentina": "ARG", "Uzbekistan": "UZB", "Venezuela": "VEN",
            "Malaysia": "MYS", "Saudi Arabia": "SAU", "Chile": "CHL", "Thailand": "THA",
            "Iran": "IRN", "Egypt": "EGY", "Colombia": "COL", "Greece": "GRC", "Portugal": "PRT",
            "Peru": "PER", "Indonesia": "IDN", "Algeria": "DZA", "Pakistan": "PAK",
            "Philippines": "PHL", "Syria": "SYR", "Tunisia": "TUN", "Morocco": "MAR",
            "D.P.R. Korea (e)": "PRK", "Viet Nam": "VNM", "Zimbabwe": "ZWE", "Cuba": "CUB",
            "Jordan": "JOR", "Nigeria": "NGA", "Venezuela ": "VEN", "Azerbaijan": "AZE",
            "Bangladesh": "BGD", "Kenya": "KEN", "Ghana": "GHA", "Zambia": "ZMB",
            "Myanmar (e)": "MMR", "Ecuador": "ECU", "Tajikistan": "TJK", "Georgia": "GEO",
            "Israel": "ISR", "Qatar": "QAT", "United Arab Emirates": "ARE", "Zaire (e)": "COD",
            "Angola (e)": "AGO", "Uganda (e)": "UGA", "Mauritania": "MRT", "Libya": "LBY",
            "Sri Lanka (e)": "LKA", "Guatemala": "GTM", "Dominican Republic": "DOM",
            "El Salvador": "SLV", "Trinidad and Tobago": "TTO", "Paraguay": "PRY",
            "Uruguay": "URY", "Bolivia": "BOL", "Honduras": "HND"}
steel95 = {}
with open(os.path.join(DATA, "steel_1995_raw.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        nm = r["name"].strip()
        if nm in NAME2ISO:
            v = r["1995"]
            steel95[NAME2ISO[nm]] = float(v) if v not in ("", "nan") else 0.0

# ---- 人口（UN WPP2024 1995）----
popdf = pd.read_csv(os.path.join(RAW, "owid_pop_lr.csv"))
pop95 = {r["Code"]: float(r["Population"]) for _, r in popdf.iterrows()
         if r["Year"] == 1995 and isinstance(r["Code"], str) and pd.notna(r["Population"])}

# ---- 逐国重算比对 ----
STD = [("成熟工业化国家", 4000.0, 400.0), ("工业化中后期国家", 3000.0, 300.0),
       ("工业化中期国家", 1000.0, 100.0), ("工业化起步国家", 500.0, 50.0)]
with open(os.path.join(DATA, "final_1995.csv"), encoding="utf-8-sig") as f:
    final = {r["code"]: r for r in csv.DictReader(f)}

errs, checked = [], 0
for code, r in final.items():
    p = pop95[code]
    e = elec95.get(code)
    if code == "SSD":
        e = 0.0
    s = steel95.get(code, 0.0)
    if e is None:
        errs.append(f"{code}: 复核无电力数据")
        continue
    pc_e, pc_s = e * 1e9 / p, s * 1e6 / p
    cat = "准备工业化国家"
    for n, se, ss in STD:
        if pc_e / se + pc_s / ss >= 2:
            cat = n
            break
    checked += 1
    if cat != r["category"]:
        errs.append(f"{code}: 类别不一致 复核={cat} 文件={r['category']}")
    if abs(pc_e - float(r["pc_elec_kwh"])) > 0.01:
        errs.append(f"{code}: 人均电力不一致 {pc_e:.2f} vs {r['pc_elec_kwh']}")
    if abs(pc_s - float(r["pc_steel_kg"])) > 0.01:
        errs.append(f"{code}: 人均钢不一致 {pc_s:.2f} vs {r['pc_steel_kg']}")
    if abs(float(r["pop1995"]) - p) > 1:
        errs.append(f"{code}: 人口不一致")

print(f"复核国家数={checked}  错误数={len(errs)}")
for e in errs:
    print("  !", e)

# ---- 敏感性：OWID(毛)替代 EIA(净) ----
ele = pd.read_csv(os.path.join(RAW, "owid_elec_gen.csv"))
o95 = ele[(ele["year"] == 1995) & (ele["code"].notna())].set_index("code")["total_generation__twh"]
flips = []
for code, r in final.items():
    if code not in o95.index:
        continue
    p, s = pop95[code], steel95.get(code, 0.0)
    pc_e, pc_s = float(o95[code]) * 1e9 / p, s * 1e6 / p
    cat = "准备工业化国家"
    for n, se, ss in STD:
        if pc_e / se + pc_s / ss >= 2:
            cat = n
            break
    if cat != r["category"]:
        flips.append((code, r["category"], cat))
print(f"\n敏感性(OWID毛发电量, 重合{len(set(final)&set(o95.index))}国): 跨档 {len(flips)} 国")
for c, a, b in flips:
    print(f"  {c}: EIA净->{a}  OWID毛->{b}")
