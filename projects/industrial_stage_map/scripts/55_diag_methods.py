# -*- coding: utf-8 -*-
"""诊断：各档在不同稳健统计量、名义/PPP口径下的代表值，找出中后期<中期的原因。"""
import csv
import os

import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

ORDER = ["后工业化国家", "成熟工业化国家", "工业化中后期国家", "工业化中期国家",
         "工业化起步国家", "准备工业化国家"]

mw = pd.read_csv(os.path.join(DATA, "minwage_raw.csv"))
d24 = pd.read_csv(os.path.join(DATA, "final_v2.csv"))
FIX = {"Democratic Republic of Congo": "Democratic Republic of the Congo",
       "Cote d'Ivoire": "Côte d'Ivoire", "Czechia": "Czech Republic"}
wiki = {r["wiki_name"]: r for _, r in mw.iterrows()}
IMPUTE = {"TUR": (7317.0 / 12, 7317.0 / 12 * 12 / 2.6)}  # 名义, PPP≈名义*?
rows = []
for _, r in d24.iterrows():
    w = wiki.get(FIX.get(r["entity"], r["entity"]))
    nom = ppp = None
    if w is not None:
        if pd.notna(w["annual_nom"]):
            nom = float(w["annual_nom"]) / 12
        if pd.notna(w["annual_ppp"]):
            ppp = float(w["annual_ppp"]) / 12
    rows.append({"entity": r["entity"], "category": r["category"], "nom": nom, "ppp": ppp})
df = pd.DataFrame(rows)


def stats(v):
    v = np.sort(np.asarray(v, dtype=float))
    n = len(v)
    if n == 0:
        return {}
    lv = np.log10(v)
    q1, q3 = np.percentile(lv, 25), np.percentile(lv, 75)
    iqr = q3 - q1
    lo, hi = 10 ** (q1 - 1.5 * iqr), 10 ** (q3 + 1.5 * iqr)
    keep = v[(v >= lo) & (v <= hi)]
    med = np.median(v)
    mad = np.median(np.abs(lv - np.median(lv)))
    if mad == 0:
        keep_mad = v
    else:
        mz = 0.6745 * (lv - np.median(lv)) / mad
        keep_mad = v[np.abs(mz) <= 3.5]
    # 四分位均值（interquartile mean, 标准稳健统计量）
    iqm = v[(v >= 10 ** q1) & (v <= 10 ** q3)].mean() if n >= 4 else np.nan
    k = int(np.floor(0.2 * n))
    trim20 = np.sort(v)[k:n - k].mean() if n - 2 * k > 0 else np.nan
    return {"n": n, "median": med, "trim20": trim20, "iqm": iqm,
            "iqr_keep_n": len(keep), "iqr_mean": keep.mean(),
            "mad_keep_n": len(keep_mad), "mad_mean": keep_mad.mean()}


for col, label in [("nom", "名义美元/月"), ("ppp", "PPP国际元/月")]:
    print(f"\n===== {label} =====")
    print(f"{'类别':<12}{'n':>3}{'中位数':>9}{'20%截尾均值':>11}{'四分位均值':>10}{'IQR均值':>9}{'MAD均值':>9}")
    for c in ORDER:
        v = df[(df["category"] == c) & df[col].notna()][col].astype(float)
        s = stats(v)
        if not s:
            print(f"{c:<12}{0:>3}")
            continue
        print(f"{c:<12}{s['n']:>3}{s['median']:>9.0f}{s['trim20']:>11.0f}{s['iqm']:>10.0f}"
              f"{s['iqr_mean']:>9.0f}{s['mad_mean']:>9.0f}")

print("\n=== 工业化中后期档逐国 ===")
print(df[df["category"] == "工业化中后期国家"].to_string(index=False))
print("\n=== 工业化中期档逐国（按名义排序）===")
print(df[df["category"] == "工业化中期国家"].sort_values("nom", ascending=False).to_string(index=False))
print("\n=== 名义/PPP 换算系数（PPP÷名义，>1说明该国有汇率/物价扭曲）===")
for c in ORDER:
    sub = df[(df["category"] == c) & df["nom"].notna() & df["ppp"].notna()]
    if len(sub):
        sub = sub.assign(ratio=sub["ppp"] / sub["nom"])
        print(f"{c:<12} 中位系数={sub['ratio'].median():.2f}  范围{sub['ratio'].min():.2f}~{sub['ratio'].max():.2f}")
