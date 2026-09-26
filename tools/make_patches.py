# -*- coding: utf-8 -*-
"""Build per-article patch specs from (current work/txt) vs (fixed re-extraction).

Writes work/_patch/<title>.json:
  {
    "title": ...,
    "old_chars": n, "new_chars": n, "added": n,
    "hunks": [ {"k":1, "before":"…", "inserted":"…", "after":"…"}, … ]
  }
`before` / `after` are the CN context that is present in BOTH the old and the
new text (used to locate the insertion point in a translation).
Also writes work/_patch/_SUMMARY.md for humans.
"""
import io, os, re, sys, json, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
CUR = os.path.join(BASE, 'work', 'txt')
NEW = r"C:\tmp\reextract_check\txt"
OUT = os.path.join(BASE, 'work', '_patch')

NEW_BATCH = {
    '关于双休问题的回答', '龙的崛起：资本主义世界体系中的中国',
    '2055年前，还有哪些国家有可能成为发达国家？',
    'AI编程是否会取代全部程序员？看看业界的实际情况',
    '完全自给自足的经济体是否还可能？', '改良主义的前景',
    '深入理解资本主义的长波周期', '阶级斗争对资本主义长波周期的影响',
    '21世纪有可能再进行一次打倒资本运动吗_',
}
ASCII_GUARD = r'(?<![A-Za-z0-9%%])%s(?![A-Za-z0-9])'
RULES = [('南方大国', '印度'), ('天竺', '印度'), ('南大', '印度'),
         ('东方大国', '中国'), ('龙国', '中国'), ('东大', '中国'),
         ('西方大国', '美国'), ('米国', '美国'), ('西大', '美国'),
         ('欧国', '欧盟'), ('两天周末', '双休'), ('周末两天', '双休')]
RULES = [(re.compile(ASCII_GUARD % re.escape(a)), b) for a, b in RULES]
RULES += [(re.compile(ASCII_GUARD % 'GOV'), '政府'), (re.compile(ASCII_GUARD % 'ZF'), '政府')]


def sanitize(s):
    for rx, rep in RULES:
        s = rx.sub(rep, s)
    return s


os.makedirs(OUT, exist_ok=True)
CTX = 60
summary = []
total_hunks = 0
for fn in sorted(os.listdir(NEW)):
    if not fn.endswith('.txt'):
        continue
    stem = fn[:-4]
    if stem in ('21世纪有可能再进行一次打倒资本运动吗_',):
        continue  # already repaired
    new_t = open(os.path.join(NEW, fn), encoding='utf-8').read()
    if stem in NEW_BATCH:
        new_t = sanitize(new_t)
    cur_p = os.path.join(CUR, fn)
    if not os.path.exists(cur_p):
        continue
    cur_t = open(cur_p, encoding='utf-8').read()
    if new_t == cur_t:
        continue
    sm = difflib.SequenceMatcher(None, cur_t, new_t, autojunk=False)
    hunks, kinds = [], {}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        kinds[tag] = kinds.get(tag, 0) + 1
        if tag == 'equal':
            continue
        hunks.append({
            'k': len(hunks) + 1,
            'op': tag,
            'deleted': cur_t[i1:i2],
            'inserted': new_t[j1:j2],
            'before': cur_t[max(0, i1 - CTX):i1],
            'after': cur_t[i2:i2 + CTX],
        })
    title = stem
    json.dump({'title': title, 'old_chars': len(cur_t), 'new_chars': len(new_t),
               'added': len(new_t) - len(cur_t), 'opcodes': kinds, 'hunks': hunks},
              open(os.path.join(OUT, title + '.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    total_hunks += len(hunks)
    summary.append((title, len(new_t) - len(cur_t), len(hunks), kinds))
    print(f'{title[:40]:42s} +{len(new_t)-len(cur_t):5d} chars  hunks={len(hunks):3d}  {kinds}')

summary.sort(key=lambda x: -x[1])
with open(os.path.join(OUT, '_SUMMARY.md'), 'w', encoding='utf-8') as f:
    f.write('# 缺文补丁清单（中文源，按丢失字数降序）\n\n')
    f.write(f'共 {len(summary)} 篇，{total_hunks} 处插入，'
            f'恢复 {sum(s[1] for s in summary)} 字\n\n')
    f.write('| 文章 | 恢复字数 | 插入处数 | opcode 分布 |\n|---|---|---|---|\n')
    for t, add, n, k in summary:
        f.write(f'| {t} | +{add} | {n} | {k} |\n')
print('=' * 74)
print(f'{len(summary)} articles, {total_hunks} hunks')
