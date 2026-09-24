# -*- coding: utf-8 -*-
"""2010年分类计算（用户2026-09-24规格，与2024年V2同法）：
1) 发达国家（IMF发达经济体口径）默认列为后工业化国家（以色列按此列入）；
2) 其余按记分 score = 人均发电量/标准发电量 + 人均钢产量/标准钢产量 >=2 归类：
   成熟 4000/400；中后期 3000/300；中期 1000/100；起步 500/50；均未达 → 准备工业化国家。
数据：人口 UN WPP2024(2010历史值)；发电量 OWID/Ember 2010（与2024年图同源）；
      粗钢 worldsteel《SSY2012》2010（未列入者按无产量计）。
输出 data/final_2010.csv（列结构与 final_v2.csv 一致）。
"""
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
RAW = os.path.join(BASE, "raw")
YEAR = 2010

STANDARDS = [
    ("成熟工业化国家", 4000.0, 400.0),
    ("工业化中后期国家", 3000.0, 300.0),
    ("工业化中期国家", 1000.0, 100.0),
    ("工业化起步国家", 500.0, 50.0),
]
PREPARE = "准备工业化国家"
POSTIND = "后工业化国家"

# IMF发达经济体（与2024年V2图完全一致的口径）
IMF = {"AUS", "AUT", "BEL", "CAN", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HKG",
       "ISL", "IRL", "ISR", "ITA", "JPN", "KOR", "LVA", "LTU", "LUX", "MAC", "MLT", "NLD", "NZL",
       "NOR", "PRT", "PRI", "SMR", "SGP", "SVK", "SVN", "ESP", "SWE", "CHE", "TWN", "GBR", "USA"}

v2 = pd.read_csv(os.path.join(DATA, "final_v2.csv"))
name = dict(zip(v2["code"], v2["entity"]))
codes = list(v2["code"])

# ---------- 人口 ----------
pop = pd.read_csv(os.path.join(RAW, "owid_pop_lr.csv"))
pY = pop[(pop["Year"] == YEAR) & (pop["Code"].notna())]
pmap = {r["Code"]: float(r["Population"]) for _, r in pY.iterrows() if pd.notna(r["Population"])}
worldY = float(pY[pY["Code"] == "OWID_WRL"]["Population"].iloc[0])
missing_pop = [c for c in codes if c not in pmap]
assert not missing_pop, f"缺{YEAR}人口: {missing_pop}"

# ---------- 电力（OWID/Ember 毛发电量，TWh） ----------
ele = pd.read_csv(os.path.join(RAW, "owid_elec_gen.csv"))
eY = ele[(ele["year"] == YEAR) & (ele["code"].notna())].set_index("code")["total_generation__twh"]
elec = {}
for c in codes:
    if c in eY.index and pd.notna(eY[c]):
        elec[c] = (float(eY[c]), "OWID-Ember2010")
# 南苏丹2011年独立，2010年其电力统计计入苏丹
for c, v in {"SSD": (0.0, "2010年尚未独立，计入苏丹")}.items():
    elec[c] = v
assert set(elec) == set(codes), f"缺电力: {set(codes) - set(elec)}"

# ---------- 钢铁（SSY2012，kt） ----------
st = pd.read_csv(os.path.join(DATA, "steel_2010.csv"))
steel = {r["code"]: (float(r["steel_kt_2010"]), "worldsteel-SSY2012")
         for _, r in st.iterrows() if pd.notna(r["steel_kt_2010"])}
for c in codes:
    if c not in steel:
        steel[c] = (0.0, "无产量(SSY2012未列)")

# ---------- 计算与归类 ----------
rows = []
for c in codes:
    popv = pmap[c]
    st_kt, st_src = steel[c]
    el_twh, el_src = elec[c]
    pc_s = st_kt * 1e6 / popv
    pc_e = el_twh * 1e9 / popv
    sc = {n: pc_e / se + pc_s / ss for n, se, ss in STANDARDS}
    if c in IMF:
        cat = POSTIND
    else:
        cat = PREPARE
        for n, _, _ in STANDARDS:
            if sc[n] >= 2:
                cat = n
                break
    rows.append({"entity": name[c], "code": c, "pop2010": popv,
                 "steel_kt": st_kt, "steel_src": st_src, "elec_twh": el_twh, "elec_src": el_src,
                 "pc_steel_kg": pc_s, "pc_elec_kwh": pc_e,
                 "s_mature": sc["成熟工业化国家"], "s_late": sc["工业化中后期国家"],
                 "s_mid": sc["工业化中期国家"], "s_start": sc["工业化起步国家"],
                 "category": cat})
df = pd.DataFrame(rows).sort_values("pop2010", ascending=False)
df.to_csv(os.path.join(DATA, "final_2010.csv"), index=False, encoding="utf-8-sig")

ORDER = [POSTIND, "成熟工业化国家", "工业化中后期国家", "工业化中期国家",
         "工业化起步国家", PREPARE]
print(f"实体数={len(df)}  全球{YEAR}人口={worldY:,.0f}  分类实体人口={df['pop2010'].sum():,.0f}")
print("\n=== 分类汇总 ===")
for c in ORDER:
    sub = df[df["category"] == c]
    print(f"{c:<10} {len(sub):>3}国  {sub['pop2010'].sum()/1e8:>7.2f}亿  "
          f"{sub['pop2010'].sum()/worldY*100:>5.2f}%")
rest = worldY - df["pop2010"].sum()
print(f"{'其他<1000万':<10}   -国  {rest/1e8:>7.2f}亿  {rest/worldY*100:>5.2f}%")

print("\n=== 各档名单（含四档得分） ===")
for c in ORDER:
    sub = df[df["category"] == c]
    print(f"\n[{c}] {len(sub)}国  {sub['pop2010'].sum()/1e8:.2f}亿")
    print("  " + "、".join(
        f"{r['entity']}({r['s_mature']:.2f}/{r['s_late']:.2f}/{r['s_mid']:.2f}/{r['s_start']:.2f})"
        for _, r in sub.iterrows()))

print("\n=== 各档得分恰好=2.000的国家（>=与>判定差异） ===")
hit = df[(df[["s_mature", "s_late", "s_mid", "s_start"]].sub(2).abs() < 1e-9).any(axis=1)]
print("无" if hit.empty else hit[["entity", "s_mature", "s_late", "s_mid", "s_start"]].to_string(index=False))

print("\n=== 临界国家（非后工业化档，某档得分1.8~2.2） ===")
for _, r in df.iterrows():
    if r["category"] == POSTIND:
        continue
    for k, lbl in [("s_mature", "成熟"), ("s_late", "中后期"), ("s_mid", "中期"), ("s_start", "起步")]:
        if 1.8 < r[k] < 2.2:
            print(f"{r['entity']:<16} {lbl}档={r[k]:.3f} -> {r['category']}")

print("\n=== 记分高于2但被归入后工业化国家的（发达国家默认档） ===")
hi = df[(df["category"] == POSTIND) & ((df[["s_mature"]].max(axis=1)) < 2)]
print("无" if hi.empty else
      "、".join(f"{r['entity']}(成熟档{r['s_mature']:.2f})" for _, r in hi.iterrows()))
