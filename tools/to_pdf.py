# -*- coding: utf-8 -*-
"""Convert language HTML files to PDF via Edge headless.

Usage: python to_pdf.py <lang> [outdir]
  lang = cn | en | fr | es | pt | ar | sw | hi | bn | id | ru
  HTML read from work/<lang>_html/, PDFs written to outdir (default pdf/)
"""
import os, glob, subprocess, urllib.parse, sys

sys.stdout.reconfigure(encoding='utf-8')
BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def convert(src_html, out_pdf):
    full = os.path.abspath(src_html)
    url = 'file:///' + urllib.parse.quote(full.replace(os.sep, '/'))
    out = os.path.abspath(out_pdf)
    r = subprocess.run([EDGE, '--headless', '--disable-gpu', '--no-pdf-header-footer',
                        '--print-to-pdf=' + out, url],
                       capture_output=True, text=True, errors='replace')
    ok = os.path.exists(out) and os.path.getsize(out) > 20000
    if not ok:
        print('FAIL', src_html, r.returncode, r.stderr[:200])
    return ok

if __name__ == '__main__':
    lang = sys.argv[1] if len(sys.argv) > 1 else 'cn'
    outdir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BASE, 'pdf')
    os.makedirs(outdir, exist_ok=True)
    srcdir = os.path.join(BASE, 'work', lang + '_html')
    if not os.path.isdir(srcdir):
        print('no such dir', srcdir)
        sys.exit(1)
    files = sorted(glob.glob(os.path.join(srcdir, '*.html')))
    only_file = os.path.join(BASE, 'work', '_only_%s.txt' % lang)
    if os.path.exists(only_file):
        only = {l.strip() for l in open(only_file, encoding='utf-8') if l.strip()}
        files = [f for f in files if os.path.splitext(os.path.basename(f))[0] in only]
        print('filter on:', len(files), 'files')
    suffix = '' if lang == 'cn' else '_' + lang
    ok_count = 0
    for f in files:
        name = os.path.splitext(os.path.basename(f))[0]
        out = os.path.join(outdir, name + suffix + '.pdf')
        print('converting:', name[:44])
        if convert(f, out):
            ok_count += 1
            print('  OK', os.path.getsize(out))
        else:
            print('  FAILED')
    print(f'{ok_count}/{len(files)} done for {lang}')
