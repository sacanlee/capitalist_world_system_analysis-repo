# -*- coding: utf-8 -*-
"""Build per-language article HTML from translated txt + notes json + CN html images.

Translated txt format (same markers as work/txt):
  # Title
  [元信息] meta line
  ## h2 / ### h3
  > quote
  [IMAGE n]
  [图注: caption]
  [表格] ... rows with |
  - list item
  inline [n] note markers
  optional trailing block:
  [NOTES]
  [1] translated note text
  [2] translated note text

Usage: python build_lang_html.py <lang>  (lang dirs: work/<lang>_txt -> work/<lang>_html)
"""
import os, glob, re, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from lxml import html as lh

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
CN_HTML = os.path.join(BASE, 'work', 'cn_html')
NOTES = os.path.join(BASE, 'work', 'notes')
AUTHOR_URL = "https://www.zhihu.com/people/zui-zui-yao-yuan-de-lu-32/posts"
AUTHOR_NAME = "最最遥远的路"

LANG_META = {
    'en':  dict(lang='en', dir='ltr', font='Georgia,"Times New Roman",serif', notes_h='Notes',
                footer1='This article was originally published on Zhihu (in Chinese):',
                footer2='Author: 最最遥远的路 · Zhihu profile:'),
    'fr':  dict(lang='fr', dir='ltr', font='Georgia,"Times New Roman",serif', notes_h='Notes',
                footer1="Cet article a été publié à l'origine sur Zhihu (en chinois) :",
                footer2='Auteur : 最最遥远的路 · Profil Zhihu :'),
    'es':  dict(lang='es', dir='ltr', font='Georgia,"Times New Roman",serif', notes_h='Notas',
                footer1='Este artículo fue publicado originalmente en Zhihu (en chino):',
                footer2='Autor: 最最遥远的路 · Perfil de Zhihu:'),
    'pt':  dict(lang='pt', dir='ltr', font='Georgia,"Times New Roman",serif', notes_h='Notas',
                footer1='Este artigo foi publicado originalmente no Zhihu (em chinês):',
                footer2='Autor: 最最遥远的路 · Perfil no Zhihu:'),
    'ar':  dict(lang='ar', dir='rtl', font='"Amiri","Scheherazade New","Traditional Arabic",serif',
                notes_h='الحواشي', footer1='نُشر هذا المقال أصلاً على موقع تشيهو (Zhihu) بالصينية:',
                footer2='المؤلف: 最最遥远的路 · صفحة تشيهو:'),
    'sw':  dict(lang='sw', dir='ltr', font='"Noto Serif","DejaVu Serif",serif', notes_h='Maelezo',
                footer1='Makala hii ilichapishwa awali kwenye Zhihu (kwa Kichina):',
                footer2='Mwandishi: 最最遥远的路 · Ukurasa wa Zhihu:'),
    'hi':  dict(lang='hi', dir='ltr', font='"Noto Serif Devanagari","Mangal",serif', notes_h='टिप्पणियाँ',
                footer1='यह लेख मूल रूप से झीहू (Zhihu) पर (चीनी में) प्रकाशित हुआ था:',
                footer2='लेखक: 最最遥远的路 · झीहू प्रोफ़ाइल:'),
    'bn':  dict(lang='bn', dir='ltr', font='"Noto Serif Bengali","Vrinda",serif', notes_h='টীকা',
                footer1='এই নিবন্ধটি মূলত ঝিহু (Zhihu) -তে (চীনা ভাষায়) প্রকাশিত হয়েছিল:',
                footer2='লেখক: 最最遥远的路 · ঝিহু প্রোফাইল:'),
    'id':  dict(lang='id', dir='ltr', font='Georgia,"Times New Roman",serif', notes_h='Catatan',
                footer1='Artikel ini awalnya diterbitkan di Zhihu (dalam bahasa Tionghoa):',
                footer2='Penulis: 最最遥远的路 · Profil Zhihu:'),
    'ru':  dict(lang='ru', dir='ltr', font='"PT Serif","Times New Roman",serif', notes_h='Примечания',
                footer1='Эта статья изначально была опубликована на Zhihu (на китайском языке):',
                footer2='Автор: 最最遥远的路 · Профиль на Zhihu:'),
}

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def sanitize_name(s):
    s = re.sub(r'[\\/:*?"<>|\r\n]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s[:100]

def css_for(lang, meta):
    dir_rtl = 'body { direction: rtl; }' if meta['dir'] == 'rtl' else ''
    return f"""
body {{ font-family: {meta['font']}; max-width: 760px; margin: 0 auto; padding: 32px 24px; line-height: 1.7; color: #1a1a1a; font-size: 15.5px; {''} }}
{dir_rtl}
h1.article-title {{ font-size: 24px; line-height: 1.35; margin-bottom: 4px; }}
.article-meta {{ color: #888; font-size: 13.5px; margin-bottom: 24px; padding-bottom: 14px; border-bottom: 1px solid #e5e5e5; }}
h2 {{ font-size: 19.5px; margin-top: 32px; }}
h3 {{ font-size: 17px; }}
p {{ margin: 10px 0; text-align: justify; }}
figure {{ margin: 18px 0; text-align: center; }}
figure img {{ max-width: 100%; height: auto; }}
figcaption {{ color: #666; font-size: 12.5px; margin-top: 6px; }}
blockquote {{ margin: 12px 0; padding: 4px 16px; border-left: 4px solid #ddd; color: #333; font-size: 14.5px; }}
table {{ border-collapse: collapse; margin: 12px 0; }}
td, th {{ border: 1px solid #ccc; padding: 4px 9px; font-size: 13.5px; }}
li {{ margin: 3px 0; }}
sup.note-ref {{ color: #175199; font-size: 12px; }}
.notes-section {{ margin-top: 44px; padding-top: 18px; border-top: 1px solid #e5e5e5; }}
.notes-section p.note {{ font-size: 13.5px; color: #333; margin: 8px 0; line-height: 1.65; }}
.notes-section .note-cn {{ display: block; font-size: 12.5px; color: #777; margin-top: 2px; }}
.notes-section .note-url {{ display: block; font-size: 12px; color: #666; margin-top: 1px; }}
.article-footer {{ margin-top: 44px; padding-top: 14px; border-top: 1px solid #e5e5e5; color: #666; font-size: 12.5px; }}
.article-footer .cn {{ display: block; margin-top: 4px; color: #999; font-size: 12px; }}
a {{ color: #175199; text-decoration: none; word-break: break-all; }}
"""

def parse_blocks(text):
    blocks = []
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith('# '):
            blocks.append(('title', line[2:].strip()))
        elif line.startswith('## '):
            blocks.append(('h2', line[3:].strip()))
        elif line.startswith('### '):
            blocks.append(('h3', line[4:].strip()))
        elif line.startswith('> '):
            q = []
            while i < len(lines) and lines[i].startswith('> '):
                q.append(lines[i][2:])
                i += 1
            blocks.append(('quote', '\n'.join(q)))
            continue
        elif line.startswith('[元信息]'):
            blocks.append(('meta', line[len('[元信息]'):].strip()))
        elif line.startswith('[IMAGE '):
            m = re.match(r'\[IMAGE (\d+)\]', line)
            if m:
                blocks.append(('image', int(m.group(1))))
        elif line.startswith('[图注:'):
            blocks.append(('caption', line[4:].strip().rstrip(']').strip()))
        elif line.startswith('[NOTES]'):
            i += 1
            notes = []
            while i < len(lines) and lines[i].strip():
                m = re.match(r'\[(\d+)\]\s*(.*)', lines[i].strip())
                if m:
                    notes.append((int(m.group(1)), m.group(2).strip()))
                i += 1
            blocks.append(('notes', notes))
            continue
        elif line.startswith('[表格]'):
            rows = []
            i += 1
            while i < len(lines) and lines[i].strip() and '|' in lines[i]:
                cells = [c.strip() for c in lines[i].split('|')]
                rows.append(cells)
                i += 1
            blocks.append(('table', rows))
            continue
        elif line.startswith('- '):
            blocks.append(('li', line[2:].strip()))
        else:
            para = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(('#', '> ', '[', '- ')):
                para.append(lines[i].rstrip())
                i += 1
            blocks.append(('p', '\n'.join(para)))
            continue
        i += 1
    return blocks

def fmt_inline(s):
    """escape and convert [n] markers to <sup>"""
    s = esc(s)
    s = re.sub(r'\[(\d{1,3})\]', r'<sup class="note-ref">[\1]</sup>', s)
    return s

def get_image_srcs(cn_html_path):
    tree = lh.fromstring(open(cn_html_path, encoding='utf-8').read())
    return [img.get('src') for img in tree.iter('img') if img.get('src')]

def cn_notes_json(title):
    p = os.path.join(NOTES, title + '.json')
    if os.path.exists(p):
        return json.load(open(p, encoding='utf-8'))
    return None

def build(blocks, img_srcs, cn_notes, meta, title):
    body = [f'<body dir="{meta["dir"]}" lang="{meta["lang"]}">']
    for btype, content in blocks:
        if btype == 'title':
            body.append(f'<h1 class="article-title">{esc(content)}</h1>')
        elif btype == 'meta':
            body.append(f'<div class="article-meta">{esc(content)}</div>')
        elif btype == 'h2':
            body.append(f'<h2>{esc(content)}</h2>')
        elif btype == 'h3':
            body.append(f'<h3>{esc(content)}</h3>')
        elif btype == 'p':
            body.append(f'<p>{fmt_inline(content)}</p>')
        elif btype == 'quote':
            body.append(f'<blockquote>{fmt_inline(content)}</blockquote>')
        elif btype == 'li':
            body.append(f'<ul><li>{fmt_inline(content)}</li></ul>')
        elif btype == 'image':
            n = content
            if n - 1 < len(img_srcs):
                body.append(f'<figure><img src="{img_srcs[n-1]}" alt="Figure {n}"></figure>')
            else:
                print('  ! image', n, 'not found in', title)
        elif btype == 'caption':
            body.append(f'<figcaption>{esc(content)}</figcaption>')
        elif btype == 'table':
            if not content:
                continue
            header = content[0]
            rows = content[1:]
            h = ''.join(f'<th>{esc(c)}</th>' for c in header)
            r = ''.join('<tr>' + ''.join(f'<td>{esc(c)}</td>' for c in row) + '</tr>' for row in rows)
            body.append(f'<table><tr>{h}</tr>{r}</table>')
        elif btype == 'notes':
            # bilingual notes section
            body.append(f'<div class="notes-section"><h2>{meta["notes_h"]}</h2>')
            nmap = {n['num']: n for n in (cn_notes['notes'] if cn_notes else [])}
            for num, translated in content:
                cn = nmap.get(num)
                body.append('<p class="note">')
                body.append(f'<sup class="note-ref">[{num}]</sup> {fmt_inline(translated)}')
                if cn and cn.get('text'):
                    body.append(f'<span class="note-cn">中文原文：{esc(cn["text"])}</span>')
                if cn and cn.get('url'):
                    body.append(f'<span class="note-url"><a href="{esc(cn["url"])}">{esc(cn["url"])}</a></span>')
                body.append('</p>')
            body.append('</div>')
    # footer
    url = cn_notes['url'] if cn_notes and cn_notes.get('url') else AUTHOR_URL
    body.append(f'<div class="article-footer">')
    body.append(f'<span>{meta["footer1"]} <a href="{esc(url)}">{esc(url)}</a></span>')
    body.append(f'<span>{meta["footer2"]} <a href="{AUTHOR_URL}">{esc(AUTHOR_URL)}</a></span>')
    body.append(f'<span class="cn">本文原发表于知乎专栏/回答（中文）：<a href="{esc(url)}">{esc(url)}</a>；作者：最最遥远的路：<a href="{AUTHOR_URL}">{esc(AUTHOR_URL)}</a></span>')
    body.append('</div>')
    return ('<!DOCTYPE html><html lang="%s" dir="%s"><head><meta charset="utf-8"><title>%s</title>'
            '<style>%s</style></head>%s</body></html>') % (
        meta['lang'], meta['dir'], esc(title), css_for(meta['lang'], meta), '\n'.join(body))

def main():
    lang = sys.argv[1] if len(sys.argv) > 1 else 'en'
    meta = LANG_META[lang]
    srcdir = os.path.join(BASE, 'work', lang + '_txt')
    outdir = os.path.join(BASE, 'work', lang + '_html')
    os.makedirs(outdir, exist_ok=True)
    files = sorted(glob.glob(os.path.join(srcdir, '*.txt')))
    only_file = os.path.join(BASE, 'work', '_only_cn.txt')
    if os.path.exists(only_file):
        only = {l.strip() for l in open(only_file, encoding='utf-8') if l.strip()}
        files = [f for f in files if os.path.splitext(os.path.basename(f))[0] in only]
        print('filter on:', len(files), 'files')
    for txt in files:
        cn_title = os.path.splitext(os.path.basename(txt))[0]
        cn = os.path.join(CN_HTML, cn_title + '.html')
        if not os.path.exists(cn):
            print('!! missing cn html for', cn_title)
            continue
        text = open(txt, encoding='utf-8').read()
        # translated title from first '# ' line
        first = text.split('\n', 1)[0]
        tr_title = first[2:].strip() if first.startswith('# ') else cn_title
        # sanitized filename: use translated title (Chinese keeps its own title)
        out_name = sanitize_name(tr_title) if lang != 'cn' else sanitize_name(cn_title)
        cn_notes = cn_notes_json(cn_title)
        blocks = parse_blocks(text)
        srcs = get_image_srcs(cn)
        out = os.path.join(outdir, out_name + '.html')
        html = build(blocks, srcs, cn_notes, meta, tr_title)
        open(out, 'w', encoding='utf-8').write(html)
        nimg = sum(1 for b, c in blocks if b == 'image')
        nnotes = sum(len(c) for b, c in blocks if b == 'notes')
        print(f'{cn_title[:22]:24s} -> {out_name[:36]:38s} | imgs={nimg}/{len(srcs)} notes_sec={nnotes}')
    print('DONE', lang)

if __name__ == '__main__':
    main()
