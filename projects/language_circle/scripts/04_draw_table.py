# -*- coding: utf-8 -*-
"""04_draw_table.py — 圈层统计表图片（中英双语）
8大圈+15子圈: 2025/2050/2055人口及全球占比、2025出生及占比
"""
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "out")
sys.path.insert(0, os.path.join(BASE, "scripts"))
from circles_def import TOPS, SUBS, COLORS

plt.rcParams["font.family"] = ["Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

stats = {}
with open(os.path.join(DATA, "circle_stats.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        stats[r["code"]] = r

fig = plt.figure(figsize=(16.6, 13), dpi=130)

fig.text(0.5, 0.968, "世界语言文化圈人口统计表（联合国WPP2024中方案）", ha="center",
         fontsize=23, weight="bold")
fig.text(0.5, 0.941, "Population of Language & Cultural Spheres of the World (UN WPP2024, Medium variant)",
         ha="center", fontsize=15, color="#333333")
fig.text(0.5, 0.916, "人口单位：亿（1亿=100 million） · 出生单位：万（1万=10 thousand） · 占比＝占全球总量比重",
         ha="center", fontsize=11.5, color="#666666")

# 列位置(数字列右对齐)
C_NAME = 0.030
CX = {"n": 0.400, "p25": 0.505, "s25": 0.578, "p55": 0.693, "s55": 0.766,
      "b25": 0.880, "bs": 0.950}
HDR = [
    ("n", "国家数", "N"), ("p25", "2025人口/亿", "Pop 2025"), ("s25", "占全球", "Share"),
    ("p55", "2055人口/亿", "Pop 2055"), ("s55", "占全球", "Share"),
    ("b25", "2025出生/万", "Births 2025"), ("bs", "占全球", "Share"),
]
yh = 0.882
for key, cn, en in HDR:
    x = CX[key]
    fig.text(x, yh, cn, fontsize=11.5, weight="bold", ha="right")
    fig.text(x, yh - 0.0145, en, fontsize=9.5, color="#666666", ha="right")
fig.text(C_NAME, yh, "文化圈 / 子圈  Sphere / Sub-sphere", fontsize=12, weight="bold")

fig.add_artist(plt.Line2D([0.03, 0.997], [yh - 0.0215, yh - 0.0215], color="#888888", lw=1.0))


COL = {"n": "n", "p25": "pop2025", "s25": "share2025",
       "p55": "pop2055", "s55": "share2055", "b25": "births2025", "bs": "bshare2025"}


def put_row(y, name, name_color, bold, r, sub=False):
    fig.text(C_NAME + (0.012 if sub else 0), y, name,
             fontsize=11.3 if not sub else 10.8, color=name_color,
             weight="bold" if bold else "normal")
    fmt = {"n": lambda v: v, "p25": lambda v: f"{float(v)/1e5:,.2f}", "s25": lambda v: f"{float(v):.2f}%",
           "p55": lambda v: f"{float(v)/1e5:,.2f}", "s55": lambda v: f"{float(v):.2f}%",
           "b25": lambda v: f"{float(v)/10:,.0f}", "bs": lambda v: f"{float(v):.2f}%"}
    for key, _, _ in HDR:
        val = r[COL[key]]
        if key == "n" and not val:
            fig.text(CX[key], y, "—", fontsize=11.3, ha="right")
            continue
        fig.text(CX[key], y, fmt[key](val), fontsize=11.3, ha="right",
                 weight="bold" if bold else "normal")


y = yh - 0.046
SUB_CIRCLES = {"E": ["E1", "E2", "E3", "E4"], "R": ["RF1", "RF2", "RS", "RP", "RO"],
               "RU": ["RU1", "RU2"]}
SHORT_SUB = {"RO": ("罗曼语圈其他（意/罗/阿）", "Romance Others (It/Ro/Al)")}
for top in TOPS:
    r = stats[top]
    put_row(y, f"{r['name_cn']}  {r['name_en']}", COLORS[top], True, r)
    y -= 0.0295
    for sub in SUB_CIRCLES.get(top, []):
        rs = stats[sub]
        cn, en = SHORT_SUB.get(sub, (rs["name_cn"], rs["name_en"]))
        put_row(y, f"· {cn}  {en}", COLORS[top], False, rs, sub=True)
        y -= 0.0295

fig.add_artist(plt.Line2D([0.03, 0.997], [y + 0.015, y + 0.015], color="#888888", lw=1.0))
r = stats["ALL"]
put_row(y, "8大圈合计（去重，多圈国家只计一次）  Any Sphere (deduplicated)", "#222222", True, r)
y -= 0.0295
r = stats["REST"]
put_row(y, "未列入清单国家·地区  Not in listed spheres", "#666666", True, r)
y -= 0.0295
wld = {"n": "237", "pop2025": 8231614.609, "share2025": 100.0,
       "pop2055": 9846238.826, "share2055": 100.0,
       "births2025": 132399.173, "bshare2025": 100.0}  # 千人
put_row(y, "全球总计  World total", "#000000", True, wld)
y -= 0.032

fig.text(0.03, y, "核心要点  Key findings", fontsize=13.5, weight="bold", color="#222222")
y -= 0.0245
st = {k: stats[k] for k in ("E", "C", "R", "A", "RU")}
sf = lambda k, col: f"{float(st[k][col])/1e5:,.2f}亿（{float(st[k]['share' + col[3:]]):.1f}%）"
findings = [
    f"① 2025年前四大圈：英语圈 {sf('E','pop2025')}、汉语圈 {sf('C','pop2025')}、罗曼语圈 {sf('R','pop2025')}、阿拉伯语圈 {sf('A','pop2025')}。",
    f"② 至2055年（联合国中方案）：英语圈升至 {sf('E','pop2055')}、罗曼语圈 {sf('R','pop2055')}、阿拉伯语圈 {sf('A','pop2055')}；汉语圈降至 {sf('C','pop2055')}、俄语圈 {sf('RU','pop2055')}。",
    f"③ 2025年出生份额：英语圈 {float(st['E']['bshare2025']):.1f}%、罗曼语圈 {float(st['R']['bshare2025']):.1f}%、汉语圈 {float(st['C']['bshare2025']):.1f}%、阿拉伯语圈 {float(st['A']['bshare2025']):.1f}%——出生格局比人口格局更加偏向英语圈与罗曼语圈（非洲高生育率；美国计入西语圈、越南计入英语圈）。",
]
for t in findings:
    fig.text(0.03, y, t, fontsize=11, color="#333333")
    y -= 0.0225

y -= 0.004
notes = [
    "注：1. 多圈国家（17国：美国、加拿大、新加坡、马来西亚、科摩罗、阿尔及利亚、摩洛哥、突尼斯、毛里塔尼亚、乍得、吉布提、塔吉克斯坦、吉尔吉斯斯坦、哈萨克斯坦、乌兹别克斯坦、越南、北塞浦路斯）",
    "　　　　同时计入所属每一圈与子圈，故各圈之和大于“8大圈合计”；北塞浦路斯无联合国数据仅地图标注；中国人口含港澳台地区。",
    "　　2. 来源：联合国《世界人口展望2024》中方案（Medium variant）；出生为2025年，2055年为预测值；国别口径与联合国一致（波多黎各、巴勒斯坦单列）。",
    "EN: Multi-sphere countries counted in every sphere (sums exceed 100%). China incl. HK/Macao/Taiwan. Source: UN WPP2024, Medium variant.",
]
for t in notes:
    fig.text(0.03, y, t, fontsize=9.8, color="#444444" if "注" in t else "#666666")
    y -= 0.0195

fig.savefig(os.path.join(OUT, "language_circles_stats_table.png"), facecolor="white")
print("saved out/language_circles_stats_table.png")
