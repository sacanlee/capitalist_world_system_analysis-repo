# -*- coding: utf-8 -*-
"""用 requests 下载 AcoBrasil 月度PDF（含worldsteel准会员国粗钢表）。"""
import os
import requests

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw")
PROXY = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"}

URLS = [
    ("acobrasil_jan2025.pdf", "https://www.acobrasil.org.br/site/wp-content/uploads/2025/01/AcoBrasil_EM_Janeiro_2025.pdf"),
    ("acobrasil_2025.pdf", "https://www.acobrasil.org.br/site/wp-content/uploads/2025/02/AcoBrasil_EM_Fevereiro_2025.pdf"),
]
for name, url in URLS:
    try:
        r = requests.get(url, proxies=PROXY, headers=HDR, timeout=60, verify=True)
        print(name, r.status_code, len(r.content), r.headers.get("content-type"))
        if r.status_code == 200 and r.content[:4] == b"%PDF":
            with open(os.path.join(RAW, name), "wb") as f:
                f.write(r.content)
            print("  saved ->", name)
    except Exception as e:
        print(name, "ERR", type(e).__name__, str(e)[:200])
