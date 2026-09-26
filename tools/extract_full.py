# -*- coding: utf-8 -*-
"""Full extraction pipeline: clean CN HTML + structured txt + notes json.

For every article HTML in articles_in_chinese/:
  - extracts title/author/date/url (og:url)
  - rewrites images to local absolute file:/// paths
  - converts <sup data-numero> citations to inline [n] markers,
    collecting (text, url) into a notes json
  - appends a Chinese notes section + author footer to the clean HTML
Outputs:
  work/cn_html/<clean>.html
  work/txt/<clean>.txt      (with [IMAGE n], [n], [图注: ...], [表格] markers)
  work/notes/<clean>.json
"""
import os, glob, re, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from lxml import html as lh

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "articles_in_chinese")
# EXTRACT_OUT lets a dry run write elsewhere (e.g. a temp dir for diffing)
WORK = os.environ.get("EXTRACT_OUT", os.path.join(BASE, "work"))
CN_HTML = os.path.join(WORK, "cn_html")
TXT = os.path.join(WORK, "txt")
NOTES = os.path.join(WORK, "notes")
AUTHOR_URL = "https://www.zhihu.com/people/zui-zui-yao-yuan-de-lu-32/posts"
AUTHOR_NAME = "最最遥远的路"
for d in (CN_HTML, TXT, NOTES):
    os.makedirs(d, exist_ok=True)

CSS = """
body { font-family: "Noto Serif SC","Source Han Serif SC","SimSun",serif; max-width: 760px; margin: 0 auto; padding: 32px 24px; line-height: 1.85; color: #1a1a1a; font-size: 16px; }
h1.article-title { font-size: 26px; line-height: 1.4; margin-bottom: 4px; }
.article-meta { color: #888; font-size: 13.5px; margin-bottom: 24px; padding-bottom: 14px; border-bottom: 1px solid #e5e5e5; }
h2 { font-size: 21px; margin-top: 36px; }
h3 { font-size: 18px; }
p { margin: 12px 0; text-align: justify; }
figure { margin: 20px 0; text-align: center; }
figure img { max-width: 100%; height: auto; }
figcaption { color: #666; font-size: 13px; margin-top: 6px; }
blockquote { margin: 14px 0; padding: 4px 16px; border-left: 4px solid #ddd; color: #444; }
a { color: #175199; text-decoration: none; word-break: break-all; }
table { border-collapse: collapse; margin: 14px 0; }
td, th { border: 1px solid #ccc; padding: 5px 10px; font-size: 14.5px; }
img { max-width: 100%; height: auto; }
sup.note-ref, span.note-ref { color: #175199; font-size: 12px; vertical-align: super; line-height: 0; }
.notes-section { margin-top: 48px; padding-top: 20px; border-top: 1px solid #e5e5e5; }
.notes-section h2 { font-size: 19px; }
.notes-section p.note { font-size: 14px; color: #444; margin: 8px 0; line-height: 1.7; }
.notes-section .note-url { display: block; font-size: 12.5px; color: #666; margin-top: 2px; }
.article-footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid #e5e5e5; color: #666; font-size: 13px; }
"""

def clean_name(s):
    s = re.sub(r'[\\/:*?"<>|\r\n]', '_', s).strip()
    return s[:100]

def find_image_file(fname, article_dir):
    """Resolve local image file: check article's _files dir, then all _files dirs."""
    fdir = os.path.join(article_dir, os.path.splitext(os.path.basename(article_dir))[0] + '_files')
    # article_dir is the dir containing the html; _files dir is sibling
    base = article_dir
    cand = os.path.join(base, os.path.basename(base) + '_files')
    if os.path.exists(os.path.join(cand, fname)):
        return os.path.join(cand, fname)
    # try sibling _files dirs by matching any _files dir in SRC
    for d in glob.glob(os.path.join(SRC, '*_files')):
        if os.path.exists(os.path.join(d, fname)):
            return os.path.join(d, fname)
    return None

def clean_tree(content, article_dir):
    # remove non-content tags
    for tag in content.iter():
        if tag.tag in ('style', 'script', 'svg', 'noscript', 'iframe', 'button', 'ins', 'textarea'):
            p = tag.getparent()
            if p is not None:
                p.remove(tag)
    # unwrap EntityWord spans (keep text), strip all span attrs
    for span in list(content.iter('span')):
        cls = span.get('class') or ''
        p = span.getparent()
        if p is None:
            continue
        if 'EntityWord' in cls:
            for svg in span.iter('svg'):
                s2 = svg.getparent()
                if s2 is not None:
                    s2.remove(svg)
            for child in list(span):
                p.addprevious(child)
            p.remove(span)
        else:
            for k in list(span.attrib):
                del span.attrib[k]
    # fix images
    for img in list(content.iter('img')):
        src = img.get('src') or img.get('data-src') or ''
        m = re.search(r'([^/\\]+\.(?:jpe?g|png|gif|webp))$', src, re.I)
        path = None
        if m:
            path = find_image_file(m.group(1), article_dir)
        if path and os.path.exists(path):
            img.set('src', 'file:///' + path.replace('\\', '/'))
            for k in list(img.attrib):
                if k not in ('src', 'alt'):
                    del img.attrib[k]
        else:
            p = img.getparent()
            if p is not None:
                p.remove(img)

def process(f):
    name = os.path.splitext(os.path.basename(f))[0]
    article_dir = os.path.dirname(f)
    parser = lh.HTMLParser(encoding='utf-8')
    tree = lh.fromstring(open(f, encoding='utf-8', errors='replace').read(), parser=parser)
    raw = open(f, encoding='utf-8', errors='replace').read()
    # og:title (cleaner than filename)
    og_title = ''
    for m in tree.iter('meta'):
        if m.get('property') == 'og:title':
            og_title = m.get('content', '').strip()
            break
    # title
    title_el = tree.find_class('Post-Title')
    if title_el:
        title = title_el[0].text_content().strip()
    elif og_title:
        title = re.sub(r'\s*-\s*最最遥远的路\s*的\s*回答\s*$', '', og_title).strip()
    else:
        title = name
    # url: og:url; if 'undefined' in it, rebuild from question/answer ids
    url = ''
    for m in tree.iter('meta'):
        if m.get('property') == 'og:url':
            url = m.get('content', '').strip()
            break
    if 'undefined' in url:
        m = re.search(r'question/(\d+)/answer/(\d+)', raw)
        if m:
            url = 'https://www.zhihu.com/question/%s/answer/%s' % (m.group(1), m.group(2))
    # author / date
    author = ''
    for m in tree.iter('meta'):
        if m.get('itemprop') == 'name' and m.getparent() is not None and (m.getparent().get('itemprop') or '') == 'author':
            author = m.get('content', '')
            break
    date = ''
    for m in tree.iter('meta'):
        if m.get('itemprop') == 'datePublished':
            date = m.get('content', '')[:10]
            break
    cont = tree.find_class('Post-RichTextContainer')
    if not cont:
        # answer pages: pick the AnswerItem whose data-zop names the author
        for div in tree.iter('div'):
            cls = div.get('class') or ''
            zop = div.get('data-zop') or ''
            if 'AnswerItem' in cls and AUTHOR_NAME in zop:
                for el in div.iter():
                    if el.get('itemprop') == 'text':
                        cont = [el]
                        break
            if cont:
                break
    if not cont:
        # fallback: longest itemprop=text
        best = None; best_len = 0
        for el in tree.iter():
            if el.get('itemprop') == 'text':
                n = len(el.text_content())
                if n > best_len:
                    best_len = n
                    best = el
        if best is not None:
            cont = [best]
    if not cont:
        print('!! no content:', name)
        return
    content = cont[0]
    # collect citations BEFORE cleaning spans
    notes = []
    ncounter = [0]
    for sup in list(content.iter('sup')):
        if sup.get('data-numero') is not None:
            ncounter[0] += 1
            txt = (sup.get('data-text') or '').strip()
            u = (sup.get('data-url') or '').strip()
            notes.append({'num': ncounter[0], 'text': txt, 'url': u})
            span = lh.Element('span'); span.set('class', 'note-ref')
            span.text = '[%d]' % ncounter[0]
            # a <sup> in mid-paragraph carries the rest of the paragraph in its
            # .tail; removing the element would drop it, so move it onto the marker
            span.tail = sup.tail
            sup.addprevious(span)
            p = sup.getparent()
            if p is not None:
                p.remove(sup)
    clean_tree(content, article_dir)
    # notes section (Chinese)
    if notes:
        ns = lh.Element('div'); ns.set('class', 'notes-section')
        h2 = lh.Element('h2'); h2.text = '注释'; ns.append(h2)
        for nt in notes:
            para = lh.Element('p'); para.set('class', 'note')
            b = lh.Element('span'); b.set('class', 'note-ref')
            b.text = '[%d] ' % nt['num']
            para.append(b)
            para.append(lh.Element('br'))
            para.text = (para.text or '') + ''
            # build: [n]<br> text <span url>
            txt_el = lh.Element('span'); txt_el.text = nt['text']
            para.append(txt_el)
            if nt['url']:
                a = lh.Element('a'); a.set('href', nt['url']); a.text = nt['url']
                u_span = lh.Element('span'); u_span.set('class', 'note-url')
                u_span.append(a)
                para.append(u_span)
            ns.append(para)
        content.addnext(ns)
    # footer with author link
    foot = lh.Element('div'); foot.set('class', 'article-footer')
    ftext = lh.Element('span')
    ftext.text = '本文原发表于知乎（中文）：'
    fa = lh.Element('a'); fa.set('href', url if url else AUTHOR_URL); fa.text = url if url else AUTHOR_URL
    ftext.append(fa)
    foot.append(ftext)
    foot.append(lh.Element('br'))
    fa2 = lh.Element('a'); fa2.set('href', AUTHOR_URL); fa2.text = '作者：%s · 知乎主页' % AUTHOR_NAME
    foot.append(fa2)
    # build clean html
    body = lh.Element('body')
    h1 = lh.Element('h1'); h1.set('class', 'article-title'); h1.text = title; body.append(h1)
    meta = lh.Element('div'); meta.set('class', 'article-meta')
    meta.text = ((author + ' · ') if author else '') + '知乎' + (' · ' + date if date else '')
    body.append(meta)
    body.append(content)
    if notes:
        body.append(ns)
    body.append(foot)
    clean = clean_name(title)
    out_html = lh.tostring(body, encoding='unicode', method='html')
    doc = (f'<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">'
           f'<title>{title}</title><style>{CSS}</style></head>{out_html}</html>')
    cn_path = os.path.join(CN_HTML, clean + '.html')
    open(cn_path, 'w', encoding='utf-8').write(doc)
    # txt
    txt = build_txt(content, title, meta.text_content().strip())
    open(os.path.join(TXT, clean + '.txt'), 'w', encoding='utf-8').write(txt)
    # notes json
    json.dump({'title': title, 'url': url, 'author': author, 'date': date,
               'notes': notes}, open(os.path.join(NOTES, clean + '.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(f'{clean[:40]:42s} | chars={len(txt):6d} | imgs={img_n} | notes={len(notes)} | {url[:46]}')

img_n = 0
def build_txt(content, title, meta):
    global img_n
    out = ['# ' + title + '\n\n', f'[元信息] {meta}\n\n']
    img_counter = [0]
    def walk(el):
        global img_n
        for child in el.iterchildren():
            tag = child.tag
            if tag is None:
                continue
            if isinstance(tag, str) and tag.lower() == 'img':
                img_counter[0] += 1
                img_n += 1
                out.append(f'\n[IMAGE {img_counter[0]}]\n')
                continue
            if tag in ('h1',):
                continue
            if tag == 'h2':
                t = child.text_content().strip()
                if t: out.append(f'\n## {t}\n')
            elif tag == 'h3':
                t = child.text_content().strip()
                if t: out.append(f'\n### {t}\n')
            elif tag == 'blockquote':
                t = child.text_content().strip()
                if t: out.append(f'\n> {t}\n')
            elif tag == 'figcaption':
                continue
            elif tag == 'figure':
                walk(child)
                cap = child.find('.//figcaption')
                if cap is not None and cap.text_content().strip():
                    out.append(f'[图注: {cap.text_content().strip()}]\n')
            elif tag == 'p':
                t = child.text_content().strip()
                if t: out.append(t + '\n\n')
            elif tag == 'li':
                t = child.text_content().strip()
                if t: out.append('- ' + t + '\n')
            elif tag == 'table':
                rows = []
                for tr in child.iter('tr'):
                    cells = [c.text_content().strip() for c in tr.iter('td')] or \
                            [c.text_content().strip() for c in tr.iter('th')]
                    rows.append(' | '.join(cells))
                if rows:
                    out.append('[表格]\n' + '\n'.join(rows) + '\n')
            else:
                walk(child)
    walk(content)
    return ''.join(out)

if __name__ == '__main__':
    files = sorted(glob.glob(os.path.join(SRC, '*.html')))
    for f in files:
        process(f)
    print(f'DONE {len(files)} files')
