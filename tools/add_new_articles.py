# -*- coding: utf-8 -*-
"""Add ONLY the 8 new (2026-09) articles to articles/ and repo/articles/.

Non-destructive: leaves the existing 444 published PDFs untouched.
New articles exist in 7 languages (Chinese + en/es/pt/fr/ru/ar); the other four
published languages have no translation of this batch yet.
"""
import os, io, re, sys, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
PDF = os.path.join(BASE, 'pdf')

CATS = {
    'world-system-mechanisms': [
        '龙的崛起：资本主义世界体系中的中国',
        '改良主义的前景',
        '完全自给自足的经济体是否还可能？',
        '深入理解资本主义的长波周期',
        '阶级斗争对资本主义长波周期的影响',
    ],
    'southern-capitalism': [
        '关于双休问题的回答',
    ],
    'multipolar-world': [
        '2055年前，还有哪些国家有可能成为发达国家？',
    ],
    'other-observations': [
        'AI编程是否会取代全部程序员？看看业界的实际情况',
    ],
}

# display dir name -> (pdf suffix, txt subdir)
LANGS = [
    ('Chinese', '', 'txt'),
    ('English', '_en', 'en_txt'),
    ('Français', '_fr', 'fr_txt'),
    ('Español', '_es', 'es_txt'),
    ('português', '_pt', 'pt_txt'),
    ('العربية', '_ar', 'ar_txt'),
    ('Русский', '_ru', 'ru_txt'),
]


def sanitize_name(s):
    s = re.sub(r'[\\/:*?"<>|\r\n]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()[:100]


def title_of(lang_sub, cn):
    p = os.path.join(BASE, 'work', lang_sub, cn + '.txt')
    first = open(p, encoding='utf-8').readline().strip()
    return first[2:].strip() if first.startswith('# ') else cn


def main():
    added, missing = 0, []
    for disp, suffix, sub in LANGS:
        for cat, titles in CATS.items():
            for cn in titles:
                name = sanitize_name(title_of(sub, cn))
                src = os.path.join(PDF, name + suffix + '.pdf')
                if not os.path.exists(src):
                    missing.append((disp, cn, src))
                    continue
                for root in (os.path.join(BASE, 'articles'),
                             os.path.join(BASE, 'repo', 'articles')):
                    d = os.path.join(root, disp, cat)
                    os.makedirs(d, exist_ok=True)
                    dst = os.path.join(d, name + '.pdf')
                    shutil.copy2(src, dst)
                    added += 1
                    print('%-14s %-24s %s  (%d KB)' % (disp, cat, name[:52], os.path.getsize(dst) // 1024))
    print('\ncopied:', added)
    if missing:
        print('MISSING', len(missing))
        for m in missing:
            print('  ', m)


if __name__ == '__main__':
    main()
