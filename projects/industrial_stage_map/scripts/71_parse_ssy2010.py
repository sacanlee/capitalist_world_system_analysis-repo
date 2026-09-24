# -*- coding: utf-8 -*-
"""解析世界钢铁协会《Steel Statistical Yearbook 2012》(raw/worldsteel_ssy2012.pdf)
"Table 1 Production of Crude Steel"（2002-2011 逐年，kt），取 2010 列。
输出 data/steel_2010_raw.csv + 世界合计核对。"""
import os
import re

import pdfplumber
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(BASE, "raw", "worldsteel_ssy2012.pdf")
OUT = os.path.join(BASE, "data", "steel_2010_raw.csv")
YEAR = 2010

HEADER_RE = re.compile(r"^\s*2002\s+2003\s+2004\s")

rows_out = []
with pdfplumber.open(PDF) as pdf:
    pages = [i for i, p in enumerate(pdf.pages)
             if re.match(r"^Table\s+1\b.*Production of Crude Steel",
                         (p.extract_text() or "").split("\n")[0].strip())]
    print("粗钢表页(0-based):", pages)

    for pi in pages:
        page = pdf.pages[pi]
        words = page.extract_words(use_text_flow=False)
        lines = {}
        for w in words:
            lines.setdefault(round(w["top"] / 3.0), []).append(w)

        header_cols = None
        for key in sorted(lines):
            ws = sorted(lines[key], key=lambda w: w["x0"])
            text = " ".join(w["text"] for w in ws)
            if HEADER_RE.match(text):
                toks = [w for w in ws if re.fullmatch(r"\d{4}", w["text"])]
                header_cols = [(int(w["text"]), w["x0"], w["x1"]) for w in toks]
                print(f"page {pi}: 年份={[c[0] for c in header_cols]}")
                continue
            if header_cols is None:
                continue
            year_x0 = min(c[1] for c in header_cols)
            name_words = [w for w in ws if w["x1"] <= year_x0 - 2]
            val_words = [w for w in ws if w["x1"] > year_x0 - 2]
            if not name_words:
                continue
            name = " ".join(w["text"] for w in name_words).strip()
            if not name or name.lower().startswith("table"):
                continue
            centers = [(y, (x0 + x1) / 2.0) for y, x0, x1 in header_cols]
            buckets = {y: [] for y, _ in centers}
            for w in sorted(val_words, key=lambda w: w["x0"]):
                cx = (w["x0"] + w["x1"]) / 2.0
                y = min(centers, key=lambda c: abs(c[1] - cx))[0]
                buckets[y].append(w["text"])
            vals = {}
            for y, toks in buckets.items():
                s = "".join(toks).replace(" ", "")
                if s == "":
                    vals[y] = None
                elif s.lower().endswith("e"):
                    vals[y] = float(s[:-1].replace(",", ""))
                elif s in ("...", "..", "."):
                    vals[y] = None
                elif re.fullmatch(r"[\d,]+", s):
                    vals[y] = float(s.replace(",", ""))
                else:
                    vals[y] = s
            rows_out.append({"page": pi, "name": name, **{str(y): vals.get(y) for y, _ in centers}})

df = pd.DataFrame(rows_out)
df.to_csv(OUT, index=False, encoding="utf-8-sig")
ycols = [c for c in df.columns if re.fullmatch(r"\d{4}", str(c))]
num = df[ycols].apply(pd.to_numeric, errors="coerce")
print(f"\n解析行数={len(df)}")
print("各年非空计数:", {c: int(num[c].notna().sum()) for c in ycols})
print("\n各年合计(Mt):", {c: round(num[c].sum() / 1000) for c in ycols})

print(f"\n=== {YEAR} 前25大 ===")
sub = df[["name", str(YEAR)]].copy()
sub["v"] = pd.to_numeric(sub[str(YEAR)], errors="coerce")
print(sub.dropna(subset=["v"]).sort_values("v", ascending=False).head(25).to_string(index=False))
