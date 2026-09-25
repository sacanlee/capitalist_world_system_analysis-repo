# -*- coding: utf-8 -*-
"""Keyword sanitisation for the 8 new articles (2025-09-25 batch).

Rules (Chinese):
    南方大国 / 天竺      -> 印度
    东方大国 / 东大      -> 中国
    西方大国 / 西大      -> 美国
    GOV / ZF (standalone) -> 政府
    两天周末 / 周末两天   -> 双休

Applied to work/txt, work/cn_html and work/notes, then the three files are
renamed to the sanitised title.  URLs / percent-encoded tokens are left alone.
"""
import os, io, sys, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
WORD = '(?<![A-Za-z0-9%%])%s(?![A-Za-z0-9])'

RULES = [
    (re.compile(r'南方大国'), '印度'),
    (re.compile(r'西方大国'), '美国'),
    (re.compile(r'东方大国'), '中国'),
    (re.compile(r'天竺'), '印度'),
    (re.compile(r'西大'), '美国'),
    (re.compile(r'东大'), '中国'),
    (re.compile(WORD % 'GOV'), '政府'),
    (re.compile(WORD % 'ZF'), '政府'),
    (re.compile(r'两天周末'), '双休'),
    (re.compile(r'周末两天'), '双休'),
]

ORIG_TITLES = [
    '关于两天周末问题的回答',
    '龙的崛起：资本主义世界体系中的东方大国',
    '2055年前，还有哪些国家有可能成为发达国家？',
    'AI编程是否会取代全部程序员？看看业界的实际情况',
    '完全自给自足的经济体是否还可能？',
    '改良主义的前景',
    '深入理解资本主义的长波周期',
    '阶级斗争对资本主义长波周期的影响',
]


def sub(text):
    counts = {}
    for rx, rep in RULES:
        text, n = rx.subn(rep, text)
        if n:
            counts[rx.pattern] = n
    return text, counts


def new_title(orig):
    return sub(orig)[0]


def main():
    renames = []
    for orig in ORIG_TITLES:
        new = new_title(orig)
        total = {}
        # ---- txt ----
        p = os.path.join(BASE, 'work', 'txt', orig + '.txt')
        s = open(p, encoding='utf-8').read()
        s2, c = sub(s)
        for k, v in c.items():
            total[k] = total.get(k, 0) + v
        open(p, 'w', encoding='utf-8').write(s2)
        # ---- cn_html ----
        p = os.path.join(BASE, 'work', 'cn_html', orig + '.html')
        s = open(p, encoding='utf-8').read()
        s2, c = sub(s)
        for k, v in c.items():
            total[k] = total.get(k, 0) + v
        open(p, 'w', encoding='utf-8').write(s2)
        # ---- notes json ----
        p = os.path.join(BASE, 'work', 'notes', orig + '.json')
        d = json.load(open(p, encoding='utf-8'))
        d['title'] = new
        for note in d.get('notes', []):
            note['text'] = sub(note['text'])[0]
        json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'{orig[:32]:34s} -> {new[:34]:36s} {total}')
        renames.append((orig, new))
    # ---- rename so file stems match the sanitised titles ----
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
