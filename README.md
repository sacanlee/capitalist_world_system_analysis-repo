# Analysis of the Capitalist World-System

A collection of essays and answers by the Marxist analyst **最最遥远的路 (Zui Zui Yao Yuan De Lu)**, originally published on the Chinese Q&A platform **Zhihu**, analysing the historical development, internal structure, and future fate of the capitalist world-system from the standpoint of historical materialism.

**Author's Zhihu page:** https://www.zhihu.com/people/zui-zui-yao-yuan-de-lu-32/posts

## What This Project Contains

This repository publishes the author's articles — originally written in Chinese — as PDF files in 11 languages, organised by topic. Every PDF preserves the images of the original web pages, the in-text citation markers, and a bilingual notes section (target language + Chinese original) at the end of each article.

## Repository Structure

```
repo/
├── articles/           — the multilingual article collection (507 PDFs, 11 languages)
│   ├── Chinese/        (中文原文)
│   │   ├── world-system-mechanisms/    世界体系基本机制 — the basic mechanisms of the world-system; the historical fate of capitalism
│   │   ├── southern-capitalism/        南方资本主义的发展 — the development of capitalism in the South (excluding India)
│   │   ├── india-rise/                 印度的崛起 — the rise of India
│   │   ├── multipolar-world/           多级世界分析 — analyses of the multipolar world
│   │   ├── language-globalization/     全球化时代的语言 — language questions within the world-system
│   │   └── other-observations/         其他观察 — other observations
│   ├── English/
│   │   └── (same six categories)
│   ├── Français/
│   ├── Español/
│   ├── português/
│   ├── العربية/
│   ├── Kiswahili/
│   ├── हिन्दी/
│   ├── বাংলা/
│   ├── Bahasa Indonesia/
│   └── Русский/
└── projects/           — coding projects related to this analysis (to be added)
```

## Categories

| Directory | Chinese name | Scope |
|---|---|---|
| `world-system-mechanisms` | 世界体系基本机制 | The basic mechanisms of the world-system: world-system theory, the historical fate of capitalism, the labour theory of value, the rate of profit, class structure |
| `southern-capitalism` | 南方资本主义的发展 | The development of capitalism in the countries of the South (industrialisation of Vietnam, Indonesia, sub-Saharan Africa, etc.) |
| `india-rise` | 印度的崛起 | The rise of India: its industrialisation, military industry, resources, and prospects |
| `multipolar-world` | 多级世界分析 | The multipolar world: how many poles, the logic of war, great-power relations |
| `language-globalization` | 全球化时代的语言 | Language questions in the world-system: English as the global lingua franca, the future of French/Spanish/Arabic, India's language policy, Vietnam's English policy |
| `other-observations` | 其他观察 | Other observations: religion and materialism, the American working class, the DSA, AI and robots, the AI bubble |

### Article counts by language

| Language | Articles |
|---|---|
| Chinese, English, Français, Español, português, العربية, Русский | 51 |
| Kiswahili, Bahasa Indonesia | 42 |
| हिन्दी, বাংলা | 33 |

The September 2026 batch (8 new articles: the long-wave essays, the rise of China in the world-system, reformism, autarky, the two-day weekend, which countries can still become developed before 2055, and AI programming) has been translated into Chinese, English, French, Spanish, Portuguese, Russian and Arabic. The remaining four languages carry the original 42-article collection.

The 26 September 2026 addition — *Is Another Movement to Overthrow Capital Possible in the 21st Century?* — joins the same seven languages.

## Translation Notes

- The author is a **Marxist**; the translations are made within the Marxist conceptual framework (historical materialism, class analysis, the capitalist world-system, imperialism, surplus value, etc.).
- The style of translation is **elegant yet accessible** (典雅通俗).
- Chinese internet slang used by the author is translated according to its real meaning, e.g.:
  - 东大 / 东方大国 / 龙国 = **China**
  - 西大 / 西方大国 / 米国 = **United States**
  - 天竺 / 南大 / 南方大国 = **India**
  - 欧国 = **EU**
  - ZF / GOV = **government**
  - 波斯 = **Iran**
  - 双休 (two days off per week) = **two-day weekend**
- Each article ends with a **Notes** section whose numbering corresponds to the in-text citation markers `[n]`; each note gives the translated text together with the Chinese original and the source link.
- Images are reproduced as in the original web pages; images whose text is part of the source data are kept in the original.

## Build Pipeline

The `tools/` directory holds the scripts that produce everything under `articles/`:

| Script | Purpose |
|---|---|
| `extract_full.py <src_dir>` | Zhihu HTML archive → clean Chinese HTML + structured text (with `[IMAGE n]`, `[n]` citation markers, `[图注: ]`, `[表格]`) + notes JSON |
| `sanitize_new.py` | rewrites Chinese internet slang into plain country/government names (September 2026 batch) |
| `sanitize_batch.py <cn-title> [...]` | same, generic version; adds 龙国 / 米国 / 欧国 |
| `TRANSLATION_SPEC.md` | the format and terminology rules every translation follows |
| `build_lang_html.py <lang>` | translated text + notes JSON + original images → per-language HTML (bilingual notes section, footer) |
| `to_pdf.py <lang> [outdir]` | Headless-Edge batch HTML → PDF |
| `verify_new.py` | QA: title line, in-text `[n]` vs notes JSON, `[NOTES]` numbering, `[IMAGE n]` counts |
| `gen_only.py` | writes per-language whitelists so a run touches only one batch of articles |
| `rebuild_articles_structure.py` | rebuilds the whole `articles/<language>/<category>/` tree |
| `add_new_articles.py` | incremental (non-destructive) addition of a new batch to the tree (September 2026 batch) |
| `add_articles.py <category> <cn-title> [...]` | generic incremental addition of one batch to the tree |
| `pdf_check.py <pdf> <prefix> [pages]` | renders PDF pages to PNG for visual inspection |

`work/txt/*.txt` (Chinese) and `work/<lang>_txt/*.txt` use the **Chinese title as the filename**; the
translated title lives on the first `# ` line. This is what links a translation to its notes JSON
and its images.

## Original Source

All articles were originally published in Chinese by the author on Zhihu:

- Author: 最最遥远的路 — https://www.zhihu.com/people/zui-zui-yao-yuan-de-lu-32/posts

Each PDF's footer contains the original article link and the author's profile link.

*The copyright of the articles belongs to the author. This repository is a non-commercial translation and compilation of publicly published content.*
