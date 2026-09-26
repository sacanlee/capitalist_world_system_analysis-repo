# -*- coding: utf-8 -*-
"""Find "orphan fragment" sites created by the sup.tail truncation.

When several <sup> markers sat in one paragraph, the truncation glued them
together (…在1950年[15][16][17]) and left the text that followed as an orphan
fragment which translators could only guess at.  Reconstructing the OLD Chinese
( = new text minus the recovered insertions ) and comparing its marker runs
with the new text isolates exactly those sites.

Writes work/_clusters/<title>.json: [{k, old_run, new_ctx, fragment}, …]
"""
import io, os, re, sys, json, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
WORK = os.path.join(BASE, 'work')
OUT = os.path.join(WORK, '_clusters')
os.makedirs(OUT, exist_ok=True)

RUN = re.compile(r'(?:\[\d{1,3}\]){2,}')


def main():
    total = 0
    for hp in sorted(glob.glob(os.path.join(WORK, '_hunks', '*.json'))):
        d = json.load(open(hp, encoding='utf-8'))
        t = d['title']
        new = open(os.path.join(WORK, 'txt', t + '.txt'), encoding='utf-8').read()
        old = new
        for h in d['hunks']:
            ins = h['inserted']
            if not ins:
                continue
            i = old.find(ins)
            if i < 0:
                continue          # already removed by an overlapping hunk
            old = old[:i] + old[i + len(ins):]
        new_runs = set(m.group(0) for m in RUN.finditer(new))
        sites = []
        for m in RUN.finditer(old):
            if m.group(0) in new_runs:
                continue          # still a legitimate multi-citation run
            frag = old[m.end():m.end() + 60].split('\n')[0]
            ctx_before = old[max(0, m.start() - 40):m.start()]
            sites.append({'k': len(sites) + 1, 'new_ctx': ctx_before, 'old_run': m.group(0),
                          'fragment': frag})
        if sites:
            json.dump({'title': t, 'sites': sites},
                      open(os.path.join(OUT, t + '.json'), 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
            total += len(sites)
            print(f'{t[:40]:42s} orphan sites={len(sites)}')
    print('=' * 70)
    print('total orphan sites:', total)


if __name__ == '__main__':
    main()
