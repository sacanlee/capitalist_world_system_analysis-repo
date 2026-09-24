# -*- coding: utf-8 -*-
"""1995年地图：五档着色（成熟/中后期/中期/起步/准备）+ 其他<1000万（浅紫）。
配色与 2024/2040/2055 各图一致；本图不设"后工业化国家（发达国家）"档，全部按记分归类。"""
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

WORLD_POP = 5758878977.0
ORDER = ["成熟工业化国家", "工业化中后期国家", "工业化中期国家",
         "工业化起步国家", "准备工业化国家"]
COLORS = {"成熟工业化国家": "#e8590c", "工业化中后期国家": "#ffa94d",
          "工业化中期国家": "#ffd43b", "工业化起步国家": "#a9d08e",
          "准备工业化国家": "#adb5bd", "未分类": "#b39ddb"}

fin = {}
with open(os.path.join(DATA, "final_1995.csv"), encoding="utf-8-sig") as f:
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
    cat = fin[code]["category"] if code in fin else "未分类"
    area = max(ring_area(p[0]) for p in polys_of(geom))
    feats.append((area, code, cat, polys_of(geom)))
feats.sort(key=lambda t: -t[0])

polys, facecolors = [], []
for area, code, cat, ps in feats:
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
ax.set_title("全球工业化阶段地图（1995年，按人均发电量与人均钢产量标准划分）",
             fontsize=19, pad=8)

handles = [Patch(facecolor=COLORS[c], edgecolor="#999999", label=c) for c in ORDER]
handles.append(Patch(facecolor=COLORS["未分类"], edgecolor="#999999", label="其他人口不足1000万国家"))
leg = fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.522), ncol=3,
                 frameon=False, fontsize=12.5, handlelength=1.4, handleheight=1.0,
                 columnspacing=2.2, labelspacing=0.55)
for t in leg.get_texts():
    t.set_color("#222222")
fig.canvas.draw()
bb = leg.get_window_extent(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())
sub_y = bb.y0 - 0.010
fig.text(0.5, sub_y, "人口1000万及以上国家（与2024/2040/2055各图同一国家名单） · 1995年数据 · 不设发达国家档",
         ha="center", va="top", fontsize=11.5, color="#444444")

y = sub_y - 0.023
fig.text(0.03, y, "工业化标准划分说明", fontsize=15, weight="bold")
y -= 0.027
lines = [
    "1. 记分方法：得分 =（该国人均年发电量 ÷ 标准人均发电量）+（该国人均年钢产量 ÷ 标准人均钢产量）；得分 ≥ 2 视为达到该阶段的标准。",
    "2. 阶段标准（标准人均发电量 / 标准人均钢产量）：成熟工业化国家 4000 kWh / 400 kg；工业化中后期国家 3000 kWh / 300 kg；工业化中期国家 1000 kWh / 100 kg；工业化起步国家 500 kWh / 50 kg。",
    "3. 归类顺序：从高标准到低标准依次对照，以所能达到的最高阶段归类；四档均未达到者（起步档得分 < 2）列为准备工业化国家。本图按用户要求不设发达国家档，",
    "　　全部国家（含美、日、西欧等）一律按记分归类，仅体现工业积累程度的差异；中国按记分（起步档得分 3.13）归入工业化起步国家。",
    "4. 数据来源：人口 = 联合国 WPP2024（1995年历史值，全球 57.59 亿）；发电量 = 美国能源信息署（EIA）《International Energy Annual 2005》表6.3 净发电量 1995年；",
    "　　粗钢产量 = 世界钢铁协会《Steel Statistical Yearbook 2003》1995年（未列入其国别表者按无产量计）。",
    "5. 口径差异：1995年发电量为 EIA 净发电量；2024年图为 Ember/OWID 毛发电量（两者相差约5%）。若1995年改用 OWID 毛发电量口径，伊朗、乌克兰、南非、以色列4国将上调一档。",
]
for t in lines:
    fig.text(0.03, y, t, fontsize=10.6, color="#333333")
    y -= 0.021

g = {}
for r in fin.values():
    g.setdefault(r["category"], []).append(float(r["pop1995"]))
tot = sum(v for vs in g.values() for v in vs)
uncls = WORLD_POP - tot
rows = [(c, len(g[c]), sum(g[c])) for c in ORDER]

y -= 0.004
fig.text(0.03, y, "各阶段人口（1995年）", fontsize=15, weight="bold")
y -= 0.028
cols = [0.045, 0.30, 0.42, 0.55]
fig.text(cols[0], y, "类别", fontsize=11.5, weight="bold")
fig.text(cols[1], y, "国家数", fontsize=11.5, weight="bold")
fig.text(cols[2], y, "总人口", fontsize=11.5, weight="bold")
fig.text(cols[3], y, "占全球总人口比重", fontsize=11.5, weight="bold")
y -= 0.0235
for c, n, p in rows:
    fig.text(cols[0], y, c, fontsize=11.5, color=COLORS[c])
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
fig.text(cols[1], y, f"{len(fin)} 国分类", fontsize=11.5)
fig.text(cols[2], y, f"{WORLD_POP/1e8:.2f} 亿", fontsize=11.5, weight="bold")
fig.text(cols[3], y, "100.0%", fontsize=11.5, weight="bold")

y -= 0.021
notes = [
    "注：本图国家名单与2024年图一致（2024年人口≥1000万的95国 + 以色列），故1995年人口不足1000万的国家（如阿联酋、约旦、以色列）仍按记分着色，其余未分类国家以浅紫色显示；",
    "　　南苏丹1995年尚未独立（2011年独立），其电力与钢铁计入苏丹，本图按0计并列为准备工业化国家。多米尼加、危地马拉1995年粗钢产量按 USGS《Minerals Yearbook 1995》记为无产出/未报告，按0计。",
    "　　临界国家（得分2.0±0.2）：英国2.08、意大利2.19处于成熟档边界；乌克兰1.97、西班牙1.84处于中后期档边界；波兰2.16、南非1.97、以色列1.92、哈萨克斯坦1.86处于中后期档边界；",
    "　　乌兹别克斯坦2.12、阿塞拜疆2.11处于中期档边界；伊朗1.98处于中期档边界；叙利亚2.08、突尼斯1.94、阿尔及利亚1.85处于起步档边界。",
]
for t in notes:
    fig.text(0.03, y, t, fontsize=9.6, color="#666666")
    y -= 0.018

fig.savefig(os.path.join(OUT, "world_industrial_stage_map_1995.png"), facecolor="white")
print("saved out/world_industrial_stage_map_1995.png")
for c, n, p in rows:
    print(f"{c}\t{n}\t{p:,.0f}\t{p/WORLD_POP*100:.2f}%")
print(f"不足1000万\t-\t{uncls:,.0f}\t{uncls/WORLD_POP*100:.2f}%")
