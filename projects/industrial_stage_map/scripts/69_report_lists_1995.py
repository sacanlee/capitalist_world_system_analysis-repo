# -*- coding: utf-8 -*-
"""生成清单md：out/工业化阶段清单_1995.md（各类国家清单 + 指标数值 + 人口汇总）。"""
import csv
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "out")
WORLD95 = 5758878977.0

ORDER = ["成熟工业化国家", "工业化中后期国家", "工业化中期国家",
         "工业化起步国家", "准备工业化国家"]

with open(os.path.join(BASE, "raw", "ne_110m_countries.geojson"), encoding="utf-8") as f:
    gj = json.load(f)
ZH = {ft["properties"].get("ADM0_A3"): ft["properties"].get("NAME_ZH")
      for ft in gj["features"] if ft["properties"].get("NAME_ZH")}
ZH["SDS"] = ZH.get("SSD")
ZH.update({"ISR": "以色列", "TWN": "台湾", "CHN": "中国大陆"})

with open(os.path.join(DATA, "final_1995.csv"), encoding="utf-8-sig") as f:
    d95 = list(csv.DictReader(f))


def zh(r):
    return ZH.get(r["code"]) or r["entity"]


L = ["# 全球工业化阶段清单（1995年）", "",
     "数据口径：人口 = 联合国 WPP2024（1995年历史值）；人均发电量 = 美国能源信息署（EIA）"
     "《International Energy Annual 2005》表6.3 净发电量 1995年；",
     "人均钢产量 = 世界钢铁协会《Steel Statistical Yearbook 2003》1995年（未列入其国别表者按无产量计）。",
     "全球总人口 5,758,878,977（UN WPP2024，1995年）。", "",
     "**记分方法**：得分 =（人均年发电量 ÷ 标准人均发电量）+（人均年钢产量 ÷ 标准人均钢产量），得分 ≥ 2 视为达到该阶段标准。", "",
     "**阶段标准**（标准人均发电量 / 标准人均钢产量）：",
     "成熟工业化国家 4000 kWh / 400 kg；工业化中后期国家 3000 kWh / 300 kg；"
     "工业化中期国家 1000 kWh / 100 kg；工业化起步国家 500 kWh / 50 kg。", "",
     "**归类顺序**：从高标准到低标准依次对照，达到的最高阶段即为其类别；四档均未达到者列为准备工业化国家。",
     "本图按用户要求**不设发达国家档**，全部国家一律按记分归类，仅体现工业积累程度的差异。", "",
     "**国家名单**：与 2024 年图一致（2024年人口≥1000万的95国 + 以色列），故部分1995年人口不足1000万的国家"
     "（阿联酋、约旦、以色列等）仍按记分着色；其余未分类国家在地图中以浅紫色显示。", "",
     "**口径差异**：1995年发电量为 EIA 净发电量，2024年图为 Ember/OWID 毛发电量（两者相差约5%）；"
     "若1995年改用 OWID 毛发电量口径，伊朗、乌克兰、南非、以色列4国将上调一档。", "",
     "## 一、各类国家清单与指标", ""]
tot = 0.0
for c in ORDER:
    sub = sorted([r for r in d95 if r["category"] == c], key=lambda x: -float(x["pop1995"]))
    p = sum(float(r["pop1995"]) for r in sub)
    tot += p
    L += [f"### {c}（{len(sub)} 国，{p/1e8:.2f} 亿，占全球 {p/WORLD95*100:.2f}%）", "",
          "| 国家 | 人口(万人) | 人均发电量(kWh) | 人均钢产量(kg) | 成熟档得分 | 中后期档得分 | 中期档得分 | 起步档得分 | 归类依据 |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    key = {"成熟工业化国家": "s_mature", "工业化中后期国家": "s_late",
           "工业化中期国家": "s_mid", "工业化起步国家": "s_start"}.get(c)
    for r in sub:
        if c == "准备工业化国家":
            why = f"各档均未达标（起步档得分 {float(r['s_start']):.2f} < 2）"
        else:
            why = f"达标（{float(r[key]):.2f} ≥ 2）"
        L.append(f"| {zh(r)} | {float(r['pop1995'])/1e4:,.0f} | {float(r['pc_elec_kwh']):,.0f} | "
                 f"{float(r['pc_steel_kg']):,.1f} | {float(r['s_mature']):.2f} | {float(r['s_late']):.2f} | "
                 f"{float(r['s_mid']):.2f} | {float(r['s_start']):.2f} | {why} |")
    L.append("")

uncls = WORLD95 - tot
L += ["## 二、人口汇总（1995年）", "",
      "| 类别 | 国家数 | 总人口 | 占全球总人口比重 |", "|---|---:|---:|---:|"]
for c in ORDER:
    sub = [r for r in d95 if r["category"] == c]
    p = sum(float(r["pop1995"]) for r in sub)
    L.append(f"| {c} | {len(sub)} | {p/1e8:.2f} 亿 | {p/WORLD95*100:.1f}% |")
L += [f"| 其他人口不足1000万国家 | — | {uncls/1e8:.2f} 亿 | {uncls/WORLD95*100:.1f}% |",
      f"| **全球合计** | **{len(d95)}** | **{WORLD95/1e8:.2f} 亿** | **100.0%** |", "",
      "## 三、说明", "",
      "- 南苏丹1995年尚未独立（2011年独立），其电力与钢铁计入苏丹，清单中按 0 计并列为准备工业化国家。",
      "- 多米尼加、危地马拉1995年粗钢产量：SSY2003 该年为空格，按 USGS《Minerals Yearbook 1995》Vol.3 表11"
      "（多米尼加 “--” 无产出、危地马拉 “NA” 未报告）按 0 计。",
      "- 临界国家（得分 2.0±0.2）：英国 2.08、意大利 2.19 处于成熟档边界；乌克兰 1.97、西班牙 1.84、波兰 2.16、"
      "南非 1.97、以色列 1.92、哈萨克斯坦 1.86 处于中后期档边界；乌兹别克斯坦 2.12、阿塞拜疆 2.11、伊朗 1.98 "
      "处于中期档边界；叙利亚 2.08、突尼斯 1.94、阿尔及利亚 1.85 处于起步档边界。",
      "- 数据核对：SSY2003 解析的 1995 年世界各国合计 752,094 kt，与表内 World 行 752,271 kt 相差 0.02%；"
      "日、中、美、俄、印、韩、德、乌、巴西、意10国数值与公开统计一致；分类结果经脚本 `66_verify_1995.py` 独立重算，0 处不一致。", "",
      "对应地图：`out/world_industrial_stage_map_1995.png`　｜　另见：`out/工业化阶段清单_2024.md`（2024年）、"
      "`out/工业化阶段清单_2040.md`（2040年推演）、`out/工业化阶段清单_2055.md`（2055年推演）"]
with open(os.path.join(OUT, "工业化阶段清单_1995.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L))
print("saved out/工业化阶段清单_1995.md  行数=", len(L))
for c in ORDER:
    sub = [r for r in d95 if r["category"] == c]
    p = sum(float(r["pop1995"]) for r in sub)
    print(f"{c}\t{len(sub)}\t{p/1e8:.2f}亿\t{p/WORLD95*100:.1f}%")
