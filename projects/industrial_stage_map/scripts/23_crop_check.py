# -*- coding: utf-8 -*-
"""放大检查关键区域着色。用法：python 23_crop_check.py [图片文件名] [输出前缀]"""
import os
import sys
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fname = sys.argv[1] if len(sys.argv) > 1 else "world_industrial_stage_map_v2.png"
prefix = sys.argv[2] if len(sys.argv) > 2 else "_crop"
img = Image.open(os.path.join(BASE, "out", fname))
W, H = img.size
print("size", W, H)

XL, XR, YT, YB = -180.0, 180.0, 84.0, -57.0
AX_X0, AX_W = 0.012, 0.976
AX_Y0, AX_H = 0.535, 0.425  # 与 22/32 绘图脚本的 axes 位置一致


def px(lon, lat):
    """经纬度 -> 图像像素(左上原点)。"""
    fx = (lon - XL) / (XR - XL)
    fy_from_top = (YT - lat) / (YT - YB)
    x_px = (AX_X0 + fx * AX_W) * W
    fig_y = AX_Y0 + (1 - fy_from_top) * AX_H
    y_px = (1 - fig_y) * H
    return x_px, y_px


def crop(name, lon, lat, span_lon, span_lat, scale=4):
    cx, cy = px(lon, lat)
    hw = span_lon / (XR - XL) * AX_W * W / 2  # span 以经/纬度为单位

    hh = span_lat / (YT - YB) * AX_H * H / 2
    box = (int(cx - hw), int(cy - hh), int(cx + hw), int(cy + hh))
    im = img.crop(box)
    im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
    p = os.path.join(BASE, "out", f"{prefix}_{name}.png")
    im.save(p)
    print(p, box)


crop("mideast", 37.0, 31.0, 22, 14)
crop("seasia", 108.0, 5.0, 40, 22)
crop("europe", 22.0, 51.0, 34, 18)
crop("southamerica", -65.0, -12.0, 40, 28)
crop("africa_south", 27.0, -14.0, 40, 26)
crop("southasia", 82.0, 26.0, 24, 16)
