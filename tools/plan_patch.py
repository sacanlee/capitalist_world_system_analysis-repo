# -*- coding: utf-8 -*-
"""Turn the hunk list (work/_hunks) into a block-level patch plan (work/_patch).

The sup.tail fix only ever APPENDS text inside an existing paragraph, so the
blank-line block structure is unchanged.  For every article we locate each
hunk's inserted text in the final CN txt, map it to a block index, and emit:

  work/_patch/<title>.json
    {"title":…, "n_blocks":N,
     "blocks":[{"idx":i, "new_cn":"<whole new CN block>",
                "insertions":["<CN text added here>", …]}, …]}

The block index is what makes the per-language splice safe: every language
file must have exactly n_blocks blocks, and block i is the same paragraph.
"""
import io, os, json, sys, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
WORK = os.path.join(BASE, 'work')
HUNKS = os.path.join(WORK, '_hunks')
PATCH = os.path.join(WORK, '_patch')
LANGS = [('en', 'en_txt'), ('es', 'es_txt'), ('pt', 'pt_txt'), ('fr', 'fr_txt'),
         ('ru', 'ru_txt'), ('ar', 'ar_txt'), ('sw', 'sw_txt'), ('hi', 'hi_txt'),
         ('bn', 'bn_txt'), ('id', 'id_txt')]


def block_index(text, pos):
    """index of the blank-line separated block containing character `pos`"""
    return text.count('\n\n', 0, pos)


def main():
    bad = []
    for hp in sorted(glob.glob(os.path.join(HUNKS, '*.json'))):
        d = json.load(open(hp, encoding='utf-8'))
        t = d['title']
        txt = open(os.path.join(WORK, 'txt', t + '.txt'), encoding='utf-8').read()
        blocks = txt.split('\n\n')
        per_block = {}
        for h in d['hunks']:
            ins = h['inserted']
            if not ins:
                continue
            pos = txt.find(ins)
            if pos < 0:
                bad.append((t, 'insertion not found', ins[:40]))
                continue
            per_block.setdefault(block_index(txt, pos), []).append(ins)
        entries = [{'idx': i, 'new_cn': blocks[i], 'insertions': per_block[i]}
                   for i in sorted(per_block)]
        json.dump({'title': t, 'n_blocks': len(blocks), 'blocks': entries},
                  open(os.path.join(PATCH, t + '.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        # every language file must share the block skeleton
        mismatch = []
        for code, sub in LANGS:
            p = os.path.join(WORK, sub, t + '.txt')
            if not os.path.exists(p):
                continue
            n = len(open(p, encoding='utf-8').read().split('\n\n'))
            if n != len(blocks):
                mismatch.append((code, n))
        flag = ''
        if mismatch:
            flag = f'   LANG MISMATCH {mismatch}'
            bad.append((t, 'block mismatch', mismatch))
        print(f'{t[:40]:42s} blocks={len(blocks):3d} touched={len(entries):3d}'
              f' ins={sum(len(e["insertions"]) for e in entries):3d}{flag}')
    print('=' * 74)
    if bad:
        print('PROBLEMS:', len(bad))
        for b in bad[:20]:
            print('  ', b)
    else:
        print('ALL CONSISTENT')


if __name__ == '__main__':
    main()
