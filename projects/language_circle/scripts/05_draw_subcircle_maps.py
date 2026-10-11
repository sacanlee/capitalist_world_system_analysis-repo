# -*- coding: utf-8 -*-
"""05_draw_subcircle_maps.py — 含子圈的大圈各一张子圈分布图（英语/罗曼/俄语）
- 子圈按专属色系着色; 非本圈国家灰色
- 中国官方边界/克里米亚/克什米尔与总图一致
- 表：各子圈 2025/2055 人口(亿)、占本圈、占全球、2025出生(万)
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
from circles_def import SUBS, COUNTRIES, MARKERS
import map_common as mc

plt.rcParams["font.family"] = ["Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["hatch.linewidth"] = 1.0

stats = mc.load_stats()
feats = mc.load_ne()
china_polys, jd_polys = mc.load_china()
kash_polys = mc.load_kashmir()

NONMEMBER = "#e4e4e4"


def members_of(sub):
    return [i for i in COUNTRIES if sub in COUNTRIES[i][2] and i != "CYN"]


def draw_map(top_cn, top_en, top_code, subcodes, palette, filename,
             marker_specs, sub_notes, extra_desc):
    sub2color = dict(zip(subcodes, palette))
    geo2sub = {}
    for sub in subcodes:
        for iso in members_of(sub):
            geo2sub[mc.DATA2GEO[iso]] = sub

    def color_of_geo(code):
        sub = geo2sub.get(code)
        if sub is None or mc.GEO2DATA.get(code) in MARKERS:
            return NONMEMBER
        return sub2color[sub]

    ukr_color = color_of_geo("UKR")
    polys, facecolors = mc.build_fill(feats, color_of_geo, ukr_color)

    fig = plt.figure(figsize=(16.5, 11.5), dpi=130)
    ax = fig.add_axes([0.010, 0.545, 0.980, 0.385])
    ax.add_collection(PolyCollection(polys, facecolors=facecolors,
                                     edgecolors="white", linewidths=0.4))
    mc.add_china(ax, china_polys, jd_polys, NONMEMBER, edge="#b9b9b9", jd_fill="#7a7a7a")
    mc.add_kashmir(ax, kash_polys)
    for mk in marker_specs:
        mc.add_marker(ax, mk["lon"], mk["lat"], mk["kind"], mk["colors"], mk["num"], mk["num_xy"])
    mc.setup_world_ax(ax)
    ax.set_title(f"{top_cn}子圈分布（2025 / 2055 年人口）\n"
                 f"Sub-spheres of the {top_en} (Population 2025 / 2055)",
                 fontsize=18.5, pad=9, linespacing=1.6)

    handles = [Patch(facecolor=sub2color[s], edgecolor="#888888",
                     label=f"{SUBS[s][0]}  {SUBS[s][1]}") for s in subcodes]
    handles.append(Patch(facecolor=NONMEMBER, edgecolor="#aaaaaa",
                         label="非本圈国家·地区 Not in this sphere"))
    if marker_specs:
        handles.append(Line2D([], [], marker="o", color="none", markerfacecolor="#999999",
                              markeredgecolor="#333333", markersize=9,
                              label="圆点＝小国 Small states"))
    leg = fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.545),
                     ncol=min(len(handles), 3), frameon=False, fontsize=11.5,
                     handlelength=1.5, handleheight=1.05, columnspacing=2.0, labelspacing=0.45)
    for t in leg.get_texts():
        t.set_color("#222222")

    fig.text(0.5, 0.452,
             "中国边界按中国官方标准地图（含台湾省、藏南地区、南海诸岛及断续线；克里米亚口径属乌克兰） · 数据：联合国WPP2024中方案\n"
             "China's boundary per official standard map · Crimea as Ukraine per China's official map · Source: UN WPP2024 Medium",
             ha="center", va="top", fontsize=10.8, color="#444444", linespacing=1.55)

    # ---------- 表 ----------
    t = stats[top_code]
    tot = {k: float(t[k]) for k in ("pop2025", "pop2055", "births2025")}
    hdr = ["子圈 Sub-sphere", "国家数 N", "2025人口/亿 Pop", "占本圈", "占全球",
           "2025出生/万 Births", "占本圈", "2055人口/亿 Pop", "占本圈", "占全球"]
    cx = [0.030, 0.345, 0.462, 0.530, 0.600, 0.700, 0.765, 0.878, 0.943, 0.999]
    y = 0.396
    fig.text(0.030, y, "各子圈人口（联合国WPP2024中方案）  Population by Sub-sphere (UN WPP2024 Medium)",
             fontsize=13.5, weight="bold")
    y -= 0.0285
    for i, h in enumerate(hdr):
        fig.text(cx[i], y, h, fontsize=10.8, weight="bold", ha="left" if i == 0 else "right")
    y -= 0.0265
    SHORT_SUB = {"RO": ("罗曼语圈其他（意/罗/阿）", "Romance Others (It/Ro/Al)")}
    for sub in subcodes:
        r = stats[sub]
        cn, en = SHORT_SUB.get(sub, (r["name_cn"], r["name_en"]))
        p25, p55, b25 = float(r["pop2025"]), float(r["pop2055"]), float(r["births2025"])
        fig.text(cx[0], y, f"· {cn}  {en}", fontsize=11, color=sub2color[sub])
        vals = [r["n"], f"{p25/1e5:,.2f}", f"{p25/tot['pop2025']*100:.1f}%", f"{float(r['share2025']):.1f}%",
                f"{b25/10:,.0f}", f"{b25/tot['births2025']*100:.1f}%",
                f"{p55/1e5:,.2f}", f"{p55/tot['pop2055']*100:.1f}%", f"{float(r['share2055']):.1f}%"]
        for i, v in enumerate(vals):
            fig.text(cx[i + 1], y, v, fontsize=11, ha="right")
        y -= 0.0265
    fig.text(cx[0], y, f"{top_cn}合计  {top_en} (total)", fontsize=11.5, weight="bold")
    vals = [t["n"], f"{tot['pop2025']/1e5:,.2f}", "100%", f"{float(t['share2025']):.1f}%",
            f"{tot['births2025']/10:,.0f}", "100%",
            f"{tot['pop2055']/1e5:,.2f}", "100%", f"{float(t['share2055']):.1f}%"]
    for i, v in enumerate(vals):
        fig.text(cx[i + 1], y, v, fontsize=11.5, ha="right", weight="bold")
    y -= 0.032
    fig.text(cx[0], y, "单位：1亿=100 million；出生＝万人（10k）；占全球＝占全球总人口/总出生比重。",
             fontsize=9, color="#666666")

    # ---------- 子圈说明+注释 ----------
    y -= 0.030
    fig.text(cx[0], y, "子圈说明  Sub-sphere notes", fontsize=12.5, weight="bold")
    y -= 0.023
    for line in sub_notes:
        fig.text(cx[0], y, line, fontsize=10, color="#333333")
        y -= 0.0195
    y -= 0.006
    for line in extra_desc:
        fig.text(cx[0], y, line, fontsize=9.6, color="#555555")
        y -= 0.018
    fig.text(cx[0], y - 0.004,
             "注：中国人口含港澳台地区；克什米尔按中国官方地图口径为印巴争议地区（斜纹）；克里米亚按中国官方地图口径属乌克兰。"
             "数据：联合国《世界人口展望2024》中方案，出生为2025年，2055年为预测值。",
             fontsize=9.2, color="#666666")
    fig.text(cx[0], y - 0.024,
             "Notes: China incl. HK/Macao/Taiwan; Kashmir = disputed area and Crimea = Ukraine per China's official map. "
             "Source: UN WPP2024 Medium variant.",
             fontsize=8.8, color="#777777")

    fig.savefig(os.path.join(mc.OUT, filename), facecolor="white")
    print("saved out/" + filename)


# ================= 英语圈 =================
draw_map(
    "英语文化圈", "English Sphere", "E",
    ["E1", "E2", "E3", "E4"], ["#08519c", "#4292c6", "#9ecae1", "#c6dbef"],
    "language_circles_english_subspheres.png",
    marker_specs=[
        {"lon": 103.82, "lat": 1.35, "kind": "dot", "colors": ["#08519c"],
         "num": "①", "num_xy": (105.5, 0.6)},
        {"lon": 43.32, "lat": -11.65, "kind": "dot", "colors": ["#9ecae1"],
         "num": "②", "num_xy": (45.3, -14.2)},
    ],
    sub_notes=[
        "· 纯英语子圈（含日耳曼语国家，含以色列）：国内或区域内以英语为通用语（①新加坡亦属汉语圈/印尼-马来语圈）。",
        "· 英语+印度-雅利安语（南亚）子圈：区域内英语和印地语双语互通，孟加拉语与印地语亲缘关系近，600小时内可完成学习、半年内可融入，近似于普通话和广东话的差异。",
        "· 英语+斯瓦西里语子圈：区域内英语和斯瓦西里语双语互通（②科摩罗亦属阿拉伯语圈）。",
        "· 英语-其他子圈：英语普及率不高，但基础教育全面加强英语，且与区域内其他国家用英语作为通用语（埃塞俄比亚、南苏丹、越南；越南同属汉语文化圈）。",
    ],
    extra_desc=[
        "注：多圈国家在本图中按其英语子圈归属着色（美国=纯英语，且同属罗曼语圈-西语子圈；越南=英语-其他，且同属汉语文化圈；加拿大=纯英语；新加坡、科摩罗见① ②）。",
    ],
)

# ================= 罗曼语圈 =================
draw_map(
    "罗曼语文化圈", "Romance Sphere", "R",
    ["RF1", "RF2", "RS", "RP", "RO"], ["#ff7f00", "#fdbf6f", "#e31a1c", "#33a54a", "#cab2d6"],
    "language_circles_romance_subspheres.png",
    marker_specs=[
        {"lon": -23.60, "lat": 15.12, "kind": "dot", "colors": ["#33a54a"],
         "num": "④", "num_xy": (-21.5, 13.5)},
        {"lon": 6.65, "lat": 0.33, "kind": "dot", "colors": ["#33a54a"],
         "num": "⑤", "num_xy": (8.6, -1.2)},
    ],
    sub_notes=[
        "· 纯法语圈：法语地位稳固，为国内通用语；泛法语圈：法语地位动摇但仍是重要语言，区域交流仍会使用。",
        "· 西语圈：西班牙语通行区域；葡语圈：葡萄牙语通行区域（④佛得角 ⑤圣多美和普林西比）。",
        "· 罗曼语圈其他：意大利、罗马尼亚、阿尔巴尼亚。罗曼语各语言亲缘关系近，600小时内可完成学习、半年内可融入，近似于普通话和广东话的差异。",
    ],
    extra_desc=[
        "注：多圈国家在本图中按其罗曼语归属着色（美国=西语圈，且同属英语圈-纯英语子圈；加拿大=纯法语圈；阿尔及利亚、摩洛哥、突尼斯、毛里塔尼亚、乍得、吉布提=泛法语圈，且同属阿拉伯语圈）。",
    ],
)

# ================= 俄语圈 =================
draw_map(
    "俄语文化圈", "Russian Sphere", "RU",
    ["RU1", "RU2"], ["#54278f", "#bcbddc"],
    "language_circles_russian_subspheres.png",
    marker_specs=[],
    sub_notes=[
        "· 纯俄语圈：俄语地位稳固，为国内基础教育语言（吉尔吉斯斯坦同属突厥语圈，塔吉克斯坦同属波斯语圈）。",
        "· 泛俄语圈：俄语地位动摇但仍有很多人会说，同时作为区域内的通用语（哈萨克斯坦、乌兹别克斯坦同属突厥语圈）。",
    ],
    extra_desc=[
        "注：多圈国家在本图中按其俄语子圈归属着色；克里米亚按中国官方地图口径属乌克兰（泛俄语圈浅紫）。",
    ],
)
