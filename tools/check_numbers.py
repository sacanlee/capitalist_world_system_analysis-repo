# -*- coding: utf-8 -*-
"""Language-independent completeness check for the patched translations.

The Chinese text recovered by the sup.tail fix is full of numbers (dates,
tonnages, ranges).  A translation either contains them or it does not, so for
every (article, language) we take the numeric tokens out of the recovered
Chinese and look for them in the target file.  Numbers are compared with
separators stripped, and both Western and local digit sets are accepted.

Anything still missing after patching is a real gap → reported.
"""
import io, os, re, sys, glob, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
WORK = os.path.join(BASE, 'work')
LANGS = ['en', 'es', 'pt', 'fr', 'ru', 'ar', 'sw', 'hi', 'bn', 'id']

DIGITS = {
    'ar': str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'),
    'hi': str.maketrans('०१२३४५६७८९', '0123456789'),
    'bn': str.maketrans('০১২৩৪৫৬৭৮৯', '0123456789'),
}
# Chinese unit words that carry a quantity without an Arabic numeral
CN_UNITS = re.compile(r'(亿|万亿|万吨|亿吨|万|千|百|百分之)')


def norm_numbers(s, lang):
    if lang in DIGITS:
        s = s.translate(DIGITS[lang])
    # thousands separators vary by language (10,169 / 10 169 / 10.169), so drop
    # every non-digit entirely — a presence check only needs the digits
    return re.sub(r'\D', '', s)


MAGNITUDE = '亿万千百'


def tokens(cn):
    """Distinctive numeric tokens in the recovered Chinese.

    A number written in Chinese with a magnitude word (5360亿, 90万) is
    restated in translation as a different numeral ("536 billion"), so those
    are useless as keys.  Years survive translation verbatim and bare numbers
    with 3+ digits (ranges, tonnages) mostly do too, so keep only those.
    """
    out = set()
    for m in re.finditer(r'\d[\d,，.\u00a0]*', cn):
        t = m.group(0)
        digits = re.sub(r'\D', '', t)
        if len(digits) < 3:
            continue
        nxt = cn[m.end():m.end() + 1]
        if nxt in MAGNITUDE:
            continue
        if len(digits) == 4 and not ('1800' <= digits <= '2100'):
            continue
        out.add(digits)
    return out


def main():
    rows = []
    for hp in sorted(glob.glob(os.path.join(WORK, '_hunks', '*.json'))):
        d = json.load(open(hp, encoding='utf-8'))
        t = d['title']
        # per hunk, never on the concatenation — adjacent fragments would
        # otherwise fuse into numbers that exist nowhere in the source
        toks = set()
        for h in d['hunks']:
            toks |= tokens(h['inserted'])
        if not toks:
            continue
        for lg in LANGS:
            p = os.path.join(WORK, lg + '_txt', t + '.txt')
            if not os.path.exists(p):
                continue
            body = norm_numbers(open(p, encoding='utf-8').read(), lg)
            miss = sorted(k for k in toks if k not in body)
            rows.append((len(miss), len(toks), lg, t, miss))

    rows.sort(reverse=True)
    bad = 0
    print(f'{"miss":>4s}/{"tot":<4s} lang  article')
    for n, tot, lg, t, miss in rows:
        if n:
            bad += 1
            print(f'{n:4d}/{tot:<4d} {lg:5s} {t[:52]}')
            print(f'          missing: {miss[:12]}')
    print('=' * 74)
    print(f'{len(rows)} (article,language) checks; {bad} still missing numbers')
    if not bad:
        print('ALL RECOVERED CONTENT PRESENT')


if __name__ == '__main__':
    main()
