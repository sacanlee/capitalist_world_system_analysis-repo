# -*- coding: utf-8 -*-
"""Render sample pages of a PDF to PNG for visual checking.

Usage: python pdf_check.py <pdf> <outprefix> [page ...]
"""
import os, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pymupdf

pdf, prefix = sys.argv[1], sys.argv[2]
pages = [int(p) for p in sys.argv[3:]] or [1]
doc = pymupdf.open(pdf)
print('pages:', doc.page_count)
for p in pages:
    if p < 1 or p > doc.page_count:
        continue
    pix = doc[p - 1].get_pixmap(dpi=90)
    out = f'{prefix}_p{p}.png'
    pix.save(out)
    print('wrote', out, pix.width, 'x', pix.height)
