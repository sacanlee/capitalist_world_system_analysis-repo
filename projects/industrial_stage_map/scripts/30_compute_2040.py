# -*- coding: utf-8 -*-
"""2040年推演：以2024年V2分类为基础，按用户给定晋级名单调整部分国家阶段；
人口用联合国WPP2024中等生育率情景（raw/owid_pop_lr.csv 投影列）。
输出 data/final_2040.csv。"""
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
RAW = os.path.join(BASE, "raw")

# ---- 用户给定晋级名单（中文名 -> ISO）----
PROMOTE = {
    # 晋级发达国家（后工业化国家）——2026-09-23变更：仅中国与欧盟国家；
    # 台湾2024年即已列入（非本轮晋级）；俄/土/沙特/阿联酋/马来西亚保持成熟工业化国家
    "后工业化国家": [("中国", "CHN"), ("波兰", "POL"), ("保加利亚", "BGR"), ("匈牙利", "HUN")],
    # 晋级成熟工业国（墨西哥按用户答复归中后期，不在此列）
    "成熟工业化国家": [("伊朗", "IRN"), ("哈萨克斯坦", "KAZ"), ("巴西", "BRA"), ("智利", "CHL"),
                       ("乌克兰", "UKR"), ("罗马尼亚", "ROU"), ("越南", "VNM")],
    # 晋级工业化中后期国家（墨西哥按用户答复归此）
    "工业化中后期国家": [("墨西哥", "MEX"), ("南非", "ZAF"), ("泰国", "THA"), ("印度", "IND"),
                         ("伊拉克", "IRQ")],
    # 晋级工业化中期国家（乌兹别克斯坦2024年已是中期，为无变化项）
    "工业化中期国家": [("印度尼西亚", "IDN"), ("哥伦比亚", "COL"), ("摩洛哥", "MAR"),
                       ("突尼斯", "TUN"), ("乌兹别克斯坦", "UZB"), ("菲律宾", "PHL")],
    # 晋级工业化起步国家（博茨瓦纳/纳米比亚原人口不足1000万，按要求新增）
    "工业化起步国家": [("巴基斯坦", "PAK"), ("孟加拉国", "BGD"), ("柬埔寨", "KHM"), ("危地马拉", "GTM"),
                       ("赞比亚", "ZMB"), ("加纳", "GHA"), ("斯里兰卡", "LKA"), ("肯尼亚", "KEN"),
                       ("缅甸", "MMR"), ("科特迪瓦", "CIV"), ("几内亚", "GIN"), ("安哥拉", "AGO"),
                       ("博茨瓦纳", "BWA"), ("纳米比亚", "NAM"), ("津巴布韦", "ZWE"), ("卢旺达", "RWA"),
                       ("乌干达", "UGA"), ("尼日利亚", "NGA"), ("塞内加尔", "SEN"),
                       ("莫桑比克", "MOZ"), ("尼泊尔", "NPL"), ("坦桑尼亚", "TZA")],
}
# 人口不足1000万但按要求列入（保/匈为发达国家，博/纳为起步国家；塞尔维亚不再晋级发达，故不列入）
NEW_COUNTRIES = ["BGR", "HUN", "BWA", "NAM"]

promote_map = {}
for cat, lst in PROMOTE.items():
    for zh, code in lst:
        assert code not in promote_map, f"重复: {code}"
        promote_map[code] = cat

# ---- 2024年分类 ----
d24 = pd.read_csv(os.path.join(DATA, "final_v2.csv"))
cat24 = dict(zip(d24["code"], d24["category"]))
name24 = dict(zip(d24["code"], d24["entity"]))
need = set(cat24) | set(NEW_COUNTRIES)

# ---- 2040人口（UN WPP2024 中等情景）----
pop = pd.read_csv(os.path.join(RAW, "owid_pop_lr.csv"))
pop40 = pop[pop["Year"] == 2040]
p40 = {}
for _, r in pop40.iterrows():
    c = r["Code"]
    if isinstance(c, str) and c in need:
        v = r["Population (projections) (Projected)"]
        if pd.notna(v):
            p40[c] = float(v)
world40 = float(pop40[pop40["Code"] == "OWID_WRL"]["Population (projections) (Projected)"].iloc[0])

missing = need - set(p40)
assert not missing, f"缺2040人口: {missing}"

rows = []
for code in sorted(need, key=lambda c: -p40[c]):
    c24 = cat24.get(code, "其他人口不足1000万国家")
    c40 = promote_map.get(code, c24)
    if code in NEW_COUNTRIES and code in promote_map:
        c24 = "其他人口不足1000万国家"
    rows.append({"code": code, "entity": name24.get(code, code), "pop2040": p40[code],
                 "cat2024": c24, "cat2040": c40, "promoted": code in promote_map})
df = pd.DataFrame(rows)
df.to_csv(os.path.join(DATA, "final_2040.csv"), index=False, encoding="utf-8-sig")

ORDER = ["后工业化国家", "工业化成熟国家", "成熟工业化国家", "工业化中后期国家", "工业化中期国家",
         "工业化起步国家", "准备工业化国家"]
print(f"实体数={len(df)}  全球2040人口={world40:,.0f}  其中分类国家人口={df['pop2040'].sum():,.0f}")
print("\n=== 2040年分类汇总 ===")
g = df.groupby("cat2040").agg(n=("code", "size"), pop=("pop2040", "sum"))
g = g.sort_values("pop", ascending=False)
for c, r in g.iterrows():
    print(f"{c:<12} {int(r['n']):>3}国  {r['pop']/1e8:>6.2f}亿  {r['pop']/world40*100:>5.2f}%")
rest = world40 - df["pop2040"].sum()
print(f"{'其他<1000万':<12}   -国  {rest/1e8:>6.2f}亿  {rest/world40*100:>5.2f}%")

print("\n=== 晋级国家核对（2024 -> 2040）===")
for cat, lst in PROMOTE.items():
    print(f"\n[{cat}]")
    for zh, code in lst:
        r = df[df["code"] == code].iloc[0]
        flag = "" if r["cat2024"] != r["cat2040"] else "  ← 与2024相同(无变化)"
        print(f"  {zh}({code}) {r['cat2024']} -> {r['cat2040']}  人口{r['pop2040']/1e6:.1f}M{flag}")

print("\n=== 未提及国家是否保持原等级 ===")
chk = df[(~df["promoted"]) & (df["cat2024"] != df["cat2040"])]
print("不一致:", chk[["code", "cat2024", "cat2040"]].to_dict("records") if len(chk) else "无（全部保持）")
