# -*- coding: utf-8 -*-
"""Verify translated articles against the Chinese source.

Usage:
    python verify_new.py                 # full corpus (all titles found in work/txt)
    python verify_new.py <title> [...]   # only these Chinese titles

Checks per language/file:
  * first line is a '# ' title
  * body [n] note markers match the Chinese notes json numbers exactly
  * [NOTES] block numbers match the json (when the article has notes)
  * [IMAGE n] count matches the Chinese source
"""
import os, io, sys, re, json, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
WORK = os.path.join(BASE, 'work')

LANGS = [('cn', 'txt'), ('en', 'en_txt'), ('es', 'es_txt'), ('pt', 'pt_txt'),
         ('fr', 'fr_txt'), ('ru', 'ru_txt'), ('ar', 'ar_txt'),
         ('sw', 'sw_txt'), ('hi', 'hi_txt'), ('bn', 'bn_txt'), ('id', 'id_txt')]


def split_notes(text):
    i = text.find('\n[NOTES]')
    if i < 0:
        return text, None
    return text[:i], text[i:]


def body_numbers(body):
    return [int(x) for x in re.findall(r'\[(\d{1,3})\]', body)]


def main():
    titles = sys.argv[1:]
    if not titles:
        titles = sorted(os.path.splitext(os.path.basename(f))[0]
                        for f in glob.glob(os.path.join(WORK, 'txt', '*.txt')))
    cn_img = {}
    cn_notes = {}
    for t in titles:
        s = open(os.path.join(WORK, 'txt', t + '.txt'), encoding='utf-8').read()
        body, _ = split_notes(s)
        cn_img[t] = len(re.findall(r'\[IMAGE (\d+)\]', body))
        j = json.load(open(os.path.join(WORK, 'notes', t + '.json'), encoding='utf-8'))
        cn_notes[t] = [n['num'] for n in j['notes']]

    fails = 0
    for code, sub in LANGS:
        print('=' * 70)
        print('LANG', code, '->', sub)
        for t in titles:
            p = os.path.join(WORK, sub, t + '.txt')
            if not os.path.exists(p):
                print(f'  MISSING  {t}')
                fails += 1
                continue
            s = open(p, encoding='utf-8').read()
            first = s.split('\n', 1)[0]
            body, nblock = split_notes(s)
            bn = body_numbers(body)
            expect = cn_notes[t]
            prob = []
            if not first.startswith('# '):
                prob.append('no-title')
            if sorted(bn) != sorted(expect):
                prob.append(f'body[bracket]={sorted(bn)} expected={sorted(expect)}')
            if bn != sorted(bn):
                prob.append('body order not ascending')
            if expect and code != 'cn':
                if nblock is None:
                    prob.append('missing [NOTES] block')
                else:
                    nn = [int(x) for x in re.findall(r'^\[(\d{1,3})\]', nblock, re.M)]
                    if nn != expect:
                        prob.append(f'notes={nn} expected={expect}')
            nimg = len(re.findall(r'\[IMAGE (\d+)\]', body))
            if nimg != cn_img[t]:
                prob.append(f'imgs={nimg} expected={cn_img[t]}')
            status = 'OK  ' if not prob else 'FAIL'
            if prob:
                fails += 1
            print(f'  {status} {t[:36]:38s} title={first[2:][:34] if first.startswith("# ") else "?"}')
            for p_ in prob:
                print('        -', p_)
    print('=' * 70)
    print('TOTAL', 'ALL OK' if not fails else f'{fails} FAIL')


if __name__ == '__main__':
    main()
