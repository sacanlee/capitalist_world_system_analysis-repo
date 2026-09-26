# -*- coding: utf-8 -*-
"""Refresh articles/ and repo/articles/ from pdf/.

For every PDF already published under articles/<Lang>/<category>/ we copy the
newer build from pdf/<stem><suffix>.pdf over it.  Nothing is added or removed,
so the published tree keeps its exact structure and filenames.
"""
import io, os, shutil, sys, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
PDF = os.path.join(BASE, 'pdf')
SUFFIX = {'Chinese': '', 'English': '_en', 'Français': '_fr', 'Español': '_es',
          'português': '_pt', 'العربية': '_ar', 'Русский': '_ru',
          'Kiswahili': '_sw', 'हिन्दी': '_hi', 'বাংলা': '_bn',
          'Bahasa Indonesia': '_id'}

copied = stale = 0
for root in (os.path.join(BASE, 'articles'), os.path.join(BASE, 'repo', 'articles')):
    if not os.path.isdir(root):
        continue
    for lang in sorted(os.listdir(root)):
        langdir = os.path.join(root, lang)
        if not os.path.isdir(langdir) or lang not in SUFFIX:
            continue
        suff = SUFFIX[lang]
        for cat in sorted(os.listdir(langdir)):
            catdir = os.path.join(langdir, cat)
            if not os.path.isdir(catdir):
                continue
            for name in sorted(os.listdir(catdir)):
                if not name.lower().endswith('.pdf'):
                    continue
                stem = name[:-4]
                src = os.path.join(PDF, stem + suff + '.pdf')
                dst = os.path.join(catdir, name)
                if not os.path.exists(src):
                    stale += 1
                    print('no rebuild for', lang, name[:60])
                    continue
                if os.path.getsize(src) == os.path.getsize(dst) and \
                        open(src, 'rb').read() == open(dst, 'rb').read():
                    continue
                shutil.copy2(src, dst)
                copied += 1
print('=' * 70)
print('refreshed:', copied, ' without a rebuilt source:', stale)
