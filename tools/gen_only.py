# -*- coding: utf-8 -*-
"""Write work/_only_<lang>.txt lists (built HTML stems) so to_pdf.py only
converts the 8 new articles of this batch."""
import os, io, sys, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
WORK = os.path.join(BASE, 'work')
CN = [l.strip() for l in open(os.path.join(WORK, '_only_cn.txt'), encoding='utf-8') if l.strip()]
TITLES = {}
for t in CN:
    first = open(os.path.join(WORK, 'txt', t + '.txt'), encoding='utf-8').readline().strip()
    TITLES[t] = first[2:].strip()

for lang in ('en', 'es', 'pt', 'fr', 'ru', 'ar'):
    names = []
    for t in CN:
        out = os.path.join(WORK, lang + '_html' if lang != 'cn' else 'cn_html')
        src = os.path.join(WORK, lang + '_txt' if lang != 'cn' else 'txt', t + '.txt')
        first = open(src, encoding='utf-8').readline().strip()
        tr = first[2:].strip()
        import re
        stem = re.sub(r'[\\/:*?"<>|\r\n]', ' ', tr)
        stem = re.sub(r'\s+', ' ', stem).strip()[:100]
        names.append(stem)
    p = os.path.join(WORK, '_only_%s.txt' % lang)
    open(p, 'w', encoding='utf-8').write('\n'.join(names) + '\n')
    print(lang, len(names), '->', p)
    for n in names:
        print('   ', n)
