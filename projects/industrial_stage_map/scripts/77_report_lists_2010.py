# -*- coding: utf-8 -*-
"""生成清单md：out/工业化阶段清单_2010.md（各类国家清单 + 指标数值 + 人口汇总）。"""
import csv
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "out")
WORLD10 = 7021732143.0

ORDER = ["后工业化国家", "成熟工业化国家", "工业化中后期国家", "工业化中期国家",
         "工业化起步国家", "准备工业化国家"]

with open(os.path.join(BASE, "raw", "ne_110m_countries.geojson"), encoding="utf-8") as f:
    gj = json.load(f)
ZH = {ft["properties"].get("ADM0_A3"): ft["properties"].get("NAME_ZH")
      for ft in gj["features"] if ft["properties"].get("NAME_ZH")}
ZH["SDS"] = ZH.get("SSD")
ZH.update({"ISR": "以色列", "TWN": "中国台湾地区", "CHN": "中国大陆"})

with open(os.path.join(DATA, "final_2010.csv"), encoding="utf-8-sig") as f:
    d10 = list(csv.DictReader(f))


def zh(r):
    return ZH.get(r["code"]) or r["entity"]


L = ["# 全球工业化阶段清单（2010年）", "",
     "数据口径：人口 = 联合国 WPP2024（2010年历史值）；人均发电量 = Ember（OWID 整理）2010年；",
     "人均钢产量 = 世界钢铁协会《Steel Statistical Yearbook 2012》2010年（未列入其国别表者按无产量计）。",
     "全球总人口 7,021,732,143（UN WPP2024，2010年）。", "",
     "**记分方法**：得分 =（人均年发电量 ÷ 标准人均发电量）+（人均年钢产量 ÷ 标准人均钢产量），得分 ≥ 2 视为达到该阶段标准。", "",
     "**阶段标准**（标准人均发电量 / 标准人均钢产量）：",
     "成熟工业化国家 4000 kWh / 400 kg；工业化中后期国家 3000 kWh / 300 kg；"
     "工业化中期国家 1000 kWh / 100 kg；工业化起步国家 500 kWh / 50 kg。", "",
     "**归类顺序**：发达国家（IMF 发达经济体口径）默认列为后工业化国家（以色列、中国台湾地区按此列入）；"
     "其余国家从高标准到低标准依次对照，达到的最高阶段即为其类别；四档均未达到者列为准备工业化国家。", "",
     "**国家名单**：与 2024 年图一致（2024年人口≥1000万的95国 + 以色列）。", "",
     "## 一、各类国家清单与指标", ""]
tot = 0.0
for c in ORDER:
    sub = sorted([r for r in d10 if r["category"] == c], key=lambda x: -float(x["pop2010"]))
    p = sum(float(r["pop2010"]) for r in sub)
    tot += p
    L += [f"### {c}（{len(sub)} 国，{p/1e8:.2f} 亿，占全球 {p/WORLD10*100:.2f}%）", "",
          "| 国家 | 人口(万人) | 人均发电量(kWh) | 人均钢产量(kg) | 成熟档得分 | 中后期档得分 | 中期档得分 | 起步档得分 | 归类依据 |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    key = {"成熟工业化国家": "s_mature", "工业化中后期国家": "s_late",
           "工业化中期国家": "s_mid", "工业化起步国家": "s_start"}.get(c)
    for r in sub:
        if c == "后工业化国家":
            why = ("发达国家（IMF口径）默认列入（中国台湾地区）" if r["code"] == "TWN"
                   else "发达国家（IMF口径）默认列入")
        elif c == "准备工业化国家":
            why = f"各档均未达标（起步档得分 {float(r['s_start']):.2f} < 2）"
        else:
            why = f"达标（{float(r[key]):.2f} ≥ 2）"
        L.append(f"| {zh(r)} | {float(r['pop2010'])/1e4:,.0f} | {float(r['pc_elec_kwh']):,.0f} | "
                 f"{float(r['pc_steel_kg']):,.1f} | {float(r['s_mature']):.2f} | {float(r['s_late']):.2f} | "
                 f"{float(r['s_mid']):.2f} | {float(r['s_start']):.2f} | {why} |")
    L.append("")

uncls = WORLD10 - tot
L += ["## 二、人口汇总（2010年）", "",
      "| 类别 | 国家数 | 总人口 | 占全球总人口比重 |", "|---|---:|---:|---:|"]
for c in ORDER:
    sub = [r for r in d10 if r["category"] == c]
    p = sum(float(r["pop2010"]) for r in sub)
    L.append(f"| {c} | {len(sub)} | {p/1e8:.2f} 亿 | {p/WORLD10*100:.1f}% |")
L += [f"| 其他人口不足1000万国家 | — | {uncls/1e8:.2f} 亿 | {uncls/WORLD10*100:.1f}% |",
      f"| **全球合计** | **{len(d10)}** | **{WORLD10/1e8:.2f} 亿** | **100.0%** |", "",
      "## 三、说明", "",
      "- 后工业化国家按发达国家默认档列入，其记分未必达到成熟档：英国（成熟档得分 1.90）、希腊（1.68）、"
      "葡萄牙（1.62）按记分不足成熟档，系按发达国家口径默认列入；反之中国按记分（中后期档 2.61）归入工业化中后期国家。",
      "- 南苏丹2011年独立，2010年其电力与钢铁统计计入苏丹，清单中按 0 计并列为准备工业化国家。",
      "- 临界国家（得分 2.0±0.2）：中国 1.96、哈萨克斯坦 1.85 处于成熟档边界；南非 2.14、波兰 2.07、"
      "马来西亚 2.12 处于中后期档边界；乌兹别克斯坦 2.08、叙利亚 2.10、阿塞拜疆 2.17、塔吉克斯坦 2.15 "
      "处于中期档边界；朝鲜 2.09 处于起步档边界。",
      "- 数据核对：SSY2012 解析的 2010 年各国合计 1,431,667 kt（14.32 亿吨），与该协会公布的世界产量 14.33 亿吨相差 0.1%；"
      "中、日、美、印、俄、韩、德、乌、巴西、土10国数值与公开统计一致；分类结果经脚本 `74_verify_2010.py` 独立重算，0 处不一致。", "",
      "对应地图：`out/world_industrial_stage_map_2010.png`　｜　另见：`out/工业化阶段清单_1995.md`、"
      "`out/工业化阶段清单_2024.md`、`out/工业化阶段清单_2040.md`（推演）、`out/工业化阶段清单_2055.md`（推演）"]
with open(os.path.join(OUT, "工业化阶段清单_2010.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L))
print("saved out/工业化阶段清单_2010.md 行数=", len(L))
for c in ORDER:
    sub = [r for r in d10 if r["category"] == c]
    p = sum(float(r["pop2010"]) for r in sub)
    print(f"{c}\t{len(sub)}\t{p/1e8:.2f}亿\t{p/WORLD10*100:.1f}%")
