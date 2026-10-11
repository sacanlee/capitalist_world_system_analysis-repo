# -*- coding: utf-8 -*-
"""语言文化圈定义（唯一数据源）：
按用户 2026-10-11 规格：8大圈15子圈。
- 国家以 ISO3(WPP口径) 标识；CYN(北塞浦路斯)无WPP数据仅图示
- CHN = 中国（含港、澳、台地区），数据聚合 CHN+HKG+MAC+TWN
- draw_base/draw_stripe: 地图底色/斜纹圈层；泛法语/泛俄语用浅色
"""

TOPS = {
    "E":  ("英语文化圈", "English Sphere"),
    "R":  ("罗曼语文化圈", "Romance Sphere"),
    "C":  ("汉语文化圈", "Chinese Sphere"),
    "A":  ("阿拉伯语文化圈", "Arabic Sphere"),
    "RU": ("俄语文化圈", "Russian Sphere"),
    "P":  ("波斯语文化圈", "Persian Sphere"),
    "T":  ("突厥语文化圈", "Turkic Sphere"),
    "M":  ("印尼-马来语文化圈", "Malay-Indonesian Sphere"),
}

SUBS = {
    "E1":  ("纯英语子圈（含日耳曼语国家）", "Anglophone Core (incl. Germanic)", "E"),
    "E2":  ("英语+印度-雅利安语（南亚）子圈", "English + Indo-Aryan (South Asia)", "E"),
    "E3":  ("英语+斯瓦西里语子圈", "English + Swahili", "E"),
    "E4":  ("英语-其他子圈", "English – Others", "E"),
    "RF1": ("纯法语圈", "Francophone Core", "R"),
    "RF2": ("泛法语圈", "Francophone Extended", "R"),
    "RS":  ("西语圈", "Hispanophone (Spanish)", "R"),
    "RP":  ("葡语圈", "Lusophone (Portuguese)", "R"),
    "RO":  ("罗曼语圈其他（意大利/罗马尼亚/阿尔巴尼亚）", "Romance Others (Italian/Romanian/Albanian)", "R"),
    "C":   ("汉语文化圈", "Chinese Sphere", "C"),
    "A":   ("阿拉伯语文化圈", "Arabic Sphere", "A"),
    "RU1": ("纯俄语圈", "Russophone Core", "RU"),
    "RU2": ("泛俄语圈", "Russophone Extended", "RU"),
    "P":   ("波斯语文化圈", "Persian Sphere", "P"),
    "T":   ("突厥语文化圈", "Turkic Sphere", "T"),
    "M":   ("印尼-马来语文化圈", "Malay-Indonesian Sphere", "M"),
}

# iso3: (中文名, 英文名, [子圈...])
COUNTRIES = {
    # ---- 一 英语圈 / 1 纯英语子圈（含日耳曼语国家）----
    "GBR": ("英国", "United Kingdom", ["E1"]),
    "USA": ("美国", "United States", ["E1", "RS"]),
    "CAN": ("加拿大", "Canada", ["E1", "RF1"]),
    "NLD": ("荷兰", "Netherlands", ["E1"]),
    "NOR": ("挪威", "Norway", ["E1"]),
    "SWE": ("瑞典", "Sweden", ["E1"]),
    "DNK": ("丹麦", "Denmark", ["E1"]),
    "FIN": ("芬兰", "Finland", ["E1"]),
    "ISL": ("冰岛", "Iceland", ["E1"]),
    "DEU": ("德国", "Germany", ["E1"]),
    "AUT": ("奥地利", "Austria", ["E1"]),
    "IRL": ("爱尔兰", "Ireland", ["E1"]),
    "CYP": ("塞浦路斯", "Cyprus", ["E1"]),
    "AUS": ("澳大利亚", "Australia", ["E1"]),
    "NZL": ("新西兰", "New Zealand", ["E1"]),
    "SGP": ("新加坡", "Singapore", ["E1", "C", "M"]),
    "PHL": ("菲律宾", "Philippines", ["E1"]),
    "ZAF": ("南非", "South Africa", ["E1"]),
    "NGA": ("尼日利亚", "Nigeria", ["E1"]),
    "MWI": ("马拉维", "Malawi", ["E1"]),
    "GHA": ("加纳", "Ghana", ["E1"]),
    "BWA": ("博茨瓦纳", "Botswana", ["E1"]),
    "ZWE": ("津巴布韦", "Zimbabwe", ["E1"]),
    "LBR": ("利比里亚", "Liberia", ["E1"]),
    "JAM": ("牙买加", "Jamaica", ["E1"]),
    "ISR": ("以色列", "Israel", ["E1"]),
    # ---- 英语圈 / 2 英语+印度-雅利安语（南亚）----
    "PAK": ("巴基斯坦", "Pakistan", ["E2"]),
    "IND": ("印度", "India", ["E2"]),
    "BGD": ("孟加拉国", "Bangladesh", ["E2"]),
    "NPL": ("尼泊尔", "Nepal", ["E2"]),
    # ---- 英语圈 / 3 英语+斯瓦西里语 ----
    "KEN": ("肯尼亚", "Kenya", ["E3"]),
    "TZA": ("坦桑尼亚", "Tanzania", ["E3"]),
    "UGA": ("乌干达", "Uganda", ["E3"]),
    "RWA": ("卢旺达", "Rwanda", ["E3"]),
    "BDI": ("布隆迪", "Burundi", ["E3"]),
    "COM": ("科摩罗", "Comoros", ["E3", "A"]),
    # ---- 英语圈 / 4 英语-其他 ----
    "ETH": ("埃塞俄比亚", "Ethiopia", ["E4"]),
    "SSD": ("南苏丹", "South Sudan", ["E4"]),
    "VNM": ("越南", "Viet Nam", ["E4", "C"]),
    # ---- 二 罗曼语圈 / 1(1) 纯法语圈 ----
    "FRA": ("法国", "France", ["RF1"]),
    "BEL": ("比利时", "Belgium", ["RF1"]),
    "CMR": ("喀麦隆", "Cameroon", ["RF1"]),
    "CIV": ("科特迪瓦", "Côte d'Ivoire", ["RF1"]),
    "GAB": ("加蓬", "Gabon", ["RF1"]),
    "COG": ("刚果（布）", "Congo", ["RF1"]),
    "TGO": ("多哥", "Togo", ["RF1"]),
    "BEN": ("贝宁", "Benin", ["RF1"]),
    "COD": ("刚果（金）", "DR Congo", ["RF1"]),
    "GIN": ("几内亚", "Guinea", ["RF1"]),
    "CAF": ("中非共和国", "Central African Republic", ["RF1"]),
    "HTI": ("海地", "Haiti", ["RF1"]),
    # ---- 罗曼语圈 / 1(2) 泛法语圈 ----
    "SEN": ("塞内加尔", "Senegal", ["RF2"]),
    "MLI": ("马里", "Mali", ["RF2"]),
    "BFA": ("布基纳法索", "Burkina Faso", ["RF2"]),
    "NER": ("尼日尔", "Niger", ["RF2"]),
    "TCD": ("乍得", "Chad", ["RF2", "A"]),
    "MRT": ("毛里塔尼亚", "Mauritania", ["RF2", "A"]),
    "MAR": ("摩洛哥", "Morocco", ["RF2", "A"]),
    "TUN": ("突尼斯", "Tunisia", ["RF2", "A"]),
    "DZA": ("阿尔及利亚", "Algeria", ["RF2", "A"]),
    "DJI": ("吉布提", "Djibouti", ["RF2", "A"]),
    "MDG": ("马达加斯加", "Madagascar", ["RF2"]),
    # ---- 罗曼语圈 / 2 西语圈 ----
    "ESP": ("西班牙", "Spain", ["RS"]),
    "GNQ": ("赤道几内亚", "Equatorial Guinea", ["RS"]),
    "MEX": ("墨西哥", "Mexico", ["RS"]),
    "CUB": ("古巴", "Cuba", ["RS"]),
    "DOM": ("多米尼加", "Dominican Republic", ["RS"]),
    "PRI": ("波多黎各（美属）", "Puerto Rico (US)", ["RS"]),
    "GTM": ("危地马拉", "Guatemala", ["RS"]),
    "HND": ("洪都拉斯", "Honduras", ["RS"]),
    "SLV": ("萨尔瓦多", "El Salvador", ["RS"]),
    "NIC": ("尼加拉瓜", "Nicaragua", ["RS"]),
    "CRI": ("哥斯达黎加", "Costa Rica", ["RS"]),
    "PAN": ("巴拿马", "Panama", ["RS"]),
    "COL": ("哥伦比亚", "Colombia", ["RS"]),
    "VEN": ("委内瑞拉", "Venezuela", ["RS"]),
    "ECU": ("厄瓜多尔", "Ecuador", ["RS"]),
    "PER": ("秘鲁", "Peru", ["RS"]),
    "BOL": ("玻利维亚", "Bolivia", ["RS"]),
    "PRY": ("巴拉圭", "Paraguay", ["RS"]),
    "CHL": ("智利", "Chile", ["RS"]),
    "ARG": ("阿根廷", "Argentina", ["RS"]),
    "URY": ("乌拉圭", "Uruguay", ["RS"]),
    # ---- 罗曼语圈 / 3 葡语圈 ----
    "PRT": ("葡萄牙", "Portugal", ["RP"]),
    "BRA": ("巴西", "Brazil", ["RP"]),
    "AGO": ("安哥拉", "Angola", ["RP"]),
    "MOZ": ("莫桑比克", "Mozambique", ["RP"]),
    "CPV": ("佛得角", "Cabo Verde", ["RP"]),
    "GNB": ("几内亚比绍", "Guinea-Bissau", ["RP"]),
    "STP": ("圣多美和普林西比", "São Tomé and Príncipe", ["RP"]),
    # ---- 罗曼语圈 / 4 其他 ----
    "ITA": ("意大利", "Italy", ["RO"]),
    "ROU": ("罗马尼亚", "Romania", ["RO"]),
    "ALB": ("阿尔巴尼亚", "Albania", ["RO"]),
    # ---- 三 汉语文化圈 ----
    "CHN": ("中国（含港澳台地区）", "China (incl. HK, Macao, Taiwan)", ["C"]),
    "PRK": ("朝鲜", "DPR Korea", ["C"]),
    "KOR": ("韩国", "Republic of Korea", ["C"]),
    "JPN": ("日本", "Japan", ["C"]),
    "MYS": ("马来西亚", "Malaysia", ["C", "M"]),
    "LAO": ("老挝", "Laos", ["C"]),
    "KHM": ("柬埔寨", "Cambodia", ["C"]),
    "MMR": ("缅甸", "Myanmar", ["C"]),
    # ---- 四 阿拉伯语文化圈 ----
    "SAU": ("沙特阿拉伯", "Saudi Arabia", ["A"]),
    "EGY": ("埃及", "Egypt", ["A"]),
    "IRQ": ("伊拉克", "Iraq", ["A"]),
    "SDN": ("苏丹", "Sudan", ["A"]),
    "YEM": ("也门", "Yemen", ["A"]),
    "SYR": ("叙利亚", "Syria", ["A"]),
    "JOR": ("约旦", "Jordan", ["A"]),
    "LBY": ("利比亚", "Libya", ["A"]),
    "ARE": ("阿联酋", "United Arab Emirates", ["A"]),
    "LBN": ("黎巴嫩", "Lebanon", ["A"]),
    "OMN": ("阿曼", "Oman", ["A"]),
    "KWT": ("科威特", "Kuwait", ["A"]),
    "QAT": ("卡塔尔", "Qatar", ["A"]),
    "BHR": ("巴林", "Bahrain", ["A"]),
    "PSE": ("巴勒斯坦", "Palestine", ["A"]),
    # ---- 五 俄语文化圈 / 1 纯俄语圈 ----
    "RUS": ("俄罗斯", "Russia", ["RU1"]),
    "BLR": ("白俄罗斯", "Belarus", ["RU1"]),
    "KGZ": ("吉尔吉斯斯坦", "Kyrgyzstan", ["RU1", "T"]),
    "TJK": ("塔吉克斯坦", "Tajikistan", ["RU1", "P"]),
    # ---- 俄语文化圈 / 2 泛俄语圈 ----
    "KAZ": ("哈萨克斯坦", "Kazakhstan", ["RU2", "T"]),
    "UZB": ("乌兹别克斯坦", "Uzbekistan", ["RU2", "T"]),
    "UKR": ("乌克兰", "Ukraine", ["RU2"]),
    "LVA": ("拉脱维亚", "Latvia", ["RU2"]),
    "EST": ("爱沙尼亚", "Estonia", ["RU2"]),
    # ---- 六 波斯语文化圈 ----
    "IRN": ("伊朗", "Iran", ["P"]),
    "AFG": ("阿富汗", "Afghanistan", ["P"]),
    # ---- 七 突厥语文化圈 ----
    "TUR": ("土耳其", "Türkiye", ["T"]),
    "TKM": ("土库曼斯坦", "Turkmenistan", ["T"]),
    "AZE": ("阿塞拜疆", "Azerbaijan", ["T"]),
    "CYN": ("北塞浦路斯", "Northern Cyprus", ["T"]),  # 无WPP数据,仅图示
    # ---- 八 印尼-马来语文化圈 ----
    "IDN": ("印度尼西亚", "Indonesia", ["M"]),
    "BRN": ("文莱", "Brunei", ["M"]),
}

# 数据聚合: 中国含港澳台
AGG = {"CHN": ["CHN", "HKG", "MAC", "TWN"]}

# 地图代码: 数据ISO3(WPP) -> NE geojson ADM0_A3
GEO_CODE = {"PSE": "PSX", "SSD": "SDS"}
GEO_CODE_INV = {v: k for k, v in GEO_CODE.items()}

# NE 110m 底图缺失的小国 -> 标注坐标与样式
MARKERS = {
    "SGP": {"lon": 103.82, "lat": 1.35, "kind": "pie", "subs": ["E1", "C", "M"]},
    "COM": {"lon": 43.32, "lat": -11.65, "kind": "pie", "subs": ["E3", "A"]},
    "BHR": {"lon": 50.55, "lat": 26.07, "kind": "dot", "subs": ["A"]},
    "CPV": {"lon": -23.60, "lat": 15.12, "kind": "dot", "subs": ["RP"]},
    "STP": {"lon": 6.65, "lat": 0.33, "kind": "dot", "subs": ["RP"]},
}

# 多圈国家地图表达: 底色圈 / 斜纹圈
# 规则: 底色=当地主体语言所属圈; 泛法语/泛俄语国家(摩洛哥等)以阿拉伯色为底、浅橙斜纹;
#       马来西亚=马来色底+汉红斜纹; 加拿大=英语蓝底+法语橙斜纹; 哈萨克/乌兹=突厥橄榄底+浅紫斜纹;
#       塔吉克=波斯青底+俄紫斜纹; 吉尔吉斯=突厥橄榄底+俄紫斜纹; 新加坡/科摩罗=饼图标注
DRAW = {
    "USA": ("E", "R", "deep"),   # 英语蓝底 + 西语橙斜纹(2026-10-11 用户加入西语子圈)
    "CAN": ("E", "R", "deep"),
    "VNM": ("C", "E", "deep"),   # 汉语红底 + 英语蓝斜纹(越南同属汉语圈与英语-其他子圈)
    "MYS": ("M", "C", "deep"),
    "TCD": ("A", "R", "light"),
    "MRT": ("A", "R", "light"),
    "MAR": ("A", "R", "light"),
    "TUN": ("A", "R", "light"),
    "DZA": ("A", "R", "light"),
    "DJI": ("A", "R", "light"),
    "TJK": ("P", "RU", "deep"),
    "KGZ": ("T", "RU", "deep"),
    "KAZ": ("T", "RU", "light"),
    "UZB": ("T", "RU", "light"),
}

COLORS = {
    "E":  "#1f77b4",
    "R":  "#ff7f0e",
    "C":  "#d62728",
    "A":  "#2ca02c",
    "RU": "#9467bd",
    "P":  "#17becf",
    "T":  "#bcbd22",
    "M":  "#e377c2",
}
COLORS_LIGHT = {
    "R":  "#ffbb78",   # 泛法语
    "RU": "#c5b0d5",   # 泛俄语
}
UNCLASSIFIED = "#d9d9d9"

# 子圈 -> 是否需要浅色(泛)
def sub_shade(sub):
    return "light" if sub in ("RF2", "RU2") else "deep"


def country_tops(subs):
    seen = []
    for s in subs:
        t = SUBS[s][2]
        if t not in seen:
            seen.append(t)
    return seen


def base_color(iso):
    """国家底色圈层代码（未列入返回 None）"""
    if iso in DRAW:
        return DRAW[iso][0]
    subs = COUNTRIES[iso][2]
    tops = country_tops(subs)
    t = tops[0]
    # 单一罗曼/俄语国: 按其子圈深浅
    if t not in ("R", "RU"):
        return t
    for s in subs:
        if SUBS[s][2] == t:
            return (t, sub_shade(s))
    return t
