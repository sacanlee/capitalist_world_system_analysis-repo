# -*- coding: utf-8 -*-
"""Audit the patched translations against the pre-patch backup.

Contract the patching agents must honour: ADD text only.  So diffing the
backup against the patched file must yield nothing but 'equal' and 'insert'
opcodes.  Any delete/replace is reported as a violation.

Usage: python check_patched.py [lang ...]      (default: all ten)
"""
import io, os, sys, glob, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
WORK = os.path.join(BASE, 'work')
BAK = r"C:\tmp\lang_backup"
LANGS = ['en', 'es', 'pt', 'fr', 'ru', 'ar', 'sw', 'hi', 'bn', 'id']


def expected_insertions(title):
    """approximate expected CN length of the patch, from the hunk list"""
    p = os.path.join(WORK, '_hunks', title + '.json')
    if not os.path.exists(p):
        return 0
    import json
    return json.load(open(p, encoding='utf-8'))['added']


def main():
    langs = sys.argv[1:] or LANGS
    problems = []
    for lg in langs:
        cur_dir = os.path.join(WORK, lg + '_txt')
        bak_dir = os.path.join(BAK, lg + '_txt')
        if not os.path.isdir(bak_dir):
            print(f'!! no backup for {lg}')
            continue
        print('=' * 74)
        print('LANG', lg)
        for bf in sorted(glob.glob(os.path.join(bak_dir, '*.txt'))):
            name = os.path.basename(bf)
            cf = os.path.join(cur_dir, name)
            if not os.path.exists(cf):
                print(f'  MISSING now: {name}')
                problems.append((lg, name, 'file disappeared'))
                continue
            old = open(bf, encoding='utf-8').read()
            new = open(cf, encoding='utf-8').read()
            if old == new:
                continue
            sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
            ops, dels, reps, ins_chars = {}, 0, 0, 0
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                ops[tag] = ops.get(tag, 0) + 1
                if tag == 'delete':
                    dels += i2 - i1
                elif tag == 'replace':
                    reps += max(i2 - i1, j2 - j1)
                    print(f'    REPLACE {i2-i1}->{j2-j1}: {old[i1:i2][:60]!r} => {new[j1:j2][:60]!r}')
                elif tag == 'insert':
                    ins_chars += j2 - j1
            exp = expected_insertions(name[:-4])
            status = 'OK ' if dels == 0 and reps == 0 else 'FAIL'
            if status == 'FAIL':
                problems.append((lg, name, f'del={dels} rep={reps}'))
            print(f'  {status} {name[:44]:46s} ins={ins_chars:5d} chars  ops={ops}')
    print('=' * 74)
    if problems:
        print('PROBLEMS:', len(problems))
        for p in problems:
            print('  ', p)
    else:
        print('ALL PATCHES ARE PURE INSERTIONS')


if __name__ == '__main__':
    main()
