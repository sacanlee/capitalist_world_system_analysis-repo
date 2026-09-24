# -*- coding: utf-8 -*-
"""生成 out/工业化阶段清单_2055.md（各类国家清单 + 晋级名单 + 人口汇总）"""
import csv
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "out")
WORLD55 = 9846237566.0

ORDER = ["后工业化国家", "成熟工业化国家", "工业化中后期国家", "工业化中期国家",
         "工业化起步国家", "准备工业化国家"]

with open(os.path.join(BASE, "raw", "ne_110m_countries.geojson"), encoding="utf-8") as f:
    gj = json.load(f)
ZH = {ft["properties"].get("ADM0_A3"): ft["properties"].get("NAME_ZH")
      for ft in gj["features"] if ft["properties"].get("NAME_ZH")}
ZH["SDS"] = ZH.get("SSD")
ZH.update({"ISR": "以色列", "TWN": "台湾", "CHN": "中国大陆"})

with open(os.path.join(DATA, "final_2055.csv"), encoding="utf-8-sig") as f:
    d55 = list(csv.DictReader(f))


def zh(r):
    return ZH.get(r["code"]) or r["entity"]


L = ["# 全球工业化阶段清单（2055年推演）", "",
     "推演方法：以 2040 年推演为基础，按经济发展趋势对部分国家作阶段调整；未提及的国家保持 2040 年等级。",
     "人口 = 联合国 WPP2024 中等生育率情景 2055 年（全球 9,846,237,566）；",
     "阶段标准与 2024/2040 年版相同（成熟 4000/400、中后期 3000/300、中期 1000/100、起步 500/50，得分以2024年人均发电量/钢产量计算）。", "",
     "对应地图：`out/world_industrial_stage_map_2055.png`　｜　另见：`out/工业化阶段清单_2040.md`、`out/工业化阶段清单_2024.md`", "",
     "## 一、晋级名单（相对2040年）", ""]
PROMO = [("晋级发达国家", "俄罗斯、土耳其（2030-2055年间晋级；其余国家保持2040年等级）"),
         ("晋级成熟工业化国家", "印度、印度尼西亚、墨西哥、伊拉克、南非、泰国、阿根廷"),
         ("晋级工业化中后期国家", "埃及、阿塞拜疆、阿尔及利亚、摩洛哥、委内瑞拉、突尼斯、乌兹别克斯坦、"
                          "塔吉克斯坦、菲律宾、约旦（多米尼加、哥伦比亚、秘鲁、厄瓜多尔仍为工业化中期国家）"),
         ("晋级工业化中期国家", "巴基斯坦、尼日利亚、孟加拉国、肯尼亚、坦桑尼亚、乌干达、安哥拉、莫桑比克、科特迪瓦、加纳、"
                         "赞比亚、塞内加尔、津巴布韦、缅甸、叙利亚、尼泊尔、柬埔寨、朝鲜、斯里兰卡、危地马拉、几内亚、"
                         "卢旺达、玻利维亚、洪都拉斯、古巴、纳米比亚、博茨瓦纳、埃塞俄比亚"),
         ("晋级工业化起步国家", "刚果民主共和国、苏丹、喀麦隆、马达加斯加、贝宁、马里、布基纳法索、海地、"
                         "巴布亚新几内亚、阿富汗、南苏丹、尼日尔、乍得、马拉维、布隆迪、索马里、也门")]
for a, b in PROMO:
    L.append(f"- **{a}**：{b}")
L += ["", "## 二、各类国家清单（2055年）", ""]
tot = 0.0
for c in ORDER:
    sub = sorted([r for r in d55 if r["cat2055"] == c], key=lambda x: -float(x["pop2055"]))
    p = sum(float(r["pop2055"]) for r in sub)
    tot += p
    if not sub:
        L += [f"### {c}（0 国）", "", "（2055年无处于该阶段的国家）", ""]
        continue
    L += [f"### {c}（{len(sub)} 国，{p/1e8:.2f} 亿，占全球 {p/WORLD55*100:.2f}%）", "",
          "| 国家 | 2055年人口(万人) | 2040年类别 | 变化 |", "|---|---:|---|---|"]
    for r in sub:
        c40 = r["cat2040"]
        chg = "保持" if c40 == c else f"{c40} → {c}"
        L.append(f"| {zh(r)} | {float(r['pop2055'])/1e4:,.0f} | {c40} | {chg} |")
    L.append("")
uncls = WORLD55 - tot
L += ["## 三、人口汇总", "",
      "| 类别 | 国家数 | 总人口 | 占全球总人口比重 |", "|---|---:|---:|---:|"]
for c in ORDER:
    sub = [r for r in d55 if r["cat2055"] == c]
    p = sum(float(r["pop2055"]) for r in sub)
    L.append(f"| {c} | {len(sub)} | {p/1e8:.2f} 亿 | {p/WORLD55*100:.1f}% |")
L += [f"| 其他人口不足1000万国家 | — | {uncls/1e8:.2f} 亿 | {uncls/WORLD55*100:.1f}% |",
      f"| **全球合计** | **{len(d55)}** | **{WORLD55/1e8:.2f} 亿** | **100.0%** |", "",
      "注明：俄罗斯、土耳其晋级发达国家，其余发达国家保持 2040 年等级；",
      "2055 年已无处于准备工业化阶段的国家（也门晋级工业化起步国家，故准备工业化一栏为 0 国）；",
      "跨两档晋级：印度尼西亚、阿根廷（工业化中期→成熟工业化国家）、埃塞俄比亚（准备工业化→工业化中期国家）。"]
with open(os.path.join(OUT, "工业化阶段清单_2055.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L))
print("saved out/工业化阶段清单_2055.md", len(L))
