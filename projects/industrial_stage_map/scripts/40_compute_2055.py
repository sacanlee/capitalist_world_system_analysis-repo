# -*- coding: utf-8 -*-
"""2055年推演：以2040年推演结果为基础，按用户给定晋级名单调整部分国家阶段；
人口用联合国WPP2024中等生育率情景2055年。输出 data/final_2055.csv。"""
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
RAW = os.path.join(BASE, "raw")

# ---- 用户给定2055年晋级名单（中文名 -> ISO）----
PROMOTE = {
    "后工业化国家": [("俄罗斯", "RUS"), ("土耳其", "TUR")],  # 2055年晋级发达国家
    "成熟工业化国家": [("印度", "IND"), ("印度尼西亚", "IDN"), ("墨西哥", "MEX"), ("伊拉克", "IRQ"),
                       ("南非", "ZAF"), ("泰国", "THA"), ("阿根廷", "ARG")],
    "工业化中后期国家": [("埃及", "EGY"), ("阿塞拜疆", "AZE"), ("阿尔及利亚", "DZA"),
                         ("摩洛哥", "MAR"), ("委内瑞拉", "VEN"),
                         ("突尼斯", "TUN"), ("乌兹别克斯坦", "UZB"),
                         ("塔吉克斯坦", "TJK"), ("菲律宾", "PHL"), ("约旦", "JOR")],
    "工业化中期国家": [("巴基斯坦", "PAK"), ("尼日利亚", "NGA"), ("孟加拉国", "BGD"), ("肯尼亚", "KEN"),
                       ("坦桑尼亚", "TZA"), ("乌干达", "UGA"), ("安哥拉", "AGO"), ("莫桑比克", "MOZ"),
                       ("科特迪瓦", "CIV"), ("加纳", "GHA"), ("赞比亚", "ZMB"), ("塞内加尔", "SEN"),
                       ("津巴布韦", "ZWE"), ("缅甸", "MMR"), ("叙利亚", "SYR"), ("尼泊尔", "NPL"),
                       ("柬埔寨", "KHM"), ("朝鲜", "PRK"), ("斯里兰卡", "LKA"), ("危地马拉", "GTM"),
                       ("几内亚", "GIN"), ("卢旺达", "RWA"), ("玻利维亚", "BOL"), ("洪都拉斯", "HND"),
                       ("古巴", "CUB"), ("纳米比亚", "NAM"), ("博茨瓦纳", "BWA"),
                       ("埃塞俄比亚", "ETH")],
    "工业化起步国家": [("刚果民主共和国", "COD"), ("苏丹", "SDN"), ("喀麦隆", "CMR"),
                       ("马达加斯加", "MDG"), ("贝宁", "BEN"), ("马里", "MLI"), ("布基纳法索", "BFA"),
                       ("海地", "HTI"), ("巴布亚新几内亚", "PNG"), ("阿富汗", "AFG"), ("南苏丹", "SSD"),
                       ("尼日尔", "NER"), ("乍得", "TCD"), ("马拉维", "MWI"), ("布隆迪", "BDI"),
                       ("索马里", "SOM"), ("也门", "YEM")],
}

promote_map = {}
for cat, lst in PROMOTE.items():
    for zh, code in lst:
        assert code not in promote_map, f"重复: {code}"
        promote_map[code] = cat

# ---- 2040年分类（基准）----
d40 = pd.read_csv(os.path.join(DATA, "final_2040.csv"))
cat40 = dict(zip(d40["code"], d40["cat2040"]))
name40 = dict(zip(d40["code"], d40["entity"]))
need = set(cat40)

# ---- 2055人口（UN WPP2024 中等情景）----
pop = pd.read_csv(os.path.join(RAW, "owid_pop_lr.csv"))
pop55 = pop[pop["Year"] == 2055]
p55 = {}
for _, r in pop55.iterrows():
    c = r["Code"]
    if isinstance(c, str) and c in need:
        v = r["Population (projections) (Projected)"]
        if pd.notna(v):
            p55[c] = float(v)
world55 = float(pop55[pop55["Code"] == "OWID_WRL"]["Population (projections) (Projected)"].iloc[0])
missing = need - set(p55)
assert not missing, f"缺2055人口: {missing}"

rows = []
for code in sorted(need, key=lambda c: -p55[c]):
    c40 = cat40[code]
    c55 = promote_map.get(code, c40)
    rows.append({"code": code, "entity": name40[code], "pop2055": p55[code],
                 "cat2040": c40, "cat2055": c55, "promoted": code in promote_map})
df = pd.DataFrame(rows)
df.to_csv(os.path.join(DATA, "final_2055.csv"), index=False, encoding="utf-8-sig")

print(f"实体数={len(df)}  全球2055人口={world55:,.0f}  其中分类国家人口={df['pop2055'].sum():,.0f}")
print("\n=== 2055年分类汇总 ===")
g = df.groupby("cat2055").agg(n=("code", "size"), pop=("pop2055", "sum")).sort_values("pop", ascending=False)
for c, r in g.iterrows():
    print(f"{c:<12} {int(r['n']):>3}国  {r['pop']/1e8:>6.2f}亿  {r['pop']/world55*100:>5.2f}%")
rest = world55 - df["pop2055"].sum()
print(f"{'其他<1000万':<12}   -国  {rest/1e8:>6.2f}亿  {rest/world55*100:>5.2f}%")

print("\n=== 晋级核对（2040 -> 2055）===")
two_step = []
for cat, lst in PROMOTE.items():
    if not lst:
        print(f"\n[{cat}] 无")
        continue
    print(f"\n[{cat}] {len(lst)}国")
    for zh, code in lst:
        r = df[df["code"] == code].iloc[0]
        flag = ""
        if r["cat2040"] == r["cat2055"]:
            flag = "  ← 与2040相同(无变化)"
        else:
            order = ["准备工业化国家", "工业化起步国家", "工业化中期国家", "工业化中后期国家",
                     "成熟工业化国家", "后工业化国家"]
            d = order.index(r["cat2055"]) - order.index(r["cat2040"])
            if d >= 2:
                flag = f"  ← 跨{d}档"
                two_step.append((zh, r["cat2040"], r["cat2055"]))
        print(f"  {zh}({code}) {r['cat2040']} -> {r['cat2055']}  人口{r['pop2055']/1e6:.1f}M{flag}")

print("\n=== 未提及国家是否保持2040等级 ===")
chk = df[(~df["promoted"]) & (df["cat2040"] != df["cat2055"])]
print("不一致:", chk[["code", "cat2040", "cat2055"]].to_dict("records") if len(chk) else "无（全部保持）")
print("\n跨档国家:", two_step if two_step else "无")
