# -*- coding: utf-8 -*-
"""放大核对1995年地图版面：图例/说明文字/统计表/注释 是否溢出或压字。"""
import os

from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "out")
SRC = os.path.join(OUT, "world_industrial_stage_map_1995.png")
im = Image.open(SRC)
W, H = im.size
print("size", W, H)

crops = {
    "crop_1995_legend.png": (0, int(H * 0.40), W, int(H * 0.53)),
    "crop_1995_text.png": (0, int(H * 0.52), W, int(H * 0.70)),
    "crop_1995_table.png": (0, int(H * 0.68), W, H),
    "crop_1995_left.png": (0, 0, int(W * 0.5), int(H * 0.45)),
}
for name, box in crops.items():
    im.crop(box).save(os.path.join(OUT, name))
    print("saved", name, box)
