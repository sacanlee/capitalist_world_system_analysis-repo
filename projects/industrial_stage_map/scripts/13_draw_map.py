# -*- coding: utf-8 -*-
"""绘制世界工业化阶段地图（6类着色+未分类灰），下方附"工业化标准划分说明"与人口统计。"""
import csv
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Patch

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "out")

plt.rcParams["font.family"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

WORLD_POP = 8161972574
CATS = ["发达国家", "中国", "工业化国家", "工业化中期国家", "工业化起步国家", "准备工业化国家"]
COLORS = {"发达国家": "#1f4e79", "中国": "#c00000", "工业化国家": "#e26b0a",
          "工业化中期国家": "#ffc000", "工业化起步国家": "#a9d08e", "准备工业化国家": "#a6a6a6",
          "未分类": "#b39ddb"}

fin = {}
with open(os.path.join(DATA, "final.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        fin[r["code"]] = r

with open(os.path.join(BASE, "raw", "ne_110m_countries.geojson"), encoding="utf-8") as f:
    gj = json.load(f)


def polys_of(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"]]
    return geom["coordinates"]


def ring_area(ring):
    s = 0.0
    for i in range(len(ring) - 1):
        x1, y1 = ring[i][0], ring[i][1]
        x2, y2 = ring[i + 1][0], ring[i + 1][1]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


ALIAS = {"SDS": "SSD"}  # NE地图中南苏丹码为SDS，数据中为SSD

feats = []
for ft in gj["features"]:
    pr = ft["properties"]
    code = pr.get("ADM0_A3")
    if code == "ATA":
        continue
    geom = ft["geometry"]
    if geom is None:
        continue
    code = ALIAS.get(code, code)
    cat = fin[code]["category"] if code in fin else "未分类"
    area = max(ring_area(p[0]) for p in polys_of(geom))
    feats.append((area, code, pr.get("NAME_ZH") or pr.get("NAME"), cat, polys_of(geom)))

# 按面积从大到小绘制：小的（飞地/内陆小国）后画，避免被覆盖
feats.sort(key=lambda t: -t[0])

polys, facecolors = [], []
for area, code, name, cat, ps in feats:
    for p in ps:
        polys.append([(x, y) for x, y in p[0]])
        facecolors.append(COLORS[cat])

fig = plt.figure(figsize=(16.5, 12.2), dpi=140)
ax = fig.add_axes([0.012, 0.44, 0.976, 0.515])
ax.add_collection(PolyCollection(polys, facecolors=facecolors, edgecolors="white", linewidths=0.35))
ax.set_xlim(-180, 180)
ax.set_ylim(-57, 84)
ax.set_aspect("auto")
ax.axis("off")
ax.set_title("全球工业化阶段地图（按中国1990/2000/2012年人均发电量与人均钢产量标准划分）",
             fontsize=19, pad=8)

# ---- 图例 ----
handles = [Patch(facecolor=COLORS[c], edgecolor="#999999", label=c) for c in CATS]
handles.append(Patch(facecolor=COLORS["未分类"], edgecolor="#999999", label="人口不足1000万（未分类）"))
leg = fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.432), ncol=7,
                 frameon=False, fontsize=12.5, handlelength=1.4, handleheight=1.0, columnspacing=1.4)
for t in leg.get_texts():
    t.set_color("#222222")
fig.canvas.draw()
bb = leg.get_window_extent(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())
sub_y = bb.y0 - 0.012
fig.text(0.5, sub_y, "人口≥1000万的国家 · 2024年数据 · 台湾按中国着色",
         ha="center", va="top", fontsize=11.5, color="#444444")

# ---- 下方文字 ----
y = sub_y - 0.024
fig.text(0.03, y, "工业化标准划分说明", fontsize=15, weight="bold")
y -= 0.026
lines = [
    "1. 记分方法：得分 =（该国人均发电量 ÷ 中国人均发电量）+（该国人均钢产量 ÷ 中国人均钢产量），得分 > 2 视为达到该年份的工业化标准。",
    "2. 中国基准（UN WPP2024人口）：1990年 人均发电量538.5 kWh、人均钢产量57.6 kg；2000年 1067.8 kWh、101.2 kg；2012年 3641.8 kWh、529.2 kg。",
    "3. 分类规则：发达国家（IMF发达经济体口径）为最高阶段；中国单独列出；其余国家依次对照——达2012年标准为工业化国家，达2000年标准为工业化中期国家，达1990年标准为工业化起步国家，均未达为准备工业化国家。",
    "4. 数据来源：人口=联合国WPP2024；发电量=Ember（OWID整理）2024年，乌克兰为EIA 2024年96.9 TWh；粗钢产量=世界钢铁协会2024年，未列入其国别表的国家采用BGS《World Mineral Production 2020-2024》。",
]
for t in lines:
    fig.text(0.03, y, t, fontsize=10.8, color="#333333", wrap=True)
    y -= 0.023

# ---- 人口统计表 ----
g = {}
for r in fin.values():
    g.setdefault(r["category"], []).append(float(r["pop2024"]))
rows = sorted(((c, len(v), sum(v)) for c, v in g.items()), key=lambda t: -t[2])
tot95 = sum(v for _, _, v in rows)
uncls = WORLD_POP - tot95

y -= 0.008
fig.text(0.03, y, "各阶段人口（2024年）", fontsize=15, weight="bold")
y -= 0.028
cols = [0.045, 0.30, 0.42, 0.55]
fig.text(cols[0], y, "类别", fontsize=11.5, weight="bold")
fig.text(cols[1], y, "国家数", fontsize=11.5, weight="bold")
fig.text(cols[2], y, "总人口", fontsize=11.5, weight="bold")
fig.text(cols[3], y, "占全球总人口比重", fontsize=11.5, weight="bold")
y -= 0.024
for c, n, p in rows:
    label = "中国（含台湾）" if c == "中国" else c
    fig.text(cols[0], y, label, fontsize=11.5,
             color=COLORS[c] if c != "中国" else COLORS["中国"], weight="bold" if c == "中国" else "normal")
    fig.text(cols[1], y, f"{n} 国" if c != "中国" else "1 国", fontsize=11.5)
    fig.text(cols[2], y, f"{p/1e8:.2f} 亿", fontsize=11.5)
    fig.text(cols[3], y, f"{p/WORLD_POP*100:.1f}%", fontsize=11.5)
    y -= 0.0225
fig.text(cols[0], y, "以上合计", fontsize=11.5)
fig.text(cols[1], y, "95 国", fontsize=11.5)
fig.text(cols[2], y, f"{tot95/1e8:.2f} 亿", fontsize=11.5)
fig.text(cols[3], y, f"{tot95/WORLD_POP*100:.1f}%", fontsize=11.5)
y -= 0.024
fig.text(0.03, y, f"注：全球其余约 {uncls/1e8:.2f} 亿人（{uncls/WORLD_POP*100:.1f}%）所在国家人口不足1000万，未参与分类统计。"
                  "处于标准线附近的国家：厄瓜多尔（2000年标准1.96）、塔吉克斯坦（1.96）、玻利维亚（1990年标准2.02）、洪都拉斯（2.14）、朝鲜（2.13）。",
         fontsize=9.8, color="#666666")

fig.savefig(os.path.join(OUT, "world_industrial_stage_map.png"), facecolor="white")
print("saved")
for c, n, p in rows:
    print(f"{c}\t{n}\t{p:,.0f}\t{p/WORLD_POP*100:.2f}%")
print(f"未分类\t-\t{uncls:,.0f}\t{uncls/WORLD_POP*100:.2f}%")
