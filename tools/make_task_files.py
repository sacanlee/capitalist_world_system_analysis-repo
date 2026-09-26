# -*- coding: utf-8 -*-
"""Write one task file per (language, article-group) for the patching agents:
work/_worklist/_task_<lang>_<group>.md"""
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"C:\Users\Administrator\Desktop\zhihu\task\capitalism_world_system_analysis"
WL = os.path.join(BASE, 'work', '_worklist')

LANGS = [
    ('en', 'English', 'work/en_txt'),
    ('es', 'Spanish', 'work/es_txt'),
    ('pt', 'Portuguese', 'work/pt_txt'),
    ('fr', 'French', 'work/fr_txt'),
    ('ru', 'Russian', 'work/ru_txt'),
    ('ar', 'Arabic', 'work/ar_txt'),
    ('sw', 'Kiswahili', 'work/sw_txt'),
    ('hi', 'Hindi', 'work/hi_txt'),
    ('bn', 'Bengali', 'work/bn_txt'),
    ('id', 'Indonesian', 'work/id_txt'),
]

G1 = ['资本主义世界体系的兴衰（二）：跨国生产资本主义的内部结构',
      '资本主义世界体系的兴衰（三）：世界体系三个阶段的矛盾分析']
G2 = ['撒南非洲的工业化',
      '资本主义世界体系的兴衰（一）：资本主义世界体系生产方式演进的三个阶段',
      '印尼资本主义的发展',
      '天竺的自然资源与工业化']
G3 = ['2050年，英语能否保持全球通用语地位？',
      'AI泡沫到底有多大？AI泡沫危机是否会远超08年金融危机？',
      'AI编程是否会取代全部程序员？看看业界的实际情况',
      '为什么唯物主义在全世界竞争不过宗教_',
      '为什么阿尔都塞在《论再生产》中，会说“购买、销售或生产的合作社，它们完完全全属于资本主义生产方式”？',
      '为何直到21世纪，还有人喜欢玩民族主义？',
      '伊朗外长称伊朗有意允许日本船只通行霍尔木兹海峡，如何看待此番表态？背后有何考量？',
      '劳动价值论到底对不对？',
      '卖盾构机给印度的是国内哪家公司？',
      '印度10年前大谈印度制造，总理莫迪几乎照抄了东亚崛起时代的政策，为什么不能像中国一样爆发式增长？',
      '四口之家，一人上班，有房有车，美国工人真有过这样的好日子吗？',
      '回答：中国为什么把劳动密集企业转移到越南和印度，而不把低端产业链转移到巴基斯坦？',
      '如何看待AI技术革命对白领阶层的影响',
      '如何评价美国民主社会主义者（DSA）及其近期（2026年）在地方选举以及议员初选中的胜利？',
      '完全自给自足的经济体是否还可能？',
      '请问左派人士，你们认为生产力达到什么程度才能实现共产主义？左派有没有让社会达到这种生产力的方法论？',
      '资本主义生产方式中利润率的长期趋势',
      '越南购买印度拉莫斯导弹的主要目的是什么？是为了防御哪些潜在威胁？']

TERMS = {
    'en': '印度=India，中国=China，美国=the US / the United States，欧盟=the EU，政府=government',
    'es': '印度=India，中国=China，美国=EE. UU. / Estados Unidos，欧盟=la UE，政府=gobierno',
    'pt': '印度=Índia，中国=China，美国=EUA / Estados Unidos，欧盟=a UE，政府=governo',
    'fr': '印度=Inde，中国=Chine，美国=États-Unis，欧盟=l\'UE，政府=gouvernement',
    'ru': '印度=Индия，中国=Китай，美国=США，欧盟=ЕС，政府=правительство',
    'ar': '印度=الهند，中国=الصين，美国=الولايات المتحدة，欧盟=الاتحاد الأوروبي，政府=الحكومة',
    'sw': '印度=India，中国=Uchina，美国=Marekani，欧盟=Umoja wa Ulaya，政府=serikali',
    'hi': '印度=भारत，中国=चीन，美国=अमेरिका，欧盟=यूरोपीय संघ，政府=सरकार',
    'bn': '印度=ভারত，中国=চীন，美国=মার্কিন যুক্তরাষ্ট্র，欧盟=ইউরোপীয় ইউনিয়ন，政府=সরকার',
    'id': '印度=India，中国=Tiongkok，美国=AS，欧盟=Uni Eropa，政府=pemerintah',
}


def write(code, langname, subdir, group, titles):
    p = os.path.join(WL, f'_task_{code}_{group}.md')
    L = [f'# 补译任务：{langname} / {group}', '',
         f'**工作目录**：`{BASE}`（下称"项目根"）；**本语言译文目录**：`{subdir}/`', '',
         '## 背景', '',
         '旧的 HTML 提取脚本在把行内引用标记 `<sup>` 换成 `[n]` 时，丢掉了标记之后直到段落结尾的文字。'
         '因此凡是段中带 `[n]` 的段落，**译文里都缺了后半截**。中文源文件已经修复（现在完整），'
         '现在要把本语言译文里缺的那部分**补译**回去。', '',
         '## 做法（对清单里每一篇文章）', '',
         f'1. 读 `work/_worklist/<中文标题>.md`。它逐处列出：前文锚点（中文，译文里已存在）、'
         '**需要补译的中文文字**（就是缺掉的部分）、后文锚点（中文，译文里已存在）。',
         f'2. 打开 `{subdir}/<中文标题>.txt`。',
         '3. 对每一处：在译文里找到「前文锚点」对应的位置，把「需要补译的中文文字」'
         f'译成{langname}插进去——位置在前文锚点译文之后、后文锚点译文之前。',
         '4. 用 Edit 工具直接改该文件；改完接着处理下一处、下一篇文章。', '',
         '## 硬性要求', '',
         '- **只新增文字**。既有译文一个字都不要改写、删减、重排（仅允许必要的标点衔接）。',
         '- `[IMAGE n]`、`[图注: ...]`、`[n]`、`[NOTES]` 标记和 markdown 结构必须原样保留；'
         '**不要改动 `[NOTES]` 块**。',
         '- 风格与全文一致（典雅通俗、马克思主义语境，世界体系／阶级分析／帝国主义等概念）；'
         '术语沿用该文件里的既有译法（可以先 grep 确认）。',
         '- 中文里作者的网络语要译成正式国名：'
         '南方大国/天竺/南大=印度，东方大国/龙国/东大=中国，西方大国/米国/西大=美国，'
         '欧国=欧盟，GOV/ZF=政府。',
         f'- 本语言对应译名：{TERMS[code]}',
         '- 不要添加任何注释、译者注、说明文字。',
         '- 路径含中文标点，在 shell 里要加引号。', '',
         '## 本组文章清单', '']
    for t in titles:
        L.append(f'- [ ] `{t}`')
    L += ['', '## 完成后回报', '', '每篇文章：补了几处、是否已写回原文件；如有任何一处找不到对应位置，'
          '明确指出是哪一处（第几处 + 前文锚点）并说明原因。']
    open(p, 'w', encoding='utf-8').write('\n'.join(L))
    print('wrote', os.path.basename(p), len(titles), 'articles')


for code, langname, subdir in LANGS:
    write(code, langname, subdir, 'G3', G3)
    write(code, langname, subdir, 'G2', G2)
    write(code, langname, subdir, 'G1', G1)
print('DONE')
