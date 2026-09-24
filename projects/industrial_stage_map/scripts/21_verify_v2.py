# -*- coding: utf-8 -*-
"""独立复核V2：只读 csv + 手写公式，不复用20脚本任何代码。
1) 逐国重算人均值与四个阶段得分，与 final_v2.csv 比对
2) 手写 if/elif 重新分类，比对 category
3) 完整性：pop_panel 中所有 >=1000万国家是否都在
4) 人口与全球占比核对"""
import csv
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
ELEC = os.path.join(BASE, "..", "productivity_compare", "raw", "owid_electricity.csv")
WORLD_POP = 8161972574

# ---- 读 final_v2 ----
rows = []
with open(os.path.join(DATA, "final_v2.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        rows.append(r)

bad = 0


def close(a, b, tol=1e-9):
    return abs(a - b) <= tol * max(1.0, abs(b))


for r in rows:
    pop = float(r["pop2024"])
    pc_s = float(r["steel_kt"]) * 1e6 / pop
    pc_e = float(r["elec_twh"]) * 1e9 / pop
    if not close(pc_s, float(r["pc_steel_kg"]), 1e-12):
        print("人均钢不一致", r["entity"], pc_s, r["pc_steel_kg"]); bad += 1
    if not close(pc_e, float(r["pc_elec_kwh"]), 1e-12):
        print("人均电不一致", r["entity"]); bad += 1
    s = {"s_mature": pc_e / 4000.0 + pc_s / 400.0,
         "s_late": pc_e / 3000.0 + pc_s / 300.0,
         "s_mid": pc_e / 1000.0 + pc_s / 100.0,
         "s_start": pc_e / 500.0 + pc_s / 50.0}
    for k, v in s.items():
        if not close(v, float(r[k])):
            print("得分不一致", r["entity"], k, v, r[k]); bad += 1

# ---- 手写重分类 ----
IMF = set("AUS AUT BEL CAN CYP CZE DNK EST FIN FRA DEU GRC HKG ISL IRL ISR ITA JPN KOR LVA LTU LUX "
          "MAC MLT NLD NZL NOR PRT PRI SMR SGP SVK SVN ESP SWE CHE TWN GBR USA".split())
mismatch = 0
for r in rows:
    if r["code"] in IMF:
        cat = "后工业化国家"
    elif float(r["s_mature"]) > 2:
        cat = "成熟工业化国家"
    elif float(r["s_late"]) > 2:
        cat = "工业化中后期国家"
    elif float(r["s_mid"]) > 2:
        cat = "工业化中期国家"
    elif float(r["s_start"]) > 2:
        cat = "工业化起步国家"
    else:
        cat = "准备工业化国家"
    if cat != r["category"]:
        print("分类不一致", r["entity"], cat, r["category"]); mismatch += 1

# ---- 完整性 ----
pp = []
with open(os.path.join(DATA, "pop_panel.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        if r["is_country"] == "True":
            pp.append(r)
big = {r["code"] for r in pp if float(r["pop2024"]) >= 10_000_000}
inc = {r["code"] for r in rows}
print(f"\n>=1000万国家数={len(big)}  final_v2国家数={len(inc)}")
print("缺少:", sorted(big - inc), " 多出(以色列等):", sorted(inc - big))

# ---- 人口汇总 ----
order = ["后工业化国家", "中国", "成熟工业化国家", "工业化中后期国家", "工业化中期国家",
         "工业化起步国家", "准备工业化国家"]
tot = 0.0
print("\n类别\t国家数\t人口\t占全球")
for c in order:
    sub = [r for r in rows if r["category"] == c]
    p = sum(float(r["pop2024"]) for r in sub)
    tot += p
    print(f"{c}\t{len(sub)}\t{p:,.0f}\t{p/WORLD_POP*100:.2f}%")
rest = WORLD_POP - tot
print(f"不足1000万\t-\t{rest:,.0f}\t{rest/WORLD_POP*100:.2f}%")
print(f"合计\t{len(rows)}\t{tot:,.0f}\t{tot/WORLD_POP*100:.2f}%")
print(f"\n错误数={bad}  分类不一致={mismatch}")
