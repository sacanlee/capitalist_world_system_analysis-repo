# -*- coding: utf-8 -*-
"""Copy one batch of PDFs into articles/<Lang>/<category>/ (non-destructive).

Usage: python add_articles.py <category> <cn-title> [<cn-title> ...]

For every language, the translated title is read from the first line of
work/<lang>_txt/<cn-title>.txt and sanitised the same way the PDF builder
does it; the PDF is then looked up in pdf/ (suffix _en/_es/...) and copied
into both articles/ and repo/articles/.
"""
import io, os, re, sys, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
PDF = os.path.join(BASE, 'pdf')

LANGS = [
    ('Chinese', '', 'txt'),
    ('English', '_en', 'en_txt'),
    ('Français', '_fr', 'fr_txt'),
    ('Español', '_es', 'es_txt'),
    ('português', '_pt', 'pt_txt'),
    ('العربية', '_ar', 'ar_txt'),
    ('Русский', '_ru', 'ru_txt'),
]


def sanitize_name(s):
    s = re.sub(r'[\\/:*?"<>|\r\n]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()[:100]


def title_of(lang_sub, cn):
    p = os.path.join(BASE, 'work', lang_sub, cn + '.txt')
    first = open(p, encoding='utf-8').readline().strip()
    return first[2:].strip() if first.startswith('# ') else cn


def main():
    if len(sys.argv) < 3:
        print('usage: python add_articles.py <category> <cn-title> [...]')
        sys.exit(1)
    cat, titles = sys.argv[1], sys.argv[2:]
    added, missing = 0, []
    for disp, suffix, sub in LANGS:
        for cn in titles:
            # Chinese PDFs keep the source stem (rebuild_articles_structure.py
            # does the same), so `?` in a title stays `_`
            name = sanitize_name(cn) if disp == 'Chinese' else sanitize_name(title_of(sub, cn))
            src = os.path.join(PDF, name + suffix + '.pdf')
            if not os.path.exists(src):
                missing.append((disp, cn, src))
                continue
            for root in (os.path.join(BASE, 'articles'),
                         os.path.join(BASE, 'repo', 'articles')):
                d = os.path.join(root, disp, cat)
                os.makedirs(d, exist_ok=True)
                dst = os.path.join(d, name + '.pdf')
                shutil.copy2(src, dst)
                added += 1
                print('%-14s %-24s %s  (%d KB)' % (disp, cat, name[:52], os.path.getsize(dst) // 1024))
    print('\ncopied:', added)
    if missing:
        print('MISSING', len(missing))
        for m in missing:
            print('  ', m)


if __name__ == '__main__':
    main()
