# 新文章翻译规范（2026-09-25 批次，8 篇）

作者「最最遥远的路」是马克思主义者。全部译文必须在马克思主义/历史唯物主义的语境下
（世界体系、中心—半外围—外围、阶级分析、帝国主义、剩余价值、改良主义等），
风格**典雅通俗**（elegant yet accessible），不要学术腔堆砌，也不要口语化网文腔。

## 输入 / 输出

- 输入：`work/txt/<中文标题>.txt`（已做过关键词替换的定稿）
- 输出：`work/<lang>_txt/<中文标题>.txt`
  - **文件名必须是中文标题原样**（管道靠它关联注释 json 与图片），不要翻译文件名！
  - 文件第一行 `# ` 后写**目标语言标题**（用于 PDF 文件名与页面大标题）
- lang 取值：`en` `es` `pt` `fr` `ru` `ar`

## 格式（逐条严格遵守，标记一律照抄）

| 源标记 | 处理方式 |
|---|---|
| `# 中文标题` | 译为 `# Translated Title` |
| `[元信息] 知乎 · 2026-09-19` | 保留方括号中文标记，只把正文部分改成目标语言：`[元信息] Zhihu · 2026-09-19` |
| `## ` / `### ` | `## ` / `### ` + 译文 |
| `> ` 引用 | 照旧 |
| `- ` 列表项 | 照旧 |
| `[IMAGE n]` | **原样保留**，不翻译、不移动、不增删 |
| `[图注: ...]` | 保留 `[图注: ` 前缀与结尾 `]`，只翻译里面的文字 |
| `[表格]` | 保留标记；表格行沿用竖线分隔，数字保留 |
| `[n]`（正文注释标记） | **原样保留**，编号、位置、数量必须与中文源完全一致 |
| 空行 | 段落之间必须有空行 |

不要添加任何解释性文字、译者注、前言后记。

## 文末 `[NOTES]` 块（仅当该文章有注释时）

中文源文件里没有 NOTES 块；注释内容在 `work/notes/<中文标题>.json` 的 `notes[]` 里。
若 `notes` 非空，必须在译文末尾追加：

```
[NOTES]
[1] 第 1 条注释的译文
[2] 第 2 条注释的译文
```

- 编号、条数、顺序与 json 完全一致（`[n] ` 后直接跟译文，不要换行）
- 只写译文，**不要**自己加中文原文或 URL（管道会自动补上中文原文与链接）
- 专有名词、书名、论文名首次出现可附英文原名，但不要加引号包裹的冗长说明

## 关键词（中文阶段已经替换完毕，译文必须用这些词）

| 中文词 | 含义 | en | es | pt | fr | ru | ar |
|---|---|---|---|---|---|---|---|
| 印度 | India | India | India | Índia | Inde | Индия | الهند |
| 中国 | China | China | China | China | Chine | Китай | الصين |
| 美国 | US | the US / the United States | EE. UU. / Estados Unidos | EUA / Estados Unidos | États-Unis | США | الولايات المتحدة |
| 政府 | government | government | gobierno | governo | gouvernement | правительство | الحكومة |
| 双休 | two-day weekend (双休日) | two-day weekend | fin de semana de dos días | fim de semana de dois dias | week-end de deux jours | двухдневные выходные | عطلة نهاية الأسبوع ليومين |

不要在译文中出现 East Power / Dragon / Southern Power 之类代号，直接写国家名。

## 术语表（沿用已发布 42 篇的既有译法）

译前请先 `grep` 已有语料确认既有译法，保持一致：

- 世界体系 → world-system / sistema-mundo / système-monde / мировое-система(мир-система) / النظام العالمي
- 中心 / 半外围 / 外围 → core·centre / semi-periphery / periphery
- 资本主义生产方式 → capitalist mode of production
- 剩余价值 → surplus value；剥削 → exploitation
- 工人阶级 / 资产阶级 → working class / bourgeoisie
- 阶级斗争 → class struggle
- 改良主义 → reformism
- 长波（周期）→ long wave
- 利润率 → rate of profit
- 工业化 → industrialisation / industrialización / industrialização / industrialisation / индустриализация / التصنيع
- 半外围工业国 → semi-peripheral industrial country
- 龙头企业（世界级）→ leading global enterprise / global champion firm
- 产业政策 → industrial policy；混合经济 → mixed economy
- 新质生产力 → new-quality productive forces
- 一带一路 → Belt and Road Initiative
- 中国制造2025 → Made in China 2025
- 中等收入陷阱 → middle-income trap
- 世界政府 → world government
- 社会改良 → social reform
- 跨国资本 → transnational capital
- 剪刀差 → scissors differential（价格剪刀差 price scissors）
- 义务交售制 → obligatory delivery quota system
- 农村税费改革 → reform of rural taxes and fees
- 人均钢产量 / 人均发电量 → per-capita steel output / per-capita electricity generation
- 单位：亿 = 100 million，万亿 = trillion，万 = 10 thousand；`400kwh` `400kg` 等照抄

## 数字与标点

- 数字保持阿拉伯数字原样（`2025年` → `2025`，`80%` → `80%`）
- 阿拉伯语用西方数字（0-9），不要用阿拉伯-印度数字
- 俄语、阿拉伯语：书名用既有语料习惯（《…》→ «…» / 《…》）
- 中文顿号「、」按目标语言习惯改为逗号/and

## 自检（必须做）

写完每个文件后运行：

```
python work/verify_new.py
```

自己那门语言对应的 8 行必须全部 `OK`（title 行有译文、body [n] 与 json 一致、
[NOTES] 编号一致、[IMAGE n] 数量一致）。有 FAIL 就改到全 OK 再收工。

## 分批写入（重要）

单个文件较大时，**分片写入**：先用 Write 写第 1 片（如 `_part1.txt`），
再用 `cat _part1.txt _part2.txt > 目标.txt` 合并，最后删掉分片。
不要试图一次 Write 一个超大文件。每写完一篇立刻落盘，再写下一篇。
