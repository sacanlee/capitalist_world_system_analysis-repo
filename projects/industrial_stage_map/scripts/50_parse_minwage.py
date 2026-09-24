# -*- coding: utf-8 -*-
"""解析维基百科最低工资表，了解列结构。"""
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw = os.path.join(BASE, "raw", "wiki_minwage.html")

tables = pd.read_html(raw)
print("表数:", len(tables))
for i, t in enumerate(tables):
    print(f"\n--- table {i} shape={t.shape}")
    print(t.columns.tolist())
    print(t.head(3).to_string()[:800])
