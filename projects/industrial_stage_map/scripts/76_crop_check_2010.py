# -*- coding: utf-8 -*-
"""放大核对2010年地图版面：说明文字/统计表/注释是否溢出、裁切或压字。"""
import os

from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "out")
im = Image.open(os.path.join(OUT, "world_industrial_stage_map_2010.png"))
W, H = im.size
print("size", W, H)
crops = {
    "crop_2010_text.png": (0, int(H * 0.52), W, int(H * 0.70)),
    "crop_2010_table.png": (0, int(H * 0.68), W, H),
    "crop_2010_legend.png": (0, int(H * 0.40), W, int(H * 0.52)),
}
for name, box in crops.items():
    im.crop(box).save(os.path.join(OUT, name))
    print("saved", name, box)
