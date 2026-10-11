# -*- coding: utf-8 -*-
"""03_draw_map.py — 总图：大圈层级世界地图（中英双语）
- 8大圈纯色着色（子圈差异见 05 子圈图）; 多圈国家斜纹; 小国圆点/饼图①-⑤
- 中国按官方标准地图: DataV省界(含台湾省/藏南) + 南海断续线; 克里米亚=乌克兰; 克什米尔争议区
- 数据：2025 / 2055 人口 + 2025 出生
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts"))
from circles_def import (TOPS, SUBS, COUNTRIES, COLORS, UNCLASSIFIED, DRAW, MARKERS)
import map_common as mc

plt.rcParams["font.family"] = ["Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["hatch.linewidth"] = 1.0

stats = mc.load_stats()
feats = mc.load_ne()
china_polys, jd_polys = mc.load_china()
kash_polys = mc.load_kashmir()


def top_of(iso):
    subs = COUNTRIES[iso][2]
    return SUBS[subs[0]][2]


def color_of_geo(code):
    iso = mc.GEO2DATA.get(code)
    if iso is None or iso in MARKERS:
        return UNCLASSIFIED
    if iso in DRAW:
        return COLORS[DRAW[iso][0]]
    return COLORS[top_of(iso)]


# 克里米亚: 属乌克兰(中国官方地图口径) → 与本图上乌克兰同色
ukr_color = color_of_geo(mc.DATA2GEO["UKR"])
polys, facecolors = mc.build_fill(feats, color_of_geo, ukr_color)

fig = plt.figure(figsize=(17, 14), dpi=130)
ax = fig.add_axes([0.010, 0.555, 0.980, 0.375])
ax.add_collection(PolyCollection(polys, facecolors=facecolors, edgecolors="white", linewidths=0.4))

mc.add_china(ax, china_polys, jd_polys, COLORS["C"], jd_fill="#a50f15")
mc.add_kashmir(ax, kash_polys)

# 多圈国家斜纹(次级大圈)
for iso, (base, stripe_top, shade) in DRAW.items():
    mc.add_hatch(ax, feats, {mc.DATA2GEO[iso]}, COLORS[stripe_top])

# 小国标注(圆点/饼图+编号)
MARK_NUM = {"SGP": ("①", (105.5, 0.6)), "COM": ("②", (45.3, -14.2)),
            "BHR": ("③", (53.2, 28.6)), "CPV": ("④", (-21.5, 13.5)),
            "STP": ("⑤", (8.6, -1.2))}
for iso, mk in MARKERS.items():
    cols = [COLORS[SUBS[s][2]] for s in mk["subs"]]
    num, num_xy = MARK_NUM[iso]
    mc.add_marker(ax, mk["lon"], mk["lat"], mk["kind"], cols, num, num_xy)

mc.setup_world_ax(ax)
ax.set_title("世界语言文化圈地图·大圈层级（2025 / 2055 年人口）\n"
             "World Map of Language & Cultural Spheres (Top-level; Population 2025 / 2055)",
             fontsize=19, pad=9, linespacing=1.6)

# ---------- 图例 ----------
handles = [Patch(facecolor=COLORS[t], edgecolor="#888888", label=f"{TOPS[t][0]} {TOPS[t][1]}")
           for t in TOPS]
handles += [
    Patch(facecolor="#ffffff", edgecolor="#444444", hatch="////",
          label="斜纹＝次级大圈 2nd sphere"),
    Line2D([], [], marker="o", color="none", markerfacecolor="#999999",
           markeredgecolor="#333333", markersize=9, label="圆点/饼图＝小国(①-⑤) Small states"),
    Patch(facecolor="#ccdcef", edgecolor="#555555", hatch="////", linestyle="--",
          label="克什米尔＝印巴争议区 Disputed"),
    Patch(facecolor=UNCLASSIFIED, edgecolor="#888888", label="未列入清单 Not listed"),
]
leg = fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.556), ncol=4,
                 frameon=False, fontsize=12, handlelength=1.5, handleheight=1.05,
                 columnspacing=2.2, labelspacing=0.45)
for t in leg.get_texts():
    t.set_color("#222222")

fig.text(0.5, 0.462,
         "中国边界按中国官方标准地图（含台湾省、藏南地区、南海诸岛及断续线） · 数据：联合国WPP2024中方案\n"
         "China's boundary per official standard map (incl. Taiwan Province, South Tibet, South China Sea Islands) · Source: UN WPP2024 Medium",
         ha="center", va="top", fontsize=11.5, color="#444444", linespacing=1.55)

# ---------- 汇总表(2025/2055) ----------
TABLE_ORDER = list(TOPS) + ["ALL", "REST"]
cols = [0.035, 0.235, 0.358, 0.455, 0.585, 0.682, 0.808, 0.905]
hdr = ["文化圈 Sphere", "国家数 N", "2025人口 Pop", "占比 Share", "2055人口 Pop",
       "占比 Share", "2025出生 Births", "占比 Share"]
y0 = 0.418
fig.text(0.035, y0, "各大圈人口与出生（联合国WPP2024中方案）  Population & Births by Sphere (UN WPP2024 Medium)",
         fontsize=14.5, weight="bold")
y = y0 - 0.027
for i, h in enumerate(hdr):
    fig.text(cols[i], y, h, fontsize=11.5, weight="bold")
y -= 0.0225

TCOLOR = {**{t: COLORS[t] for t in TOPS}, "ALL": "#333333", "REST": "#777777"}
for code in TABLE_ORDER:
    r = stats[code]
    name = r["name_cn"]
    if code == "REST":
        name = "未列入清单国家·地区（递余）"
    if code == "ALL":
        name = "8大圈合计（去重）"
    fig.text(cols[0], y, name, fontsize=11.5, color=TCOLOR[code],
             weight="bold" if code in TOPS else "normal")
    fig.text(cols[1], y, r["n"] if r["n"] else "—", fontsize=11.5)
    fig.text(cols[2], y, f"{float(r['pop2025'])/1e5:,.2f} 亿", fontsize=11.5)
    fig.text(cols[3], y, f"{float(r['share2025']):.1f}%", fontsize=11.5)
    fig.text(cols[4], y, f"{float(r['pop2055'])/1e5:,.2f} 亿", fontsize=11.5)
    fig.text(cols[5], y, f"{float(r['share2055']):.1f}%", fontsize=11.5)
    fig.text(cols[6], y, f"{float(r['births2025'])/10:,.0f} 万", fontsize=11.5)
    fig.text(cols[7], y, f"{float(r['bshare2025']):.1f}%", fontsize=11.5)
    y -= 0.0198

fig.text(cols[0], y, "全球总计 World", fontsize=11.5, weight="bold")
fig.text(cols[1], y, "237", fontsize=11.5, weight="bold")
fig.text(cols[2], y, "82.32 亿", fontsize=11.5, weight="bold")
fig.text(cols[3], y, "100%", fontsize=11.5)
fig.text(cols[4], y, "98.46 亿", fontsize=11.5, weight="bold")
fig.text(cols[5], y, "100%", fontsize=11.5)
fig.text(cols[6], y, "13,240 万", fontsize=11.5, weight="bold")
fig.text(cols[7], y, "100%", fontsize=11.5)
y -= 0.019
fig.text(cols[0], y, "单位：1亿 = 100 million；出生＝万人（10k）。", fontsize=9, color="#666666")

# ---------- 注释 ----------
y -= 0.0215
alln = stats["ALL"]["n"]
alls = float(stats["ALL"]["share2025"])
notes = [
    ("注：1. 本图为大圈层级（8大圈纯色）；含子圈的大圈（英语4子圈、罗曼5子圈、俄语2子圈）另附子圈分布图。中国人口含香港、澳门、台湾地区（2025年合计14.47亿）；", 0),
    ("　　　　中国边界按中国官方标准地图绘制（台湾省、藏南地区、阿克赛钦、喀喇昆仑走廊、南海诸岛及其断续线均属中国）；克里米亚按中国官方地图口径属乌克兰；克什米尔按官方口径为印巴争议地区（斜纹标示）。", 0),
    ("　　2. 多圈国家（美国、加拿大、越南、新加坡、马来西亚、科摩罗、阿尔及利亚、摩洛哥、突尼斯、毛里塔尼亚、乍得、吉布提、塔吉克斯坦、", 0),
    (f"　　　　吉尔吉斯斯坦、哈萨克斯坦、乌兹别克斯坦，及仅图示的北塞浦路斯）底色为主大圈、斜纹为次大圈；各圈之和大于全球总计；8大圈覆盖{alln}国·地区，2025年占全球人口{alls:.1f}%。", 0),
    ("　　3. 小国标注（图中数字）：① 新加坡（英/汉/马来三圈交汇）② 科摩罗（英语-斯瓦西里/阿语两圈）③ 巴林（阿语圈）④ 佛得角 ⑤ 圣多美和普林西比；北塞浦路斯（突厥语圈）无联合国单列人口数据，仅地图标注、未计入统计。", 0),
    ("　　4. 未列入清单的国家·地区以灰色显示（如瑞士、泰国、波兰、斯里兰卡、蒙古、格鲁吉亚、亚美尼亚、塞尔维亚等）。", 0),
    ("　　5. 数据来源：联合国《世界人口展望2024》中方案（Medium），出生为2025年；2055年为联合国预测值。", 0),
    ("Notes: Multi-sphere countries are counted in every sphere (sums exceed 100%). Small states in numbers ①Singapore ②Comoros ③Bahrain ④Cabo Verde ⑤São Tomé. Kashmir = India-Pakistan disputed area; Crimea = Ukraine, per China's official map. Source: UN WPP2024 Medium.", 1),
]
for t, en in notes:
    fig.text(0.035, y, t, fontsize=9.8 if not en else 9.2,
             color="#333333" if not en else "#666666")
    y -= 0.0168 if not en else 0.0155

fig.savefig(os.path.join(mc.OUT, "world_language_circles_map.png"), facecolor="white")
print("saved out/world_language_circles_map.png")
