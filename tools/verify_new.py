# -*- coding: utf-8 -*-
"""Verify the 8 new articles across all languages.

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

CN_TITLES = [
    '关于双休问题的回答',
    '龙的崛起：资本主义世界体系中的中国',
    '2055年前，还有哪些国家有可能成为发达国家？',
    'AI编程是否会取代全部程序员？看看业界的实际情况',
    '完全自给自足的经济体是否还可能？',
    '改良主义的前景',
    '深入理解资本主义的长波周期',
    '阶级斗争对资本主义长波周期的影响',
]

LANGS = [('cn', 'txt'), ('en', 'en_txt'), ('es', 'es_txt'), ('pt', 'pt_txt'),
         ('fr', 'fr_txt'), ('ru', 'ru_txt'), ('ar', 'ar_txt')]


def split_notes(text):
    i = text.find('\n[NOTES]')
    if i < 0:
        return text, None
    return text[:i], text[i:]


def body_numbers(body):
    return [int(x) for x in re.findall(r'\[(\d{1,3})\]', body)]


def main():
    cn_img = {}
    cn_notes = {}
    for t in CN_TITLES:
        s = open(os.path.join(WORK, 'txt', t + '.txt'), encoding='utf-8').read()
        body, _ = split_notes(s)
        cn_img[t] = len(re.findall(r'\[IMAGE (\d+)\]', body))
        j = json.load(open(os.path.join(WORK, 'notes', t + '.json'), encoding='utf-8'))
        cn_notes[t] = [n['num'] for n in j['notes']]

    for code, sub in LANGS:
        print('=' * 70)
        print('LANG', code, '->', sub)
        for t in CN_TITLES:
            p = os.path.join(WORK, sub, t + '.txt')
            if not os.path.exists(p):
                print(f'  MISSING  {t}')
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
            print(f'  {status} {t[:36]:38s} title={first[2:][:34] if first.startswith("# ") else "?"}')
            for p_ in prob:
                print('        -', p_)


if __name__ == '__main__':
    main()
