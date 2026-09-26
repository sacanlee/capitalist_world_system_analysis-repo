# -*- coding: utf-8 -*-
"""Render work/_hunks/<title>.json into a human-readable worklist for the
translation-patching agents: work/_worklist/<title>.md"""
import io, os, json, sys, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
WORK = os.path.join(BASE, 'work')
HUNKS = os.path.join(WORK, '_hunks')
OUT = os.path.join(WORK, '_worklist')
os.makedirs(OUT, exist_ok=True)

for hp in sorted(glob.glob(os.path.join(HUNKS, '*.json'))):
    d = json.load(open(hp, encoding='utf-8'))
    t = d['title']
    lines = [f'# 补译工作清单：{t}', '',
             f'- 中文源文件（已含完整文字）：`work/txt/{t}.txt`',
             f'- 待补译文：`work/<lang>_txt/{t}.txt`',
             f'- 共 {len(d["hunks"])} 处插入，累计 {d["added"]} 个中文字符',
             '- 每处都是**段落后半截被吞掉**：把 inserted 的中文译成目标语言，'
             '接在 before 所对应的译文之后、after 所对应的译文之前。',
             '- 只**新增**文字，不要改写、删减或重排既有译文。', '']
    for h in d['hunks']:
        lines.append(f'## 第 {h["k"]} 处（+{len(h["inserted"])} 字）')
        lines.append('')
        lines.append(f'- 前文锚点（中文，译文里已存在）：…{h["before"]}')
        lines.append(f'- **需要补译的文字**：{h["inserted"]}')
        lines.append(f'- 后文锚点（中文，译文里已存在）：{h["after"]}…')
        lines.append('')
    open(os.path.join(OUT, t + '.md'), 'w', encoding='utf-8').write('\n'.join(lines))
    print(f'{t[:42]:44s} hunks={len(d["hunks"]):3d} -> {t[:40]}.md')
print('DONE', len(glob.glob(os.path.join(OUT, "*.md"))))
