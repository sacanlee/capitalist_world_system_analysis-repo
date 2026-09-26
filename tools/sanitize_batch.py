# -*- coding: utf-8 -*-
"""Keyword sanitisation for a batch of new articles (generic version).

Usage: python sanitize_batch.py <cn-title> [<cn-title> ...]

Rules (Chinese), see CLAUDE.md:
    南方大国 / 天竺 / 南大        -> 印度
    东方大国 / 龙国 / 东大        -> 中国
    西方大国 / 米国 / 西大        -> 美国
    欧国                          -> 欧盟
    GOV / ZF (standalone)         -> 政府
    两天周末 / 周末两天            -> 双休

Applied to work/txt, work/cn_html and work/notes; the three files are renamed
when the title itself changes.  Tokens glued to ASCII letters/digits/`%`
(e.g. inside percent-encoded URLs or `data-pid="9MIbQZFo"`) are left alone.
"""
import io, os, re, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
ASCII_GUARD = r'(?<![A-Za-z0-9%%])%s(?![A-Za-z0-9])'

RULES = [
    ('南方大国', '印度'),
    ('天竺', '印度'),
    ('南大', '印度'),
    ('东方大国', '中国'),
    ('龙国', '中国'),
    ('东大', '中国'),
    ('西方大国', '美国'),
    ('米国', '美国'),
    ('西大', '美国'),
    ('欧国', '欧盟'),
    ('两天周末', '双休'),
    ('周末两天', '双休'),
]
RULES = [(re.compile(ASCII_GUARD % re.escape(a)), b) for a, b in RULES]
RULES.append((re.compile(ASCII_GUARD % 'GOV'), '政府'))
RULES.append((re.compile(ASCII_GUARD % 'ZF'), '政府'))


def sub(text):
    counts = {}
    for rx, rep in RULES:
        text, n = rx.subn(rep, text)
        if n:
            counts[rx.pattern] = n
    return text, counts


def main():
    titles = sys.argv[1:]
    if not titles:
        print('usage: python sanitize_batch.py <cn-title> [...]')
        sys.exit(1)
    renames = []
    for orig in titles:
        new = sub(orig)[0]
        total = {}
        for sub_dir, ext in (('txt', '.txt'), ('cn_html', '.html')):
            p = os.path.join(BASE, 'work', sub_dir, orig + ext)
            s = open(p, encoding='utf-8').read()
            s2, c = sub(s)
            for k, v in c.items():
                total[k] = total.get(k, 0) + v
            open(p, 'w', encoding='utf-8').write(s2)
        p = os.path.join(BASE, 'work', 'notes', orig + '.json')
        d = json.load(open(p, encoding='utf-8'))
        d['title'] = new
        for note in d.get('notes', []):
            note['text'] = sub(note['text'])[0]
        json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'{orig[:34]:36s} -> {new[:34]:36s} {total}')
        renames.append((orig, new))
    for orig, new in renames:
        if orig == new:
            continue
        for sub_dir, ext in (('txt', '.txt'), ('cn_html', '.html'), ('notes', '.json')):
            src = os.path.join(BASE, 'work', sub_dir, orig + ext)
            dst = os.path.join(BASE, 'work', sub_dir, new + ext)
            if os.path.exists(dst):
                os.remove(dst)
            os.rename(src, dst)
        print('renamed:', orig, '->', new)


if __name__ == '__main__':
    main()
