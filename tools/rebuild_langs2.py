# -*- coding: utf-8 -*-
"""Rebuild every language by converting exactly the HTML files just (re)built.

Background: a few old HTML files were named with a trailing space, so matching
a whitelist against the translated title missed them.  Instead of guessing the
name, rebuild the HTML for the repaired batch and then take every HTML whose
mtime is newer than the run marker as the conversion set.
"""
import io, glob, os, subprocess, sys, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
WORK = os.path.join(BASE, 'work')
LANGS = ['en', 'es', 'pt', 'fr', 'ru', 'ar', 'sw', 'hi', 'bn', 'id']

T0 = time.time() - 5
print('marker', time.strftime('%H:%M:%S', time.localtime(T0)), flush=True)

for lg in LANGS:
    r = subprocess.run([sys.executable, os.path.join(WORK, 'build_lang_html.py'), lg],
                       cwd=BASE, capture_output=True, text=True, encoding='utf-8', errors='replace')
    built = [os.path.splitext(os.path.basename(f))[0]
             for f in glob.glob(os.path.join(WORK, lg + '_html', '*.html'))
             if os.path.getmtime(f) >= T0]
    open(os.path.join(WORK, '_only_%s.txt' % lg), 'w', encoding='utf-8').write('\n'.join(sorted(built)) + '\n')
    print(f'{lg}: built {len(built)} html', flush=True)
    r = subprocess.run([sys.executable, '-u', os.path.join(WORK, 'to_pdf.py'), lg],
                       cwd=BASE, capture_output=True, text=True, encoding='utf-8', errors='replace')
    tail = [l for l in (r.stdout or '').splitlines() if l.strip()][-1:]
    print('   ', tail[0][:90] if tail else 'no output', flush=True)
    if r.returncode != 0:
        print('    !! exit', r.returncode, (r.stderr or '')[-200:], flush=True)
print('DONE', flush=True)
