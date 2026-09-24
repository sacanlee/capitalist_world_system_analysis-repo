# -*- coding: utf-8 -*-
"""诊断：SSY2012 PDF 中粗钢产量表的位置、年份列与行样例（用于2010年数据提取）。"""
import os
import re
import sys

import pdfplumber

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(BASE, "raw", "worldsteel_ssy2012.pdf")

with pdfplumber.open(PDF) as pdf:
    print("总页数:", len(pdf.pages))
    hits = []
    for i, page in enumerate(pdf.pages):
        txt = page.extract_text() or ""
        head = "\n".join(txt.split("\n")[:3])
        if re.search(r"Crude Steel", head, re.I) and re.search(r"Production", head, re.I):
            hits.append(i)
            if len(hits) <= 8:
                print(f"\n--- page {i} ---")
                for ln in txt.split("\n")[:14]:
                    print("   ", ln)
    print("\n候选页(0-based):", hits)
