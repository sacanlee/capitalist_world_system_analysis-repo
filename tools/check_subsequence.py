# -*- coding: utf-8 -*-
"""Insert-only audit without difflib (which blows up on the big articles).

Walks the pre-patch text as a subsequence of the post-patch text: every
character of the old file must still appear, in order.  Characters that cannot
be matched are the (few, declared) punctuation fix-ups; a large count would
mean somebody rewrote or dropped text.

Usage: python check_subsequence.py [lang ...]
"""
import io, os, sys, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
WORK = os.path.join(BASE, 'work')
BAK = r"C:\tmp\lang_backup"
LANGS = ['en', 'es', 'pt', 'fr', 'ru', 'ar', 'sw', 'hi', 'bn', 'id']


def body(text):
    """everything before the [NOTES] block — its lines carry the Chinese
    original, whose rare characters otherwise derail the greedy scan"""
    i = text.find('\n[NOTES]')
    return text if i < 0 else text[:i]


def unmatched(old, new):
    """characters of `old` not found, in order, inside `new` (greedy scan)"""
    i = 0
    n = len(new)
    first_bad = []
    for ch in old:
        j = new.find(ch, i)
        if j < 0:
            first_bad.append(ch)
            if len(first_bad) > 400:
                break
        else:
            i = j + 1
    return first_bad


def main():
    langs = sys.argv[1:] or LANGS
    total_bad = 0
    rows = []
    for lg in langs:
        for bf in sorted(glob.glob(os.path.join(BAK, lg + '_txt', '*.txt'))):
            name = os.path.basename(bf)
            cf = os.path.join(WORK, lg + '_txt', name)
            if not os.path.exists(cf):
                print('MISSING', lg, name)
                continue
            old = body(open(bf, encoding='utf-8').read())
            new = body(open(cf, encoding='utf-8').read())
            if old == new:
                continue
            bad = unmatched(old, new)
            tot = len(bad)
            total_bad += tot
            rows.append((tot, lg, name, ''.join(bad[:14])))
    rows.sort(reverse=True)
    for tot, lg, name, sample in rows:
        flag = 'OK  ' if tot == 0 else ('MIN ' if tot <= 12 else 'CHECK')
        print(f'{flag} {lg:3s} {tot:5d} chars lost  {name[:44]:46s} {sample!r}')
    print('=' * 74)
    print(f'{len(rows)} patched files, {total_bad} unmatched characters total')


if __name__ == '__main__':
    main()
