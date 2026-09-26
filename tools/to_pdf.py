# -*- coding: utf-8 -*-
"""Convert language HTML files to PDF via Edge headless.

Usage: python to_pdf.py <lang> [outdir]
  lang = cn | en | fr | es | pt | ar | sw | hi | bn | id | ru
  HTML read from work/<lang>_html/, PDFs written to outdir (default pdf/)
"""
import os, glob, subprocess, urllib.parse, sys, time

sys.stdout.reconfigure(encoding='utf-8')
BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
JOBS = int(os.environ.get('PDF_JOBS', '4'))

def convert(src_html, out_pdf, slot=0):
    full = os.path.abspath(src_html)
    url = 'file:///' + urllib.parse.quote(full.replace(os.sep, '/'))
    out = os.path.abspath(out_pdf)
    # a private profile per worker keeps parallel headless runs from fighting
    # over the same user-data-dir (which makes startup crawl)
    # a unique profile per run: a shared one hits a stale lock file and Edge
    # aborts with a ProcessSingleton error
    profile = os.path.join(os.environ.get('TEMP', r'C:\tmp'),
                           'edgepdf_%d_%d_%d' % (slot, os.getpid(), int(time.time() * 1000) % 100000))
    # drop any previous output first: otherwise a failed run would still look
    # successful just because the old file is sitting there
    if os.path.exists(out):
        os.remove(out)
    # NB: headless Edge writes the PDF within seconds but then keeps running,
    # so subprocess.run() would block for minutes.  Poll for the file instead
    # and kill the browser as soon as the output is complete.
    p = subprocess.Popen([EDGE, '--headless', '--disable-gpu', '--no-pdf-header-footer',
                          '--no-first-run', '--no-default-browser-check',
                          '--disable-extensions', '--disable-background-networking',
                          '--user-data-dir=' + profile,
                          '--print-to-pdf=' + out, url],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ok = False
    end = time.time() + 180
    while time.time() < end:
        if os.path.exists(out):
            s1 = os.path.getsize(out)
            time.sleep(0.4)
            if os.path.exists(out) and os.path.getsize(out) == s1 and s1 > 20000:
                ok = True
                break
        if p.poll() is not None and not os.path.exists(out):
            break
        time.sleep(0.3)
    # kill the whole tree: renderer/GPU children survive a bare Popen.kill()
    # and, left behind, they pile up and starve the machine
    try:
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(p.pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
    except Exception:
        try:
            p.kill()
        except Exception:
            pass
    try:
        p.wait(timeout=10)
    except Exception:
        pass
    import shutil
    shutil.rmtree(profile, ignore_errors=True)
    if not ok:
        print('FAIL', src_html)
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
        # only the newline is stripped: a >100-char title can legitimately end
        # in a space, and stripping it would stop the filename matching
        only = {l.rstrip('\n') for l in open(only_file, encoding='utf-8') if l.strip()}
        files = [f for f in files if os.path.splitext(os.path.basename(f))[0] in only]
        print('filter on:', len(files), 'files')
    suffix = '' if lang == 'cn' else '_' + lang
    jobs = []
    for f in files:
        name = os.path.splitext(os.path.basename(f))[0]
        jobs.append((f, os.path.join(outdir, name + suffix + '.pdf'), name))
    from concurrent.futures import ThreadPoolExecutor
    results = [False] * len(jobs)

    def work(i):
        src, out, name = jobs[i]
        print('converting:', name[:44], flush=True)
        results[i] = convert(src, out, slot=i % JOBS)
        print(('  OK ' if results[i] else '  FAILED ') + name[:40], flush=True)

    with ThreadPoolExecutor(max_workers=JOBS) as ex:
        list(ex.map(work, range(len(jobs))))
    ok_count = sum(results)
    print(f'{ok_count}/{len(files)} done for {lang} (jobs={JOBS})')
