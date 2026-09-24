# -*- coding: utf-8 -*-
"""1995年分类计算（用户2026-09-24规格）：
score = 人均年发电量/标准发电量 + 人均年钢产量/标准钢产量
  成熟 4000/400；中后期 3000/300；中期 1000/100；起步 500/50；均未达 >=2 → 准备工业化国家。
不划发达国家档（无后工业化国家），全部按记分归类。
数据：人口 UN WPP2024(1995)；发电量 EIA IEA2005 Table 6.3（净发电量，1995）；
      粗钢 worldsteel SSY2003（1995，未列入者=0）。
输出 data/final_1995.csv（列结构与 final_v2.csv 一致）。
"""
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
RAW = os.path.join(BASE, "raw")
YEAR = 1995

STANDARDS = [
    ("成熟工业化国家", 4000.0, 400.0),
    ("工业化中后期国家", 3000.0, 300.0),
    ("工业化中期国家", 1000.0, 100.0),
    ("工业化起步国家", 500.0, 50.0),
]
PREPARE = "准备工业化国家"

# ---------- 实体名单（与2024年V2图一致的96实体） ----------
v2 = pd.read_csv(os.path.join(DATA, "final_v2.csv"))
name = dict(zip(v2["code"], v2["entity"]))
codes = list(v2["code"])

# ---------- 人口（UN WPP2024 历史值） ----------
pop = pd.read_csv(os.path.join(RAW, "owid_pop_lr.csv"))
p95s = pop[(pop["Year"] == YEAR) & (pop["Code"].notna())]
p95 = {r["Code"]: float(r["Population"]) for _, r in p95s.iterrows()
       if pd.notna(r["Population"])}
world95 = float(p95s[p95s["Code"] == "OWID_WRL"]["Population"].iloc[0])
missing_pop = [c for c in codes if c not in p95]
assert not missing_pop, f"缺{YEAR}人口: {missing_pop}"

# ---------- 电力（EIA 净发电量，TWh） ----------
ele = pd.read_csv(os.path.join(DATA, "elec_1995_eia.csv")).set_index("code")
elec = {}
for c in codes:
    if c in ele.index:
        elec[c] = (float(ele.loc[c, "eia_1995"]), "EIA-IEA2005")
# 南苏丹1995年尚未独立（2011年独立），其电力计入苏丹
SPECIAL_ELEC = {"SSD": (0.0, "1995年尚未独立，计入苏丹")}
for c, v in SPECIAL_ELEC.items():
    elec[c] = v
assert set(elec) == set(codes), f"缺电力: {set(codes) - set(elec)}"

# ---------- 钢铁（worldsteel SSY2003，kt） ----------
st = pd.read_csv(os.path.join(DATA, "steel_1995.csv"))
steel = {}
for _, r in st.iterrows():
    v = r["steel_kt_1995"]
    if pd.notna(v):
        steel[r["code"]] = (float(v), "worldsteel-SSY2003")
# SSY2003 中 1995 为空格的2国：USGS《Minerals Yearbook 1995》Vol.3 表11 记为
# 多米尼加 "--"(无产出)、危地马拉 "NA"(未报告)，按 0 计
FIX_STEEL = {"DOM": (0.0, "SSY空/USGS-MYB1995:--"), "GTM": (0.0, "SSY空/USGS-MYB1995:NA")}
for c, v in FIX_STEEL.items():
    steel[c] = v
for c in codes:
    if c not in steel:
        steel[c] = (0.0, "无产量(SSY2003未列)")

# ---------- 计算与归类 ----------
rows = []
for c in codes:
    popv = p95[c]
    st_kt, st_src = steel[c]
    el_twh, el_src = elec[c]
    pc_s = st_kt * 1e6 / popv
    pc_e = el_twh * 1e9 / popv
    sc = {n: pc_e / se + pc_s / ss for n, se, ss in STANDARDS}
    cat = PREPARE
    for n, _, _ in STANDARDS:
        if sc[n] >= 2:          # 用户规格为 >=2（2024年图为 >2；1995年无恰好等于2.0的国家，见核对输出）
            cat = n
            break
    rows.append({"entity": name[c], "code": c, "pop1995": popv,
                 "steel_kt": st_kt, "steel_src": st_src, "elec_twh": el_twh, "elec_src": el_src,
                 "pc_steel_kg": pc_s, "pc_elec_kwh": pc_e,
                 "s_mature": sc["成熟工业化国家"], "s_late": sc["工业化中后期国家"],
                 "s_mid": sc["工业化中期国家"], "s_start": sc["工业化起步国家"],
                 "category": cat})
df = pd.DataFrame(rows).sort_values("pop1995", ascending=False)
df.to_csv(os.path.join(DATA, "final_1995.csv"), index=False, encoding="utf-8-sig")

print(f"实体数={len(df)}  全球{YEAR}人口={world95:,.0f}  分类实体人口={df['pop1995'].sum():,.0f}")
print("\n=== 分类汇总 ===")
ORDER = ["成熟工业化国家", "工业化中后期国家", "工业化中期国家", "工业化起步国家", PREPARE]
for c in ORDER:
    sub = df[df["category"] == c]
    print(f"{c:<10} {len(sub):>3}国  {sub['pop1995'].sum()/1e8:>7.2f}亿  "
          f"{sub['pop1995'].sum()/world95*100:>5.2f}%")
rest = world95 - df["pop1995"].sum()
print(f"{'其他<1000万':<10}   -国  {rest/1e8:>7.2f}亿  {rest/world95*100:>5.2f}%")

print("\n=== 各档名单（含四档得分） ===")
for c in ORDER:
    sub = df[df["category"] == c]
    print(f"\n[{c}] {len(sub)}国  {sub['pop1995'].sum()/1e8:.2f}亿")
    print("  " + "、".join(
        f"{r['entity']}({r['s_mature']:.2f}/{r['s_late']:.2f}/{r['s_mid']:.2f}/{r['s_start']:.2f})"
        for _, r in sub.iterrows()))

print("\n=== 恰好等于2.000的国家（>=与>的判定差异） ===")
hit = df[(df[["s_mature", "s_late", "s_mid", "s_start"]].sub(2).abs() < 1e-9).any(axis=1)]
print("无" if hit.empty else hit[["entity", "s_mature", "s_late", "s_mid", "s_start"]].to_string(index=False))

print("\n=== 临界国家（某档得分1.8~2.2） ===")
for _, r in df.iterrows():
    for k, lbl in [("s_mature", "成熟"), ("s_late", "中后期"), ("s_mid", "中期"), ("s_start", "起步")]:
        if 1.8 < r[k] < 2.2:
            print(f"{r['entity']:<16} {lbl}档={r[k]:.3f} -> {r['category']}")
