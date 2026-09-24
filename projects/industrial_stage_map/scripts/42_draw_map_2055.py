# -*- coding: utf-8 -*-
"""2055年推演地图：7类着色，人口用联合国WPP2024中等情景2055年数。"""
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

WORLD_POP = 9846237566.0  # UN WPP2024 中等情景 2055年全球人口
ORDER = ["后工业化国家", "成熟工业化国家", "工业化中后期国家", "工业化中期国家",
         "工业化起步国家", "准备工业化国家"]
DISPLAY = {"后工业化国家": "后工业化国家（发达国家）"}
COLORS = {"后工业化国家": "#1f4e79", "成熟工业化国家": "#e8590c",
          "工业化中后期国家": "#ffa94d", "工业化中期国家": "#ffd43b",
          "工业化起步国家": "#a9d08e", "准备工业化国家": "#adb5bd",
          "未分类": "#b39ddb"}

fin = {}
with open(os.path.join(DATA, "final_2055.csv"), encoding="utf-8-sig") as f:
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


ALIAS = {"SDS": "SSD"}

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
    cat = fin[code]["cat2055"] if code in fin else "未分类"
    area = max(ring_area(p[0]) for p in polys_of(geom))
    feats.append((area, code, pr.get("NAME_ZH") or pr.get("NAME"), cat, polys_of(geom)))

feats.sort(key=lambda t: -t[0])

polys, facecolors = [], []
for area, code, name, cat, ps in feats:
    for p in ps:
        polys.append([(x, y) for x, y in p[0]])
        facecolors.append(COLORS[cat])

fig = plt.figure(figsize=(16.5, 13.4), dpi=140)
ax = fig.add_axes([0.012, 0.535, 0.976, 0.425])
ax.add_collection(PolyCollection(polys, facecolors=facecolors, edgecolors="white", linewidths=0.35))
ax.set_xlim(-180, 180)
ax.set_ylim(-57, 84)
ax.set_aspect("auto")
ax.axis("off")
ax.set_title("全球工业化阶段地图（2055年推演）", fontsize=20, pad=8)

# ---- 图例 ----
handles = [Patch(facecolor=COLORS[c], edgecolor="#999999", label=DISPLAY.get(c, c)) for c in ORDER]
handles.append(Patch(facecolor=COLORS["未分类"], edgecolor="#999999", label="其他人口不足1000万国家"))
leg = fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.522), ncol=4,
                 frameon=False, fontsize=12.5, handlelength=1.4, handleheight=1.0,
                 columnspacing=2.2, labelspacing=0.55)
for t in leg.get_texts():
    t.set_color("#222222")
fig.canvas.draw()
bb = leg.get_window_extent(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())
sub_y = bb.y0 - 0.010
fig.text(0.5, sub_y, "人口1000万及以上国家 · 人口为联合国WPP2024中等情景2055年数",
         ha="center", va="top", fontsize=11.5, color="#444444")

# ---- 下方文字 ----
y = sub_y - 0.026
fig.text(0.03, y, "工业化标准划分说明（2055年推演）", fontsize=15, weight="bold")
y -= 0.027
lines = [
    "1. 阶段标准（标准人均发电量 / 标准人均钢产量）：成熟工业化国家 4000 kWh / 400 kg；工业化中后期国家 3000 kWh / 300 kg；工业化中期国家 1000 kWh / 100 kg；工业化起步国家 500 kWh / 50 kg；记分得分 > 2 视为达标。",
    "2. 本图为2055年推演：以2040年推演为基础，按经济发展趋势调整部分国家的阶段；未提及的国家保持2040年等级。",
    "3. 晋级情况：2国晋级发达国家（俄罗斯、土耳其）；7国晋级成熟工业化国家（印度、印度尼西亚、墨西哥、伊拉克、南非、泰国、阿根廷）；10国晋级工业化中后期国家（埃及、菲律宾、阿尔及利亚等）；",
    "　　32国晋级工业化中期国家（巴基斯坦、尼日利亚、孟加拉国、埃塞俄比亚等）；17国晋级工业化起步国家（刚果民主共和国、苏丹、也门等，详见 out/工业化阶段清单_2055.md）。",
    "4. 数据来源：人口 = 联合国 WPP2024 中等生育率情景 2055年；人均发电量、人均钢产量为 2024年数据（Ember / 世界钢铁协会、BGS），2055年等级为趋势推演。",
]
for t in lines:
    fig.text(0.03, y, t, fontsize=10.6, color="#333333")
    y -= 0.021

# ---- 人口统计表 ----
g = {}
for r in fin.values():
    g.setdefault(r["cat2055"], []).append(float(r["pop2055"]))
tot = sum(v for vs in g.values() for v in vs)
uncls = WORLD_POP - tot
rows = [(c, len(g.get(c, [])), sum(g.get(c, []))) for c in ORDER]

y -= 0.004
fig.text(0.03, y, "各阶段人口（2055年，联合国中等情景）", fontsize=15, weight="bold")
y -= 0.028
cols = [0.045, 0.30, 0.42, 0.55]
fig.text(cols[0], y, "类别", fontsize=11.5, weight="bold")
fig.text(cols[1], y, "国家数", fontsize=11.5, weight="bold")
fig.text(cols[2], y, "总人口", fontsize=11.5, weight="bold")
fig.text(cols[3], y, "占全球总人口比重", fontsize=11.5, weight="bold")
y -= 0.0235
for c, n, p in rows:
    fig.text(cols[0], y, DISPLAY.get(c, c), fontsize=11.5, color=COLORS[c])
    fig.text(cols[1], y, f"{n} 国", fontsize=11.5)
    fig.text(cols[2], y, f"{p/1e8:.2f} 亿", fontsize=11.5)
    fig.text(cols[3], y, f"{p/WORLD_POP*100:.1f}%", fontsize=11.5)
    y -= 0.0205
fig.text(cols[0], y, "其他人口不足1000万国家", fontsize=11.5)
fig.text(cols[1], y, "—", fontsize=11.5)
fig.text(cols[2], y, f"{uncls/1e8:.2f} 亿", fontsize=11.5)
fig.text(cols[3], y, f"{uncls/WORLD_POP*100:.1f}%", fontsize=11.5)
y -= 0.021
fig.text(cols[0], y, "全球合计", fontsize=11.5, weight="bold")
fig.text(cols[1], y, f"{len(fin)} 个实体", fontsize=11.5)
fig.text(cols[2], y, f"{WORLD_POP/1e8:.2f} 亿", fontsize=11.5, weight="bold")
fig.text(cols[3], y, "100.0%", fontsize=11.5, weight="bold")

y -= 0.025
notes = [
    "注：俄罗斯、土耳其晋级发达国家（其余发达国家保持2040年等级）。2055年已无处于准备工业化阶段的国家（也门晋级工业化起步国家）。"
    "跨两档晋级：印度尼西亚、阿根廷（工业化中期→成熟工业化国家）、埃塞俄比亚（准备工业化→工业化中期国家）。",
]
for t in notes:
    fig.text(0.03, y, t, fontsize=9.6, color="#666666")
    y -= 0.019

fig.savefig(os.path.join(OUT, "world_industrial_stage_map_2055.png"), facecolor="white")
print("saved out/world_industrial_stage_map_2055.png")
for c, n, p in rows:
    print(f"{c}\t{n}\t{p:,.0f}\t{p/WORLD_POP*100:.2f}%")
print(f"不足1000万\t-\t{uncls:,.0f}\t{uncls/WORLD_POP*100:.2f}%")
print(f"总计\t{len(fin)}\t{tot:,.0f}\t{tot/WORLD_POP*100:.2f}%")
