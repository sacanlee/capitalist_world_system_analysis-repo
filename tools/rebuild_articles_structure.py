# -*- coding: utf-8 -*-
"""Rebuild articles/<Lang>/<category>/<translated-title>.pdf using translated filenames."""
import os, re, shutil, sys, glob
sys.stdout.reconfigure(encoding='utf-8')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
PDF = os.path.join(BASE, 'pdf')
OUT = os.path.join(BASE, 'articles')

CATS = {
    'world-system-mechanisms': ['世界会实现大一统吗？','为什么阿尔都塞在《论再生产》中，会说“购买、销售或生产的合作社，它们完完全全属于资本主义生产方式”？','我有个同学说他向往计划经济，但是我说我来负责计划他就不乐意了，这是为什么？','请问左派人士，你们认为生产力达到什么程度才能实现共产主义？左派有没有让社会达到这种生产力的方法论？','劳动价值论到底对不对？','资本主义生产方式中利润率的长期趋势','资本主义世界体系的兴衰（一）：资本主义世界体系生产方式演进的三个阶段','资本主义世界体系的兴衰（二）：跨国生产资本主义的内部结构','资本主义世界体系的兴衰（三）：世界体系三个阶段的矛盾分析','如何看待AI技术革命对白领阶层的影响','白左思潮是否已经侵入中国？','为何直到21世纪，还有人喜欢玩民族主义？','你如何看待国内基本盘_','龙的崛起：资本主义世界体系中的中国','改良主义的前景','完全自给自足的经济体是否还可能？','深入理解资本主义的长波周期','阶级斗争对资本主义长波周期的影响'],
    'southern-capitalism': ['印尼资本主义的发展','撒南非洲的工业化','为什么有人觉得越南能崛起_','越南购买印度拉莫斯导弹的主要目的是什么？是为了防御哪些潜在威胁？','回答：中国为什么把劳动密集企业转移到越南和印度，而不把低端产业链转移到巴基斯坦？','中国用30年走完了发达国家300年的发展道路，值得中国人骄傲吗？','关于双休问题的回答'],
    'india-rise': ['印度在可预见的未来会发展成为工业化国家吗？','为什么空调在印度难以普及？','卖盾构机给印度的是国内哪家公司？','印度10年前大谈印度制造，总理莫迪几乎照抄了东亚崛起时代的政策，为什么不能像中国一样爆发式增长？','印度是真的烂还是咱们在信息茧房里面？','印度的军工实力如何？其实没想的那么差','印度这个国家是不是被国内严重低估了？','天竺的自然资源与工业化','怎么看待印共毛_'],
    'multipolar-world': ['多极世界有几极？展望2050','战争的逻辑及其前景','伊朗外长称伊朗有意允许日本船只通行霍尔木兹海峡，如何看待此番表态？背后有何考量？','世界能否容得下一个发达的中国？','2055年前，还有哪些国家有可能成为发达国家？'],
    'language-globalization': ['2050年，英语能否保持全球通用语地位？','印度是否会抛弃英语？印地语取而代之？','学英语的意义到底什么_','未来法语、西班牙语、俄语、阿拉伯语哪个最有发展前景？','如何看待越南实行英语立国？'],
    'other-observations': ['为什么唯物主义在全世界竞争不过宗教_','四口之家，一人上班，有房有车，美国工人真有过这样的好日子吗？','如何评价美国民主社会主义者（DSA）及其近期（2026年）在地方选举以及议员初选中的胜利？','关于AI和机器人的想象，很多都是不切实际的','AI泡沫到底有多大？AI泡沫危机是否会远超08年金融危机？','AI编程是否会取代全部程序员？看看业界的实际情况'],
}

LANGS = {
    'Chinese': ('', 'cn'),
    'English': ('_en', 'en'),
    'Français': ('_fr', 'fr'),
    'Español': ('_es', 'es'),
    'português': ('_pt', 'pt'),
    'العربية': ('_ar', 'ar'),
    'Русский': ('_ru', 'ru'),
    'Kiswahili': ('_sw', 'sw'),
    'हिन्दी': ('_hi', 'hi'),
    'বাংলা': ('_bn', 'bn'),
    'Bahasa Indonesia': ('_id', 'id'),
}

def sanitize_name(s):
    s = re.sub(r'[\\/:*?"<>|\r\n]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s[:100]

def lang_titles(lang):
    """Chinese title -> translated title, from each <lang>_txt first line."""
    m = {}
    for f in glob.glob(os.path.join(BASE, 'work', lang + '_txt', '*.txt')):
        cn = os.path.basename(f)[:-4]
        first = open(f, encoding='utf-8').readline().strip()
        tr = first[2:].strip() if first.startswith('# ') else cn
        m[cn] = tr
    return m

def main():
    total = 0
    missing = []
    for lang, (suffix, code) in LANGS.items():
        titles = lang_titles(code) if code != 'cn' else None
        for cat, lst in CATS.items():
            d = os.path.join(OUT, lang, cat)
            # clean stale files
            if os.path.isdir(d):
                for f in os.listdir(d):
                    os.remove(os.path.join(d, f))
            os.makedirs(d, exist_ok=True)
            for cn in lst:
                if titles is not None and cn not in titles:
                    continue  # not yet translated into this language
                name = sanitize_name(titles[cn]) if titles else sanitize_name(cn)
                src = os.path.join(PDF, name + suffix + '.pdf')
                if os.path.exists(src):
                    shutil.copy2(src, os.path.join(d, name + '.pdf'))
                    total += 1
                else:
                    missing.append((lang, cn))
    print('copied:', total, 'missing:', missing)

if __name__ == '__main__':
    main()
