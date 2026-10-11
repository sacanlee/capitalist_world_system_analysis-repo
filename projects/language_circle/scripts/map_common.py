# -*- coding: utf-8 -*-
"""map_common.py — 地图公共层：NE底图 / 中国官方DataV图层 / 克什米尔争议区 /
克里米亚按中国官方地图口径改绘乌克兰 / 小国圆点饼图标注。
"""
import csv
import json
import os
import sys

from matplotlib.collections import PolyCollection
from matplotlib.patches import Circle, Wedge

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
RAW = os.path.join(BASE, "raw")
OUT = os.path.join(BASE, "out")
sys.path.insert(0, os.path.join(BASE, "scripts"))
from circles_def import COUNTRIES, GEO_CODE, UNCLASSIFIED  # noqa: E402

SKIP_GEO = {"ATA", "TWN", "CHN"}  # 南极不画; 台湾/中国用官方DataV图层
CRIMEA_PT = (34.1, 45.3)  # 克里米亚(辛菲罗波尔附近): 中国官方地图口径属乌克兰
DATA2GEO = {iso: GEO_CODE.get(iso, iso) for iso in COUNTRIES}
GEO2DATA = {v: k for k, v in DATA2GEO.items()}


def load_stats():
    stats = {}
    with open(os.path.join(DATA, "circle_stats.csv"), encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            stats[r["code"]] = r
    return stats


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


def point_in_ring(pt, ring):
    x, y = pt
    inside = False
    n = len(ring)
    for i in range(n):
        x1, y1 = ring[i][0], ring[i][1]
        x2, y2 = ring[(i + 1) % n][0], ring[(i + 1) % n][1]
        if (y1 > y) != (y2 > y):
            xin = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if xin > x:
                inside = not inside
    return inside


def load_ne():
    """NE底图: [(area, geo_code, polys)], 按面积降序"""
    with open(os.path.join(RAW, "ne_110m_countries.geojson"), encoding="utf-8") as f:
        gj = json.load(f)
    feats = []
    for ft in gj["features"]:
        code = ft["properties"].get("ADM0_A3")
        if code in SKIP_GEO or ft["geometry"] is None:
            continue
        geom = ft["geometry"]
        area = max(ring_area(p[0]) for p in polys_of(geom))
        feats.append((area, code, polys_of(geom)))
    feats.sort(key=lambda t: -t[0])
    return feats


def build_fill(feats, color_of_geo, crimea_color):
    """按 geo_code->颜色 生成 (polys, facecolors); 克里米亚用 crimea_color。
    color_of_geo: callable(geo_code) -> color str。"""
    polys, facecolors = [], []
    for area, code, ps in feats:
        c = color_of_geo(code)
        for p in ps:
            ring = [(x, y) for x, y in p[0]]
            col = crimea_color if (code == "RUS" and point_in_ring(CRIMEA_PT, p[0])) else c
            polys.append(ring)
            facecolors.append(col)
    return polys, facecolors


def load_china():
    with open(os.path.join(RAW, "china_datav_100000_full.json"), encoding="utf-8") as f:
        cd = json.load(f)
    china_polys, jd_polys = [], []
    for ft in cd["features"]:
        if ft["properties"]["adcode"] == "100000_JD":
            for poly in polys_of(ft["geometry"]):
                jd_polys.append([(x, y) for x, y in poly[0]])
        else:
            for poly in polys_of(ft["geometry"]):
                china_polys.append([(x, y) for x, y in poly[0]])
    return china_polys, jd_polys


def add_china(ax, china_polys, jd_polys, fill, edge="#a02020", jd_fill=None):
    ax.add_collection(PolyCollection(china_polys, facecolors=fill,
                                     edgecolors=edge, linewidths=0.35))
    jf = jd_fill or fill
    ax.add_collection(PolyCollection(jd_polys, facecolors=jf, edgecolors=jf, linewidths=0.3))


def load_kashmir():
    KASHMIR = {"Jammu and Kashmir", "Gilgit-Baltistan", "Azad Kashmir", "Siachen Glacier"}
    with open(os.path.join(RAW, "ne_10m_disputed.geojson"), encoding="utf-8") as f:
        dgj = json.load(f)
    polys = []
    for ft in dgj["features"]:
        if ft["properties"].get("BRK_NAME") in KASHMIR:
            geom = ft["geometry"]
            for poly in polys_of(geom):
                polys.append([(x, y) for x, y in poly[0]])
    return polys


def add_kashmir(ax, kash_polys, label=True, label_xy=(72.3, 31.2)):
    ax.add_collection(PolyCollection(kash_polys, facecolors=(1, 1, 1, 0.35),
                                     edgecolors="#555555", linewidths=0.5,
                                     linestyles=(0, (4, 3)), hatch="////"))
    if label:
        ax.text(label_xy[0], label_xy[1], "克什米尔\nKashmir", fontsize=7.2, color="#333333",
                ha="center", va="center", zorder=5, linespacing=1.3,
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.7, pad=0.6))


def add_hatch(ax, feats, geo_codes, color):
    """对指定geo_code国家叠加斜纹"""
    flat = []
    for area, code, ps in feats:
        if code in geo_codes:
            for poly in ps:
                flat.append([(x, y) for x, y in poly[0]])
    ax.add_collection(PolyCollection(flat, facecolors="none", edgecolors=color,
                                     linewidths=0.45, hatch="////"))


def add_marker(ax, lon, lat, kind, colors, num=None, num_xy=None):
    if kind == "pie":
        n = len(colors)
        for i, col in enumerate(colors):
            ax.add_patch(Wedge((lon, lat), 2.0, 90 - 360 * (i + 1) / n, 90 - 360 * i / n,
                               facecolor=col, edgecolor="white", linewidth=0.7, zorder=6))
    else:
        ax.add_patch(Circle((lon, lat), 1.1, facecolor=colors[0], edgecolor="#333333",
                            linewidth=0.7, zorder=6))
    if num:
        ax.text(num_xy[0], num_xy[1], num, fontsize=11, color="#111111",
                ha="center", va="center", zorder=7,
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.55, pad=0.4))


def setup_world_ax(ax):
    ax.set_xlim(-180, 180)
    ax.set_ylim(-57, 86)
    ax.set_aspect("auto")
    ax.axis("off")
