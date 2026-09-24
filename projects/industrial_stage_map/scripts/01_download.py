# -*- coding: utf-8 -*-
"""下载人口(OWID/UN WPP2024)与USGS铁钢核对PDF。"""
import os
import sys

import requests

PROXY = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")

TARGETS = [
    ("https://ourworldindata.org/grapher/population.csv", "owid_pop_wpp2024.csv"),
    ("https://pubs.usgs.gov/periodicals/mcs2025/mcs2025-iron-steel.pdf", "usgs_mcs2025-iron-steel.pdf"),
    ("https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-iron-steel.pdf", "usgs_mcs2026-iron-steel.pdf"),
]

for url, name in TARGETS:
    dest = os.path.join(RAW, name)
    if os.path.exists(dest) and os.path.getsize(dest) > 5000:
        print("skip (exists)", name)
        continue
    try:
        r = requests.get(url, proxies=PROXY, timeout=120)
        r.raise_for_status()
        with open(dest, "wb") as f:
            f.write(r.content)
        print("OK", name, len(r.content), "bytes")
    except Exception as e:
        print("FAIL", name, repr(e)[:200])
