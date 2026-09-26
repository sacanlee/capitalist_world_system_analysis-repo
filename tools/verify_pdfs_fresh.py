# -*- coding: utf-8 -*-
"""Verify every freshly built HTML has a matching, newer PDF."""
import io, glob, os, sys, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
WORK = os.path.join(BASE, 'work')
LANGS = ['cn', 'en', 'es', 'pt', 'fr', 'ru', 'ar', 'sw', 'hi', 'bn', 'id']
MARKER = float(sys.argv[1]) if len(sys.argv) > 1 else os.path.getmtime(
    os.path.join(WORK, '_rebuild2.log')) - 4000

bad = []
for lg in LANGS:
    hd = os.path.join(WORK, 'cn_html' if lg == 'cn' else lg + '_html')
    suffix = '' if lg == 'cn' else '_' + lg
    if not os.path.isdir(hd):
        continue
    fresh = [f for f in glob.glob(os.path.join(hd, '*.html'))
             if os.path.getmtime(f) >= MARKER]
    ok = 0
    for h in fresh:
        stem = os.path.splitext(os.path.basename(h))[0]
        p = os.path.join(BASE, 'pdf', stem + suffix + '.pdf')
        if not os.path.exists(p):
            bad.append((lg, stem, 'no pdf'))
        elif os.path.getmtime(p) < os.path.getmtime(h):
            bad.append((lg, stem, 'pdf older than html'))
        else:
            ok += 1
    print(f'{lg:3s} fresh html={len(fresh):3d}  up-to-date pdf={ok}')
print('=' * 70)
print('problems:', len(bad))
for b in bad[:20]:
    print('  ', b[0], b[2], b[1][:66])
