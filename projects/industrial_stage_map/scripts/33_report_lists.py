# -*- coding: utf-8 -*-
"""生成清单md：out/工业化阶段清单_2024.md 与 out/工业化阶段清单_2040.md
（各类国家清单 + 进入该类别的相关指标数值）"""
import csv
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "out")
WORLD24 = 8161972574.0
WORLD40 = 9177190200.0

ORDER24 = ["后工业化国家", "成熟工业化国家", "工业化中后期国家", "工业化中期国家",
           "工业化起步国家", "准备工业化国家"]
ORDER40 = ["后工业化国家", "成熟工业化国家", "工业化中后期国家", "工业化中期国家",
           "工业化起步国家", "准备工业化国家"]

with open(os.path.join(BASE, "raw", "ne_110m_countries.geojson"), encoding="utf-8") as f:
    gj = json.load(f)
ZH = {ft["properties"].get("ADM0_A3"): ft["properties"].get("NAME_ZH")
      for ft in gj["features"] if ft["properties"].get("NAME_ZH")}
ZH["SDS"] = ZH.get("SSD")
ZH.update({"ISR": "以色列", "TWN": "台湾", "CHN": "中国大陆"})

with open(os.path.join(DATA, "final_v2.csv"), encoding="utf-8-sig") as f:
    d24 = list(csv.DictReader(f))
with open(os.path.join(DATA, "final_2040.csv"), encoding="utf-8-sig") as f:
    d40 = list(csv.DictReader(f))


def zh(r):
    return ZH.get(r["code"]) or r["entity"]


# ============ 2024 ============
L = ["# 全球工业化阶段清单（2024年）", "",
     "数据口径：人口 = 联合国 WPP2024（2024年）；人均发电量 = Ember（OWID 整理）2024年，乌克兰为 EIA 2024年；",
     "人均钢产量 = 世界钢铁协会 2024年（未列国用 BGS《World Mineral Production 2020-2024》）。",
     "全球总人口 8,161,972,574（UN WPP2024）。", "",
     "**记分方法**：得分 =（人均年发电量 ÷ 标准人均发电量）+（人均年钢产量 ÷ 标准人均钢产量），得分 > 2 视为达到该阶段标准。", "",
     "**阶段标准**（标准人均发电量 / 标准人均钢产量）：",
     "成熟工业化国家 4000 kWh / 400 kg；工业化中后期国家 3000 kWh / 300 kg；工业化中期国家 1000 kWh / 100 kg；工业化起步国家 500 kWh / 50 kg。", "",
     "**归类顺序**：发达国家（IMF 发达经济体口径）默认列为后工业化国家（以色列、中国台湾地区按此列入）；",
     "其余国家从高标准到低标准依次对照，达到的最高阶段即为其类别；四档均未达到者列为准备工业化国家。",
     "中国按记分归入成熟工业化国家（成熟档得分 3.55 > 2）。", "",
     "## 一、各类国家清单与指标", ""]
tot = 0.0
for c in ORDER24:
    sub = sorted([r for r in d24 if r["category"] == c], key=lambda x: -float(x["pop2024"]))
    p = sum(float(r["pop2024"]) for r in sub)
    tot += p
    L += [f"### {c}（{len(sub)} 国，{p/1e8:.2f} 亿，占全球 {p/WORLD24*100:.2f}%）", "",
          "| 国家 | 人口(万人) | 人均发电量(kWh) | 人均钢产量(kg) | 成熟档得分 | 中后期档得分 | 中期档得分 | 起步档得分 | 归类依据 |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in sub:
        if r["code"] == "CHN":
            why = "记分达标（成熟档得分 3.55 > 2）"
        elif r["code"] == "TWN":
            why = "发达国家（IMF口径）默认列入（中国台湾地区）"
        elif c == "后工业化国家":
            why = "发达国家（IMF口径）默认列入"
        else:
            key = {"成熟工业化国家": "s_mature", "工业化中后期国家": "s_late",
                   "工业化中期国家": "s_mid", "工业化起步国家": "s_start",
                   "准备工业化国家": "s_start"}[c]
            if c == "准备工业化国家":
                why = f"各档均未达标（起步档得分 {float(r['s_start']):.2f} ≤ 2）"
            else:
                why = f"达标（{float(r[key]):.2f} > 2）"
        L.append(f"| {zh(r)} | {float(r['pop2024'])/1e4:,.0f} | {float(r['pc_elec_kwh']):,.0f} | "
                 f"{float(r['pc_steel_kg']):,.1f} | {float(r['s_mature']):.2f} | {float(r['s_late']):.2f} | "
                 f"{float(r['s_mid']):.2f} | {float(r['s_start']):.2f} | {why} |")
    L.append("")

uncls = WORLD24 - tot
L += ["## 二、人口汇总", "",
      "| 类别 | 国家数 | 总人口 | 占全球总人口比重 |", "|---|---:|---:|---:|"]
for c in ORDER24:
    sub = [r for r in d24 if r["category"] == c]
    p = sum(float(r["pop2024"]) for r in sub)
    L.append(f"| {c} | {len(sub)} | {p/1e8:.2f} 亿 | {p/WORLD24*100:.1f}% |")
L += [f"| 其他人口不足1000万国家 | — | {uncls/1e8:.2f} 亿 | {uncls/WORLD24*100:.1f}% |",
      f"| **全球合计** | **{len(d24)}** | **{WORLD24/1e8:.2f} 亿** | **100.0%** |", "",
      "注明：以色列（UN WPP2024 人口 938.7 万）按发达国家列入后工业化国家；其余人口不足1000万的国家未参与分类。", "",
      "对应地图：`out/world_industrial_stage_map_v2.png`　｜　报告：`out/report_v2.md`　｜　"
      "另见：`out/工业化阶段清单_2040.md`（2040年推演）"]
with open(os.path.join(OUT, "工业化阶段清单_2024.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L))
print("saved out/工业化阶段清单_2024.md", len(L))

# ============ 2040 ============
L = ["# 全球工业化阶段清单（2040年推演）", "",
     "推演方法：以 2024 年分类为基础，按经济发展趋势对部分国家作阶段调整；未提及的国家保持 2024 年等级。",
     "人口 = 联合国 WPP2024 中等生育率情景 2040 年（全球 9,177,190,200）；",
     "阶段标准与 2024 年版相同（成熟 4000/400、中后期 3000/300、中期 1000/100、起步 500/50，得分以2024年人均发电量/钢产量计算）。", "",
     "对应地图：`out/world_industrial_stage_map_2040.png`　｜　另见：`out/工业化阶段清单_2024.md`（2024年实测分类）", "",
     "## 一、晋级名单（相对2024年）", ""]
PROMO = [("晋级发达国家", "中国、波兰、保加利亚、匈牙利（仅中国与欧盟国家晋级；台湾地区2024年已按发达国家列入；"
                        "俄罗斯、土耳其、沙特阿拉伯、阿联酋、马来西亚保持成熟工业化国家）"),
         ("晋级成熟工业化国家", "伊朗、哈萨克斯坦、巴西、智利、乌克兰、罗马尼亚、越南"),
         ("晋级工业化中后期国家", "墨西哥、南非、泰国、印度、伊拉克"),
         ("晋级工业化中期国家", "印度尼西亚、哥伦比亚、摩洛哥、突尼斯、菲律宾（乌兹别克斯坦2024年已属该档）"),
         ("晋级工业化起步国家", "巴基斯坦、孟加拉国、柬埔寨、危地马拉、赞比亚、加纳、斯里兰卡、肯尼亚、缅甸、科特迪瓦、"
                          "几内亚、安哥拉、博茨瓦纳、纳米比亚、津巴布韦、卢旺达、乌干达、尼日利亚、塞内加尔、莫桑比克、尼泊尔、坦桑尼亚")]
for a, b in PROMO:
    L.append(f"- **{a}**：{b}")
L += ["", "## 二、各类国家清单（2040年）", ""]
tot40 = 0.0
n24 = {r["code"]: r for r in d24}
for c in ORDER40:
    sub = sorted([r for r in d40 if r["cat2040"] == c], key=lambda x: -float(x["pop2040"]))
    p = sum(float(r["pop2040"]) for r in sub)
    tot40 += p
    L += [f"### {c}（{len(sub)} 国，{p/1e8:.2f} 亿，占全球 {p/WORLD40*100:.2f}%）", "",
          "| 国家 | 2040年人口(万人) | 2024年类别 | 变化 |", "|---|---:|---|---|"]
    for r in sub:
        c24 = r["cat2024"]
        chg = "保持" if c24 == c else f"{c24} → {c}"
        L.append(f"| {zh(r)} | {float(r['pop2040'])/1e4:,.0f} | {c24} | {chg} |")
    L.append("")
uncls40 = WORLD40 - tot40
L += ["## 三、人口汇总", "",
      "| 类别 | 国家数 | 总人口 | 占全球总人口比重 |", "|---|---:|---:|---:|"]
for c in ORDER40:
    sub = [r for r in d40 if r["cat2040"] == c]
    p = sum(float(r["pop2040"]) for r in sub)
    L.append(f"| {c} | {len(sub)} | {p/1e8:.2f} 亿 | {p/WORLD40*100:.1f}% |")
L += [f"| 其他人口不足1000万国家 | — | {uncls40/1e8:.2f} 亿 | {uncls40/WORLD40*100:.1f}% |",
      f"| **全球合计** | **{len(d40)}** | **{WORLD40/1e8:.2f} 亿** | **100.0%** |", "",
      "注明：中国已晋级发达国家（2024年为成熟工业化国家），中国台湾地区2024年即按发达国家列入，地图上均按后工业化国家着色；保加利亚、匈牙利、博茨瓦纳、纳米比亚"
      "人口不足1000万，按晋级名单列入；其余人口不足1000万的国家未分类。", "",
      "更新记录：2026-09-23 用户追加——越南→成熟工业化国家；伊拉克→工业化中后期国家；莫桑比克、尼泊尔→工业化起步国家。"]
with open(os.path.join(OUT, "工业化阶段清单_2040.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L))
print("saved out/工业化阶段清单_2040.md", len(L))
