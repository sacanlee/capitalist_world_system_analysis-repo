# -*- coding: utf-8 -*-
"""Set up the rebuild whitelists precisely.

work/_only_cn.txt        = Chinese titles whose source text was repaired
                           (the hunk list + 龙的崛起, whose slang was fixed)
work/_only_<lang>.txt    = only those articles whose <lang> text actually
                           changed, so to_pdf.py converts the minimum set
"""
import io, os, re, sys, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
WORK = os.path.join(BASE, 'work')
BAK = r"C:\tmp\lang_backup"
LANGS = [('en', 'en_txt'), ('es', 'es_txt'), ('pt', 'pt_txt'), ('fr', 'fr_txt'),
         ('ru', 'ru_txt'), ('ar', 'ar_txt'), ('sw', 'sw_txt'), ('hi', 'hi_txt'),
         ('bn', 'bn_txt'), ('id', 'id_txt')]


def sanitize_name(s):
    s = re.sub(r'[\\/:*?"<>|\r\n]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()[:100]


def translated_stem(lang, cn):
    p = os.path.join(WORK, lang + '_txt', cn + '.txt')
    if not os.path.exists(p):
        return None
    first = open(p, encoding='utf-8').readline().strip()
    return sanitize_name(first[2:].strip() if first.startswith('# ') else cn)


def main():
    repair = sorted(os.path.splitext(os.path.basename(f))[0]
                    for f in glob.glob(os.path.join(WORK, '_hunks', '*.json')))
    if '龙的崛起：资本主义世界体系中的中国' not in repair:
        repair.append('龙的崛起：资本主义世界体系中的中国')
    repair.sort()
    open(os.path.join(WORK, '_only_cn.txt'), 'w', encoding='utf-8').write('\n'.join(repair) + '\n')
    print('_only_cn.txt :', len(repair), 'articles')

    for lang, sub in LANGS:
        cur_dir = os.path.join(WORK, sub)
        bak_dir = os.path.join(BAK, sub)
        changed = []
        for cn in repair:
            cf = os.path.join(cur_dir, cn + '.txt')
            bf = os.path.join(bak_dir, cn + '.txt')
            if not os.path.exists(cf):
                continue
            if os.path.exists(bf) and open(cf, encoding='utf-8').read() == open(bf, encoding='utf-8').read():
                continue                      # identical to pre-patch state
            stem = translated_stem(lang, cn)
            if stem:
                changed.append(stem)
        open(os.path.join(WORK, '_only_%s.txt' % lang), 'w', encoding='utf-8').write('\n'.join(changed) + '\n')
        print(f'_only_{lang}.txt : {len(changed):2d} changed')


if __name__ == '__main__':
    main()
