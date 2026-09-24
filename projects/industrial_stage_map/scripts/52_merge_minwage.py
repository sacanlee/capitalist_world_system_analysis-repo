# -*- coding: utf-8 -*-
"""维基最低工资 × 2024年分类：逐国匹配，统计各类别平均值。输出 data/minwage_2024.csv"""
import csv
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

mw = pd.read_csv(os.path.join(DATA, "minwage_raw.csv"))
d24 = pd.read_csv(os.path.join(DATA, "final_v2.csv"))

# 名称修正：我们的entity名 -> 维基表名
FIX = {
    "Democratic Republic of Congo": "Democratic Republic of the Congo",
    "Cote d'Ivoire": "Côte d'Ivoire",
    "Czechia": "Czech Republic",
}
wiki_by_name = {}
for _, r in mw.iterrows():
    wiki_by_name.setdefault(r["wiki_name"], r)

rows, miss = [], []
for _, r in d24.iterrows():
    ent = r["entity"]
    w = wiki_by_name.get(FIX.get(ent, ent))
    if w is None:
        miss.append((ent, "表中无此国"))
        rows.append({"code": r["code"], "entity": ent, "category": r["category"],
                     "annual_nom": None, "annual_ppp": None, "note": "维基表未列该国"})
        continue
    note = ""
    if pd.isna(w["annual_nom"]) and pd.isna(w["annual_ppp"]):
        note = "无法定最低工资/无数据"
        miss.append((ent, note))
    rows.append({"code": r["code"], "entity": ent, "category": r["category"],
                 "annual_nom": w["annual_nom"], "annual_ppp": w["annual_ppp"],
                 "wiki_name": w["wiki_name"], "eff": w["eff"], "note": note})

df = pd.DataFrame(rows)
df.to_csv(os.path.join(DATA, "minwage_2024.csv"), index=False, encoding="utf-8-sig")

print(f"匹配国家数={len(df)}  缺数据={len(miss)}")
print("\n缺数据的国家:")
for e, n in miss:
    print(f"  {e}  ({n})")

ORDER = ["后工业化国家", "成熟工业化国家", "工业化中后期国家", "工业化中期国家",
         "工业化起步国家", "准备工业化国家"]
print("\n=== 各类别最低工资（年度，美元）===")
print(f"{'类别':<12}{'国家数':>5}{'有数据':>6}{'名义均值':>10}{'名义中位':>10}{'PPP均值':>10}{'PPP中位':>10}")
for c in ORDER:
    sub = df[(df["category"] == c)]
    sn = sub["annual_nom"].dropna()
    sp = sub["annual_ppp"].dropna()
    print(f"{c:<12}{len(sub):>5}{len(sn):>6}{sn.mean():>10.0f}{sn.median():>10.0f}"
          f"{sp.mean() if len(sp) else float('nan'):>10.0f}{sp.median() if len(sp) else float('nan'):>10.0f}")
