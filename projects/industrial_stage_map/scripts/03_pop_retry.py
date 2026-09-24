# -*- coding: utf-8 -*-
"""尝试多个来源获取2024年人口；并 dump USGS 全文。"""
import os

import pandas as pd
import requests

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw")
PROXY = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}

CANDS = [
    ("https://ourworldindata.org/grapher/population.csv?v=1&csvType=full&useColumnShortNames=true", "owid_pop_v2.csv"),
    ("https://ourworldindata.org/grapher/population.csv?csvType=full", "owid_pop_v3.csv"),
    ("https://ourworldindata.org/grapher/population-long-run-with-projections.csv", "owid_pop_lr.csv"),
]

for url, name in CANDS:
    dest = os.path.join(RAW, name)
    if not (os.path.exists(dest) and os.path.getsize(dest) > 5000):
        try:
            r = requests.get(url, proxies=PROXY, timeout=180)
            r.raise_for_status()
            with open(dest, "wb") as f:
                f.write(r.content)
            print("DL OK", name, len(r.content))
        except Exception as e:
            print("DL FAIL", name, repr(e)[:150])
            continue
    try:
        df = pd.read_csv(dest)
        cols = df.columns.tolist()
        ycol = [c for c in cols if "ear" in c.lower()][0]
        print(name, "| cols:", cols, "| year range:", df[ycol].min(), df[ycol].max(), "| rows:", len(df))
        chn = df[df.iloc[:, 0] == "China"]
        if len(chn):
            print("   China max year row:", chn.sort_values(ycol).iloc[-1].tolist())
    except Exception as e:
        print(name, "parse fail", repr(e)[:150])

print("\n===== USGS mcs2026 full text =====")
from pypdf import PdfReader

txt = "\n".join((p.extract_text() or "") for p in PdfReader(os.path.join(RAW, "usgs_mcs2026-iron-steel.pdf")).pages)
print(txt)
