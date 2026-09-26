# -*- coding: utf-8 -*-
"""Confirm the rebuilt translated PDFs carry the recovered text.

Takes distinctive numeric tokens from the recovered Chinese hunks and requires
them in the PDF text — the same signal check_numbers.py uses on the txt, read
back out of the PDF.
"""
import io, glob, json, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pymupdf

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
WORK = os.path.join(BASE, 'work')
DIGITS = {'ar': str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'),
          'hi': str.maketrans('०१२३४५६७८९', '0123456789'),
          'bn': str.maketrans('০১২৩৪৫৬৭৮৯', '0123456789')}
MAG = '亿万千百'

SAMPLE = [
    ('撒南非洲的工业化', ['en', 'fr', 'ru', 'hi', 'bn']),
    ('天竺的自然资源与工业化', ['pt', 'ar', 'sw', 'id']),
    ('资本主义世界体系的兴衰（一）：资本主义世界体系生产方式演进的三个阶段', ['en', 'pt', 'sw']),
    ('资本主义世界体系的兴衰（三）：世界体系三个阶段的矛盾分析', ['ru', 'ar', 'hi']),
    ('印尼资本主义的发展', ['es', 'bn', 'id']),
    ('四口之家，一人上班，有房有车，美国工人真有过这样的好日子吗？', ['es', 'ru', 'fr']),
]


def tokens(cn):
    out = set()
    for m in re.finditer(r'\d[\d,，.\u00a0]*', cn):
        d = re.sub(r'\D', '', m.group(0))
        if len(d) < 3 or cn[m.end():m.end() + 1] in MAG:
            continue
        if len(d) == 4 and not ('1800' <= d <= '2100'):
            continue
        out.add(d)
    return out


def sanitize_name(s):
    s = re.sub(r'[\\/:*?"<>|\r\n]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()[:100]


def pdf_for(lang, cn_title):
    p = os.path.join(WORK, lang + '_txt', cn_title + '.txt')
    if not os.path.exists(p):
        return None
    first = open(p, encoding='utf-8').readline().strip()
    stem = sanitize_name(first[2:].strip() if first.startswith('# ') else cn_title)
    cand = os.path.join(BASE, 'pdf', stem + '_' + lang + '.pdf')
    return cand if os.path.exists(cand) else None


ok = bad = skip = 0
for title, langs in SAMPLE:
    hp = os.path.join(WORK, '_hunks', title + '.json')
    d = json.load(open(hp, encoding='utf-8'))
    toks = tokens(''.join(h['inserted'] for h in d['hunks']))
    for lg in langs:
        pdf = pdf_for(lg, title)
        if not pdf:
            print('SKIP', lg, title[:28], '(no pdf)')
            skip += 1
            continue
        txt = ''.join(pg.get_text() for pg in pymupdf.open(pdf))
        txt = re.sub(r'\D', '', txt.translate(DIGITS.get(lg, {})))
        miss = sorted(t for t in toks if t not in txt)
        if miss:
            bad += 1
            print(f'MISS {lg:3s} {title[:28]:30s} {miss[:8]}')
        else:
            ok += 1
            print(f'OK   {lg:3s} {title[:28]:30s} ({len(toks)} tokens present)')
print('=' * 70)
print(f'ok={ok} bad={bad} skip={skip}')
