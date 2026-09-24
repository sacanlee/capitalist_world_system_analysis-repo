# -*- coding: utf-8 -*-
"""诊断：定位 SSY2003 PDF 中「Total Production of Crude Steel」表格页，打印页面几何与词坐标。"""
import os
import sys

import pdfplumber

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(BASE, "raw", "worldsteel_ssy2003.pdf")

with pdfplumber.open(PDF) as pdf:
    print("总页数:", len(pdf.pages))
    hits = []
    for i, page in enumerate(pdf.pages):
        txt = page.extract_text() or ""
        if "Total Production of Crude Steel" in txt:
            hits.append(i)
    print("含标题页(0-based):", hits)

    if not hits:
        sys.exit(0)

    for i in hits[:4]:
        page = pdf.pages[i]
        print(f"\n===== page index {i} size={page.width}x{page.height} =====")
        txt = page.extract_text() or ""
        print("--- raw text (first 1200 chars) ---")
        print(txt[:1200])
        words = page.extract_words()
        print(f"--- words={len(words)} ---")
        for w in words[:25]:
            print(f"  x0={w['x0']:7.1f} x1={w['x1']:7.1f} top={w['top']:6.1f} {w['text']!r}")
