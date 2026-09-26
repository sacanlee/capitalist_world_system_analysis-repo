# -*- coding: utf-8 -*-
"""Rebuild HTML + PDF for every language, one language at a time.

Uses the whitelists written by plan_rebuild.py:
  work/_only_cn.txt      -> build_lang_html.py filter (Chinese titles)
  work/_only_<lang>.txt  -> to_pdf.py filter (translated HTML stems)
"""
import io, os, subprocess, sys, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
WORK = os.path.join(BASE, 'work')
LANGS = ['sw', 'hi', 'bn', 'id', 'ar', 'ru', 'fr', 'pt', 'es', 'en']


def run(args):
    t = time.time()
    r = subprocess.run([sys.executable, '-u'] + args, cwd=BASE, capture_output=True,
                       text=True, encoding='utf-8', errors='replace')
    out = (r.stdout or '') + (r.stderr or '')
    lines = [l for l in out.splitlines() if l.strip()]
    tail = lines[-2:] if lines else []
    print(f'  [{time.time()-t:6.1f}s] ' + ' | '.join(l[:70] for l in tail), flush=True)
    if r.returncode != 0:
        print('  !! exit', r.returncode, out[-300:], flush=True)


for lg in LANGS:
    print('=' * 70, flush=True)
    print('LANG', lg, flush=True)
    run([os.path.join(WORK, 'build_lang_html.py'), lg])
    run([os.path.join(WORK, 'to_pdf.py'), lg])
print('ALL LANGUAGES DONE', flush=True)
