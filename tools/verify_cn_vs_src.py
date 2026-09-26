# -*- coding: utf-8 -*-
"""Authoritative completeness check: every block of the saved web page must
appear in the Chinese txt (and therefore in the Chinese PDF).

For each source HTML we walk the answer/article container, take every
paragraph, heading, list item and caption, strip <sup> citations and all
whitespace, and require it to be a substring of the CN txt (with [n] markers
and [IMAGE n] markers removed).  Anything not found is reported as MISSING.
"""
import io, os, re, sys, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from lxml import html as lh

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
TXT = os.path.join(BASE, 'work', 'txt')
AUTHOR = '最最遥远的路'


def content_of(tree):
    for div in tree.iter('div'):
        cls = div.get('class') or ''
        if 'AnswerItem' in cls and AUTHOR in (div.get('data-zop') or ''):
            for el in div.iter():
                if el.get('itemprop') == 'text':
                    return el
    c = tree.find_class('Post-RichTextContainer')
    if c:
        return c[0]
    best, bl = None, 0
    for el in tree.iter():
        if el.get('itemprop') == 'text':
            n = len(el.text_content())
            if n > bl:
                bl, best = n, el
    return best


def strip_sups(el):
    """text_content() with only citation <sup data-numero> dropped — those are
    the ones the pipeline turns into [n] markers.  Plain <sup>a/b/c</sup>
    markers are kept as literal text by the pipeline, so keep them here too."""
    parts = []
    if el.text:
        parts.append(el.text)
    for ch in el:
        if isinstance(ch.tag, str) and ch.tag == 'sup' and ch.get('data-numero') is not None:
            pass
        else:
            parts.append(strip_sups(ch))
        if ch.tail:
            parts.append(ch.tail)
    return ''.join(parts)


ASCII_GUARD = r'(?<![A-Za-z0-9%%])%s(?![A-Za-z0-9])'
_RULES = [('南方大国', '印度'), ('天竺', '印度'), ('南大', '印度'),
          ('东方大国', '中国'), ('龙国', '中国'), ('东大', '中国'),
          ('西方大国', '美国'), ('米国', '美国'), ('西大', '美国'),
          ('欧国', '欧盟'), ('两天周末', '双休'), ('周末两天', '双休')]
# keep in step with sanitize_batch.py: the ASCII guard applies to GOV/ZF only
_RULES = [(re.compile(re.escape(a)), b) for a, b in _RULES]
_RULES += [(re.compile(ASCII_GUARD % 'GOV'), '政府'), (re.compile(ASCII_GUARD % 'ZF'), '政府')]


def sanitize(s):
    """both sides are sanitised, so old-corpus files stay comparable"""
    for rx, rep in _RULES:
        s = rx.sub(rep, s)
    return s


def norm(s):
    s = re.sub(r'\s+', '', s)
    return re.sub(r'\[\d{1,3}\]', '', s)   # citation markers exist on both sides


def txt_body(title):
    p = os.path.join(TXT, title + '.txt')
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'\[IMAGE \d+\]', '', s)
    s = re.sub(r'\[图注:', '', s)
    s = re.sub(r'\[\d{1,3}\]', '', s)     # citation markers
    s = s.replace('[元信息]', '').replace('[表格]', '')
    return norm(sanitize(s))


bad = 0
checked = 0
for f in sorted(glob.glob(os.path.join(BASE, 'articles_in_chinese', '**', '*.html'), recursive=True)):
    tree = lh.fromstring(open(f, encoding='utf-8', errors='replace').read(),
                         parser=lh.HTMLParser(encoding='utf-8'))
    cont = content_of(tree)
    if cont is None:
        continue
    title_el = tree.find_class('Post-Title')
    og = ''
    for m in tree.iter('meta'):
        if m.get('property') == 'og:title':
            og = m.get('content', '')
            break
    title = title_el[0].text_content().strip() if title_el else \
        re.sub(r'\s*-\s*最最遥远的路\s*的\s*回答\s*$', '', og).strip()
    raw = re.sub(r'[\\/:*?"<>|\r\n]', '_', title).strip()[:100]
    # the nine new-batch articles were renamed after slang sanitisation, so try
    # the raw stem first and fall back to the sanitised one
    for cand in (raw, sanitize(raw)[:100]):
        if os.path.exists(os.path.join(TXT, cand + '.txt')):
            title = cand
            break
    else:
        print(f'SKIP (no txt)  {raw[:60]}')
        continue
    checked += 1
    body = txt_body(title)
    missing = []
    for el in cont.iter():
        if not isinstance(el.tag, str) or el.tag not in ('p', 'h2', 'h3', 'li', 'blockquote', 'figcaption'):
            continue
        t = norm(sanitize(strip_sups(el)))
        if len(t) < 4:
            continue
        if t not in body:
            missing.append(t)
    if missing:
        bad += 1
        tot = sum(len(m) for m in missing)
        print(f'MISSING  {title[:44]:46s} blocks={len(missing):3d} chars={tot:5d}')
        for m in missing[:3]:
            print('      ->', m[:90])
    else:
        print(f'OK       {title[:44]}')
print('=' * 74)
print(f'checked={checked}  articles_with_missing_text={bad}')
