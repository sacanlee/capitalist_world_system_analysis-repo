# -*- coding: utf-8 -*-
"""2010年结果独立复核：不复用 73_compute_2010.py 的中间变量，
直接从 SSY2012 解析表（按英文名独立映射）+ OWID 电力 + UN人口 重算，逐国比对 data/final_2010.csv。
另核对：IMF发达经济体是否全部落在后工业化国家档。"""
import csv
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
RAW = os.path.join(BASE, "raw")

NAME2ISO = {"Russia": "RUS", "Ukraine": "UKR", "Saudi Arabia": "SAU",
            "United Arab Emirates": "ARE", "China": "CHN", "Turkey": "TUR",
            "South Africa": "ZAF", "Poland": "POL", "Malaysia": "MYS", "Kazakhstan": "KAZ",
            "Brazil": "BRA", "Mexico": "MEX", "Egypt": "EGY", "Iran": "IRN", "Thailand": "THA",
            "Argentina": "ARG", "Venezuela": "VEN", "Uzbekistan": "UZB", "Syria": "SYR",
            "Romania": "ROU", "Chile": "CHL", "Azerbaijan": "AZE", "Tajikistan": "TJK",
            "Jordan": "JOR", "India": "IND", "Viet Nam": "VNM", "Colombia": "COL",
            "Algeria": "DZA", "Iraq": "IRQ", "Peru": "PER", "DPR Korea (e)": "PRK",
            "Ecuador": "ECU", "Cuba": "CUB", "Tunisia": "TUN", "Dominican Republic": "DOM",
            "Indonesia": "IDN", "Pakistan": "PAK", "Nigeria": "NGA", "Bangladesh": "BGD",
            "Philippines": "PHL", "Ethiopia": "ETH", "Zaire": "COD", "Myanmar": "MMR",
            "Kenya": "KEN", "Morocco": "MAR", "Uganda": "UGA", "Nepal": "NPL", "Yemen": "YEM",
            "Ghana": "GHA", "Angola": "AGO", "Mozambique": "MOZ", "Cote d'Ivoire": "CIV",
            "Madagascar": "MDG", "Sri Lanka": "LKA", "Cameroon": "CMR", "Niger": "NER",
            "Burkina Faso": "BFA", "Mali": "MLI", "Malawi": "MWI", "Cambodia": "KHM",
            "Guatemala": "GTM", "Zambia": "ZMB", "Zimbabwe": "ZWE", "Senegal": "SEN",
            "Chad": "TCD", "Somalia": "SOM", "Guinea": "GIN", "Rwanda": "RWA",
            "Bolivia": "BOL", "Haiti": "HTI", "Benin": "BEN", "Burundi": "BDI",
            "Honduras": "HND", "Papua New Guinea": "PNG", "Japan": "JPN", "Germany": "DEU",
            "United States": "USA", "Italy": "ITA", "South Korea": "KOR", "Spain": "ESP",
            "Canada": "CAN", "Taiwan, China": "TWN", "Australia": "AUS", "Netherlands": "NLD",
            "Belgium": "BEL", "Portugal": "PRT", "Czech Republic": "CZE", "Sweden": "SWE",
            "Israel": "ISR", "France": "FRA", "United Kingdom": "GBR", "Greece": "GRC",
            "Egypt ": "EGY"}
steel = {}
with open(os.path.join(DATA, "steel_2010_raw.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        nm = r["name"].strip()
        if nm in NAME2ISO:
            v = r["2010"]
            steel[NAME2ISO[nm]] = float(v) if v not in ("", "nan") else 0.0

ele = pd.read_csv(os.path.join(RAW, "owid_elec_gen.csv"))
e10 = ele[(ele["year"] == 2010) & (ele["code"].notna())].set_index("code")["total_generation__twh"]

popdf = pd.read_csv(os.path.join(RAW, "owid_pop_lr.csv"))
pop10 = {r["Code"]: float(r["Population"]) for _, r in popdf.iterrows()
         if r["Year"] == 2010 and isinstance(r["Code"], str) and pd.notna(r["Population"])}

IMF = {"AUS", "AUT", "BEL", "CAN", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC",
       "HKG", "ISL", "IRL", "ISR", "ITA", "JPN", "KOR", "LVA", "LTU", "LUX", "MAC", "MLT",
       "NLD", "NZL", "NOR", "PRT", "PRI", "SMR", "SGP", "SVK", "SVN", "ESP", "SWE", "CHE",
       "TWN", "GBR", "USA"}
STD = [("成熟工业化国家", 4000.0, 400.0), ("工业化中后期国家", 3000.0, 300.0),
       ("工业化中期国家", 1000.0, 100.0), ("工业化起步国家", 500.0, 50.0)]

with open(os.path.join(DATA, "final_2010.csv"), encoding="utf-8-sig") as f:
    final = {r["code"]: r for r in csv.DictReader(f)}

errs, checked = [], 0
for code, r in final.items():
    p = pop10[code]
    e = 0.0 if code == "SSD" else (float(e10[code]) if code in e10.index else None)
    s = steel.get(code, 0.0)
    if e is None:
        errs.append(f"{code}: 复核无电力数据")
        continue
    pc_e, pc_s = e * 1e9 / p, s * 1e6 / p
    if code in IMF:
        cat = "后工业化国家"
    else:
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
    if abs(float(r["pop2010"]) - p) > 1:
        errs.append(f"{code}: 人口不一致")

print(f"复核国家数={checked}  错误数={len(errs)}")
for e in errs:
    print("  !", e)

imf_in = sorted(c for c in final if c in IMF)
bad = [c for c in imf_in if final[c]["category"] != "后工业化国家"]
print(f"\nIMF发达经济体在本名单内={len(imf_in)}国：{imf_in}")
print("未落入后工业化国家档:", bad or "无")
non_imf_post = [c for c in final if final[c]["category"] == "后工业化国家" and c not in IMF]
print("非IMF却列为后工业化:", non_imf_post or "无")

# 参考：若纯按记分（不设发达国家默认档）这些国家会落到哪一档
flips = []
for code in imf_in:
    r = final[code]
    sc = {"成熟工业化国家": float(r["s_mature"]), "工业化中后期国家": float(r["s_late"]),
          "工业化中期国家": float(r["s_mid"]), "工业化起步国家": float(r["s_start"])}
    cat = "准备工业化国家"
    for n, _, _ in STD:
        if sc[n] >= 2:
            cat = n
            break
    if cat != "后工业化国家":
        flips.append((code, cat, round(sc["成熟工业化国家"], 2)))
print(f"\n参考：18个后工业化国家中，若纯按记分应归入其他档的有 {len(flips)} 国")
for c, cat, sm in flips:
    print(f"  {c}: 记分档={cat}（成熟档得分{sm}）")
