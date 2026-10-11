# -*- coding: utf-8 -*-
"""crop_check.py — 地图局部放大检查（坐标换算: fig 17x14@130dpi=2210x1820,
ax=[0.010,0.555,0.980,0.375], xlim 360, ylim -57..86)"""
import os
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img = Image.open(os.path.join(BASE, "out", "world_language_circles_map.png"))
W, H = img.size  # 2210x1820
x0, x1 = 0.010 * W, 0.990 * W
yb, yt = (1 - 0.555) * H, (1 - 0.555 - 0.375) * H


def crop(name, lon0, lon1, lat0, lat1, scale=2):
    px0 = x0 + (lon0 + 180) / 360 * (x1 - x0)
    px1 = x0 + (lon1 + 180) / 360 * (x1 - x0)
    py0 = yb - (lat1 + 57) / 143 * (yb - yt)
    py1 = yb - (lat0 + 57) / 143 * (yb - yt)
    box = (int(px0), int(py0), int(px1), int(py1))
    c = img.crop(box)
    c = c.resize((c.width * scale, c.height * scale), Image.LANCZOS)
    out = os.path.join(BASE, "out", f"crop_{name}.png")
    c.save(out)
    print(out, box, c.size)


crop("east_asia", 88, 135, -2, 45, 2)
crop("north_africa", -18, 40, 8, 40, 2)
crop("north_america", -142, -50, 38, 76, 2)
crop("southeast_asia", 88, 118, -22, 22, 2)
crop("legend_area", -180, 180, 100, 101, 1)
