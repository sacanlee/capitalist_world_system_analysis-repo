# -*- coding: utf-8 -*-
"""最低工资 vs 工业化阶段（2024年分类）
- 口径：2024年名义美元 / 月（维基百科年度名义美元 ÷ 12；缺4国按来源折算）
- 每档代表值：1.5×IQR 剔除离群值后的平均值
- 输出 out/minwage_by_stage_2024.png + data/minwage_stats_2024.csv
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "out")

plt.rcParams["font.family"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

ORDER = ["后工业化国家", "成熟工业化国家", "工业化中后期国家", "工业化中期国家",
         "工业化起步国家", "准备工业化国家"]
# 工业化中后期档仅3国（波兰、哈萨克斯坦、伊朗），样本过少不具备分析价值，本图不纳入
SKIP_TIERS = {"工业化中后期国家"}
PLOT_ORDER = [c for c in ORDER if c not in SKIP_TIERS]
DISPLAY = {"后工业化国家": "后工业化国家（发达）"}
COLORS = {"后工业化国家": "#1f4e79", "成熟工业化国家": "#e8590c",
          "工业化中后期国家": "#ffa94d", "工业化中期国家": "#ffd43b",
          "工业化起步国家": "#a9d08e", "准备工业化国家": "#adb5bd"}

# 维基主表缺失的4国：2024年名义美元/月（来源见 out 报告）
IMPUTE = {  # code -> (monthly USD, source)
    "TUR": (7317.0 / 12, "维基同页2023/2024年表：2024名义年度7,317US$"),
    "KAZ": (181.1, "2024年最低工资85,000坚戈/月÷2024均价≈468.6坚戈/US$"),
    "KEN": (1490.0 / 12, "2024年11月起内罗毕等大城市一般工人16,113.75先令/月，"
                          "折年193,365先令÷2024均价≈129.9先令/US$"),
    "ARG": (272.0, "2024年12月SMVM 279,718比索/月，官方汇率折US$272"),
}

mw = pd.read_csv(os.path.join(DATA, "minwage_raw.csv"))
d24 = pd.read_csv(os.path.join(DATA, "final_v2.csv"))
FIX = {"Democratic Republic of Congo": "Democratic Republic of the Congo",
       "Cote d'Ivoire": "Côte d'Ivoire", "Czechia": "Czech Republic"}
wiki = {r["wiki_name"]: r for _, r in mw.iterrows()}

rows = []
for _, r in d24.iterrows():
    ent = r["entity"]
    w = wiki.get(FIX.get(ent, ent))
    m = None
    src = ""
    if w is not None and pd.notna(w["annual_nom"]):
        m = float(w["annual_nom"]) / 12.0
        src = "维基年度名义US$/12"
    elif r["code"] in IMPUTE:
        m = IMPUTE[r["code"]][0]
        src = IMPUTE[r["code"]][1]
    rows.append({"code": r["code"], "entity": ent, "category": r["category"],
                 "monthly_usd": m, "src": src})
df = pd.DataFrame(rows)

stats = []
for i, c in enumerate(ORDER):
    sub = df[(df["category"] == c) & df["monthly_usd"].notna()].copy()
    n_all = int((df["category"] == c).sum())
    if c in SKIP_TIERS or sub.empty:
        stats.append({"category": c, "n_all": n_all, "n": 0, "n_used": 0,
                      "mean_trim": float("nan"), "median": float("nan"), "ratio": float("nan"),
                      "min": float("nan"), "max": float("nan"), "outliers": "（该档不纳入分析）"})
        continue
    v = sub["monthly_usd"].astype(float)
    # 标准离群值检验：对数尺度上的 MAD 修正z分数（Iglewicz & Hoaglin），|z|>3.5 判为离群
    lv = np.log10(v)
    med_lv = float(np.median(lv))
    mad = float(np.median(np.abs(lv - med_lv)))
    if mad > 0:
        mz = 0.6745 * (lv - med_lv) / mad
        keep_mask = mz.abs() <= 3.5
    else:
        keep_mask = pd.Series(True, index=v.index)
    keep = v[keep_mask]
    names = sub.loc[~keep_mask, "entity"].tolist()
    stats.append({"category": c, "n_all": n_all, "n": len(sub), "n_used": len(keep),
                  "mean_raw": v.mean(), "median": v.median(), "mean_trim": keep.mean(),
                  "min": float(v.min()), "max": float(v.max()),
                  "outliers": "、".join(names)})
S = pd.DataFrame(stats)

# 典型国家：剔除离群值后，取值最接近该档代表值的国家（对数距离），并列时取人口更多者
pop24 = pd.read_csv(os.path.join(DATA, "final_v2.csv"))[["code", "pop2024"]]
df = df.merge(pop24, on="code", how="left")
ZH_NAME = {"United States": "美国", "Germany": "德国", "United Kingdom": "英国",
           "Netherlands": "荷兰", "Belgium": "比利时", "Spain": "西班牙", "France": "法国",
           "Canada": "加拿大", "Chile": "智利", "Czechia": "捷克", "Greece": "希腊",
           "Sweden": "瑞典", "Portugal": "葡萄牙", "Italy": "意大利", "Israel": "以色列",
           "Japan": "日本", "South Korea": "韩国", "Australia": "澳大利亚", "Poland": "波兰",
           "Russia": "俄罗斯", "China": "中国", "Turkey": "土耳其", "Saudi Arabia": "沙特阿拉伯",
           "Malaysia": "马来西亚", "Iran": "伊朗", "Kazakhstan": "哈萨克斯坦",
           "Brazil": "巴西", "Mexico": "墨西哥", "Argentina": "阿根廷", "Thailand": "泰国",
           "South Africa": "南非", "Iraq": "伊拉克", "India": "印度", "Vietnam": "越南",
           "Egypt": "埃及", "Philippines": "菲律宾", "Indonesia": "印度尼西亚",
           "Colombia": "哥伦比亚", "Algeria": "阿尔及利亚", "Ukraine": "乌克兰",
           "Uzbekistan": "乌兹别克斯坦", "Peru": "秘鲁", "Ecuador": "厄瓜多尔",
           "Azerbaijan": "阿塞拜疆", "Dominican Republic": "多米尼加", "Jordan": "约旦",
           "Tunisia": "突尼斯", "Morocco": "摩洛哥", "Nigeria": "尼日利亚", "Kenya": "肯尼亚",
           "Myanmar": "缅甸", "Uganda": "乌干达", "Tanzania": "坦桑尼亚",
           "Bangladesh": "孟加拉国", "Pakistan": "巴基斯坦", "Ethiopia": "埃塞俄比亚",
           "DR Congo": "刚果金", "Democratic Republic of Congo": "刚果金", "Angola": "安哥拉",
           "Ghana": "加纳", "Mozambique": "莫桑比克", "Nepal": "尼泊尔", "Yemen": "也门",
           "Afghanistan": "阿富汗", "Sudan": "苏丹", "Cote d'Ivoire": "科特迪瓦",
           "Cameroon": "喀麦隆", "Madagascar": "马达加斯加", "Niger": "尼日尔",
           "Mali": "马里", "Burkina Faso": "布基纳法索", "Malawi": "马拉维",
           "Zambia": "赞比亚", "Senegal": "塞内加尔", "Somalia": "索马里", "Chad": "乍得",
           "Guinea": "几内亚", "Rwanda": "卢旺达", "Benin": "贝宁", "Burundi": "布隆迪",
           "Haiti": "海地", "South Sudan": "南苏丹", "Papua New Guinea": "巴新",
           "Bolivia": "玻利维亚", "Honduras": "洪都拉斯", "Cuba": "古巴", "Syria": "叙利亚",
           "North Korea": "朝鲜", "Sri Lanka": "斯里兰卡", "Cambodia": "柬埔寨",
           "Guatemala": "危地马拉", "Zimbabwe": "津巴布韦", "Venezuela": "委内瑞拉",
           "Paraguay": "巴拉圭", "Uruguay": "乌拉圭"}
til = {}
for c in ORDER:
    st = S[S["category"] == c].iloc[0]
    m = st.get("mean_trim")
    sub = df[(df["category"] == c) & df["monthly_usd"].notna()].copy()
    if not isinstance(m, float) or pd.isna(m) or sub.empty:
        til[c] = "—"
        continue
    sub["dev"] = (np.log10(sub["monthly_usd"].astype(float)) - np.log10(m)).abs()
    cand = sub.sort_values(["dev", "pop2024"], ascending=[True, False]).head(6)
    cand = cand.sort_values("pop2024", ascending=False).head(3)
    til[c] = "、".join(f"{ZH_NAME.get(r['entity'], r['entity'])}{r['monthly_usd']:.0f}"
                      for _, r in cand.iterrows())

base = float(S[S["category"] == "后工业化国家"]["mean_trim"].iloc[0])
S["ratio"] = S["mean_trim"] / base
S["typical"] = S["category"].map(til)
S.to_csv(os.path.join(DATA, "minwage_stats_2024.csv"), index=False, encoding="utf-8-sig")

print(S.to_string(index=False))
print("\n有月最低工资数据的国家数:", df["monthly_usd"].notna().sum(), "/", len(df))
print("无数据:", df[df["monthly_usd"].isna()]["entity"].tolist())
df.to_csv(os.path.join(DATA, "minwage_final_2024.csv"), index=False, encoding="utf-8-sig")

# ---------------- 绘图 ----------------
fig = plt.figure(figsize=(16.5, 11.6), dpi=140)
ax = fig.add_axes([0.075, 0.40, 0.90, 0.52])
rng = np.random.default_rng(7)

for i, c in enumerate(PLOT_ORDER):
    sub = df[(df["category"] == c) & df["monthly_usd"].notna()]
    x = i + rng.uniform(-0.22, 0.22, len(sub))
    ax.scatter(x, sub["monthly_usd"], s=46, color=COLORS[c], edgecolors="#555555",
               linewidths=0.5, zorder=3, alpha=0.95)
    st = S[S["category"] == c].iloc[0]
    ax.hlines(st["mean_trim"], i - 0.36, i + 0.36, color="#c00000", linewidth=3.2, zorder=5)
    ax.text(i + 0.40, st["mean_trim"], f"{st['mean_trim']:.0f}", color="#c00000",
            fontsize=11, weight="bold", va="center")

# 标注若干国家
LABEL = ["United States", "Sweden", "Belgium", "Netherlands", "Spain", "Poland", "Russia",
         "China", "Mexico", "Saudi Arabia", "Malaysia", "Vietnam", "India", "Indonesia",
         "Nigeria", "Bangladesh", "Ethiopia", "Pakistan", "Venezuela", "Brazil", "Turkey",
         "Argentina", "Dominican Republic", "Haiti", "Burundi", "Afghanistan", "Uganda"]
ZH = {"United States": "美国", "Sweden": "瑞典", "Belgium": "比利时", "Netherlands": "荷兰",
      "Spain": "西班牙", "Poland": "波兰", "Russia": "俄罗斯", "China": "中国", "Mexico": "墨西哥",
      "Saudi Arabia": "沙特", "Malaysia": "马来西亚", "Vietnam": "越南", "India": "印度",
      "Indonesia": "印尼", "Nigeria": "尼日利亚", "Bangladesh": "孟加拉国", "Ethiopia": "埃塞俄比亚",
      "Pakistan": "巴基斯坦", "Venezuela": "委内瑞拉", "Brazil": "巴西", "Turkey": "土耳其",
      "Argentina": "阿根廷", "Dominican Republic": "多米尼加", "Haiti": "海地", "Burundi": "布隆迪",
      "Afghanistan": "阿富汗", "Uganda": "乌干达", "Egypt": "埃及", "Thailand": "泰国",
      "South Africa": "南非", "Philippines": "菲律宾", "Colombia": "哥伦比亚", "Peru": "秘鲁"}
OFFSET = {"Netherlands": (6, 2), "Belgium": (6, -8), "Spain": (6, -3), "United States": (-42, -4),
          "Dominican Republic": (6, 3), "Venezuela": (-16, 6), "Argentina": (6, -8),
          "Haiti": (-6, 6), "Afghanistan": (6, -9), "Uganda": (-24, -12), "Pakistan": (6, 2),
          "Nigeria": (6, -2), "India": (-14, -12), "Mexico": (6, 2), "Brazil": (6, -1),
          "China": (6, -2), "Turkey": (-16, 6), "Saudi Arabia": (6, 0), "Russia": (6, 1),
          "Poland": (6, 2), "Ethiopia": (6, 0), "Bangladesh": (-38, -3),
          "Malaysia": (-56, -2)}
for i, c in enumerate(PLOT_ORDER):
    for _, r in df[(df["category"] == c) & df["monthly_usd"].notna()].iterrows():
        if r["entity"] in LABEL:
            ax.annotate(ZH.get(r["entity"], r["entity"]), (i, r["monthly_usd"]),
                        textcoords="offset points", xytext=OFFSET.get(r["entity"], (6, 4)),
                        fontsize=8.6, color="#222222")

ax.set_yscale("log")
ax.set_ylim(20, 4000)
ax.set_yticks([20, 50, 100, 200, 500, 1000, 2000, 4000])
ax.set_yticklabels(["20", "50", "100", "200", "500", "1000", "2000", "4000"], fontsize=11)
ax.set_xticks(range(len(PLOT_ORDER)))
ax.set_xticklabels([DISPLAY.get(c, c).replace("（发达）", "\n（发达）") if c == "后工业化国家"
                    else c.replace("国家", "\n国家") for c in PLOT_ORDER], fontsize=12)
ax.set_ylabel("法定最低月工资（2024年美元，对数刻度）", fontsize=13)
ax.grid(axis="y", linestyle=":", color="#bbbbbb", alpha=0.8)
ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_title("各工业化阶段国家的最低月工资分布（2024年）", fontsize=19, pad=10)
ax.text(0.5, -0.115, "红横线＝各档剔除离群值（对数尺度 MAD 修正z分数，|z|>3.5）后的平均月最低工资；工业化中后期档样本过少未纳入",
        transform=ax.transAxes, ha="center", fontsize=10.5, color="#666666")

# ---------------- 图下数值表 ----------------
y = 0.335
fig.text(0.03, y, "各档最低月工资（2024年美元）", fontsize=15, weight="bold")
y -= 0.032
cols = [0.03, 0.195, 0.30, 0.415, 0.535, 0.645, 0.865]
heads = ["工业化阶段", "国家数(有数据/总)", "剔除离群值后平均", "中位数(参考)",
         "相对后工业化国家", "典型国家（美元/月）", "区间(最小~最大)"]
for x, h in zip(cols, heads):
    fig.text(x, y, h, fontsize=11, weight="bold")
y -= 0.024
for c in PLOT_ORDER:
    st = S[S["category"] == c].iloc[0]
    fig.text(cols[0], y, DISPLAY.get(c, c), fontsize=11, color=COLORS[c])
    fig.text(cols[1], y, f"{st['n']} / {st['n_all']}", fontsize=11)
    fig.text(cols[2], y, f"{st['mean_trim']:.0f} 美元（n={int(st['n_used'])}）", fontsize=11, weight="bold")
    fig.text(cols[3], y, f"{st['median']:.0f} 美元", fontsize=11)
    fig.text(cols[4], y, "1.00 倍" if c == "后工业化国家" else f"{st['ratio']:.2f} 倍", fontsize=11)
    fig.text(cols[5], y, til[c], fontsize=10, color="#333333")
    fig.text(cols[6], y, f"{st['min']:.0f} ~ {st['max']:.0f}", fontsize=11)
    y -= 0.0225

y -= 0.006
notes = [
    "口径：2024年名义美元／月。数据来源：维基百科《List of countries by minimum wage》年度名义美元÷12。",
    "该表缺失的4国按权威来源折算：土耳其（2024年名义年度7,317美元）、哈萨克斯坦（85,000坚戈／月÷2024均价汇率）、"
    "肯尼亚（内罗毕等大城市一般工人16,113.75先令／月）、阿根廷（2024年12月SMVM 279,718比索／月，官方汇率折272美元）。",
    "代表值：先按标准离群值检验（对数尺度 MAD 修正z分数，Iglewicz-Hoaglin，|z|>3.5 判为离群）剔除离群值，再取算术平均；中位数仅作参考。剔除情况见下表“剔除的离群值”列。",
    "工业化中后期国家仅 3 国（波兰、哈萨克斯坦、伊朗），样本过少、不具备分析价值，未纳入本图（其数值亦受官方汇率扭曲影响）。",
    "无法定最低工资或无可比数据的国家不参与统计（共14国，如意大利、瑞典、阿联酋、埃及、埃塞俄比亚、朝鲜等）。",
    "各国逐国数值见 data/minwage_final_2024.csv。",
]
for t in notes:
    fig.text(0.03, y, t, fontsize=9.3, color="#666666", wrap=False)
    y -= 0.019

fig.savefig(os.path.join(OUT, "minwage_by_stage_2024.png"), facecolor="white")
print("\nsaved out/minwage_by_stage_2024.png")
