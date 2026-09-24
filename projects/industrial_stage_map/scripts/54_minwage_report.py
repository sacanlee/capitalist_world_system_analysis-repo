# -*- coding: utf-8 -*-
"""生成 out/最低工资_2024.md：各档代表值 + 逐国明细。"""
import json
import os

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "out")

with open(os.path.join(BASE, "raw", "ne_110m_countries.geojson"), encoding="utf-8") as f:
    gj = json.load(f)
ZH_GJ = {ft["properties"].get("ADM0_A3"): ft["properties"].get("NAME_ZH")
         for ft in gj["features"] if ft["properties"].get("NAME_ZH")}
ZH_GJ.update({"SDS": ZH_GJ.get("SSD"), "ISR": "以色列", "TWN": "台湾", "COD": "刚果民主共和国"})

ORDER = ["后工业化国家", "成熟工业化国家", "工业化中后期国家", "工业化中期国家",
         "工业化起步国家", "准备工业化国家"]
SKIP_TIERS = {"工业化中后期国家"}  # 样本仅3国，不具备分析价值
ZH = {"United States": "美国", "Sweden": "瑞典", "Belgium": "比利时", "Netherlands": "荷兰",
      "Spain": "西班牙", "Poland": "波兰", "Russia": "俄罗斯", "China": "中国", "Mexico": "墨西哥",
      "Saudi Arabia": "沙特阿拉伯", "Malaysia": "马来西亚", "Vietnam": "越南", "India": "印度",
      "Indonesia": "印度尼西亚", "Nigeria": "尼日利亚", "Bangladesh": "孟加拉国", "Ethiopia": "埃塞俄比亚",
      "Pakistan": "巴基斯坦", "Venezuela": "委内瑞拉", "Brazil": "巴西", "Turkey": "土耳其",
      "Argentina": "阿根廷", "Dominican Republic": "多米尼加", "Haiti": "海地", "Burundi": "布隆迪",
      "Afghanistan": "阿富汗", "Uganda": "乌干达", "Egypt": "埃及", "Thailand": "泰国",
      "South Africa": "南非", "Philippines": "菲律宾", "Colombia": "哥伦比亚", "Peru": "秘鲁",
      "Italy": "意大利", "Sweden ": "瑞典", "United Arab Emirates": "阿联酋", "North Korea": "朝鲜",
      "South Sudan": "南苏丹", "Guinea": "几内亚", "Rwanda": "卢旺达", "Zimbabwe": "津巴布韦",
      "Cambodia": "柬埔寨", "Somalia": "索马里", "Yemen": "也门", "Ethiopia ": "埃塞俄比亚"}

df = pd.read_csv(os.path.join(DATA, "minwage_final_2024.csv"))
S = pd.read_csv(os.path.join(DATA, "minwage_stats_2024.csv"))

L = ["# 各国最低月工资与工业化阶段（2024年）", "",
     "口径：**2024年名义美元／月**。数据来源：维基百科《List of countries by minimum wage》年度名义美元÷12；",
     "该表缺失的4国按权威来源折算（土耳其：2024年名义年度7,317美元；哈萨克斯坦：85,000坚戈／月÷2024均价汇率；",
     "肯尼亚：内罗毕等大城市一般工人16,113.75先令／月；阿根廷：2024年12月SMVM 279,718比索／月，官方汇率折272美元）。", "",
     "对应图：`out/minwage_by_stage_2024.png`　｜　逐国数据：`data/minwage_final_2024.csv`", "",
     "## 一、各档代表值（对数尺度 MAD 修正z分数剔除离群值后的平均值）", "",
     "| 工业化阶段 | 国家数(有数据/总) | 代表值(美元/月) | 中位数(参考) | 相对后工业化国家 | 典型国家（美元/月） | 区间(最小~最大) | 剔除的离群值 |",
     "|---|---:|---:|---:|---:|---|---|---|"]
for c in ORDER:
    st = S[S["category"] == c].iloc[0]
    if c in SKIP_TIERS:
        L.append(f"| {c} | {int(st['n_all'])} | —（样本过少，不具备分析价值） | — | — | — | — | — |")
        continue
    L.append(f"| {c} | {int(st['n'])} / {int(st['n_all'])} | **{st['mean_trim']:.0f}** | {st['median']:.0f} | "
             f"{st['ratio']:.2f} 倍 | {st['typical']} | {st['min']:.0f} ~ {st['max']:.0f} | "
             f"{st['outliers'] if isinstance(st['outliers'], str) else '—'} |")
L += ["", "## 二、逐国明细", ""]
for c in ORDER:
    sub = df[df["category"] == c].sort_values("monthly_usd", ascending=False, na_position="last")
    L += [f"### {c}（{len(sub)}国）", "",
          "| 国家 | 最低月工资(2024美元) | 数据来源 |", "|---|---:|---|"]
    for _, r in sub.iterrows():
        nm = ZH_GJ.get(r["code"]) or ZH.get(r["entity"]) or r["entity"]
        if pd.isna(r["monthly_usd"]):
            L.append(f"| {nm} | — | 无法定最低工资或无可比数据 |")
        else:
            L.append(f"| {nm} | {r['monthly_usd']:.0f} | {r['src']} |")
    L.append("")
L += ["## 三、计算说明", "",
      "- 代表值：对该档国家先按**标准离群值检验**（对数尺度 MAD 修正z分数，Iglewicz-Hoaglin，|z|>3.5 判为离群）剔除离群值，再取算术平均；中位数仅作参考。",
      "- 典型国家：在剔除离群值后的国家中，取值与该档代表值最接近（对数距离最小）且人口较多的2~3国。",
      "- 剔除情况：工业化中期剔除委内瑞拉（0.86美元/月）；工业化起步剔除叙利亚（8）、古巴；准备工业化剔除苏丹。",
      "- **工业化中后期国家仅3国（波兰、哈萨克斯坦、伊朗），样本过少、不具备分析价值，未纳入本报告与图表**（其数值亦受官方汇率扭曲影响）。",
      "- 部分国家无全国统一法定最低工资（如意大利、瑞典、阿联酋、埃及等），或维基表无数据（埃塞俄比亚、朝鲜、柬埔寨等），共14国不参与统计。",
      "- 各国最低工资口径存在差异（全国统一／分地区／分行业），跨国比较仅供参考。"]
with open(os.path.join(OUT, "最低工资_2024.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L))
print("saved out/最低工资_2024.md", len(L), "lines")
