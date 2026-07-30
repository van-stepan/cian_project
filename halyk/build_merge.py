# -*- coding: utf-8 -*-
# Build filled "Соединение вариаций товаров": multi-colour families share Код вариации;
# each card gets its mapped Цвет. Names generated with the SAME templates used at creation.
import json, re, collections, openpyxl
SP="/tmp/claude-0/-home-user-cian-project/86d433ab-8129-51c0-9d4f-b1a23c7ce53d/scratchpad"
cards={c["vendorCode"]:c for c in json.load(open(SP+"/wb_cards.json"))}
compat_opts=json.load(open(SP+"/compat_opts.json"))
color_opts=json.load(open(SP+"/color_opts.json")); color_lc={k.lower() for k in color_opts}
def norm(s): return re.sub(r'\s+',' ',s.strip().lower()).replace('ё','е')
CANON_ID={norm(k):v for k,v in compat_opts.items()}; CANON_NM={norm(k):k for k in compat_opts}
def variants(s):
    n=norm(s); outs=[n]
    n2=re.sub(r'\s*\b[45]g\b','',n).strip()
    if n2!=n: outs.append(n2)
    for base in list(outs):
        if base.startswith("redmi") or base.startswith("poco"): outs.append("xiaomi "+base)
    return outs
def compat_name(sku,c):
    wb=next((ch["value"] for ch in c["characteristics"] if ch["name"]=="Совместимость"),[])
    for v in wb:
        if norm(v) in CANON_ID: return CANON_NM[norm(v)]
    for v in wb:
        for cand in variants(v):
            if cand in CANON_ID: return CANON_NM[cand]
    seg=sku.split("-")
    if seg[0] in ("c7","c10","c5","c6","c2"): seg=seg[1:]
    if seg and seg[0]=="iphone":
        m=re.match(r'(\d+)(pro)?(max)?',seg[1] if len(seg)>1 else "")
        if m:
            cand=norm("apple iphone "+m.group(1)+(" pro" if m.group(2) else "")+(" max" if m.group(3) else ""))
            if cand in CANON_ID: return CANON_NM[cand]
    return None
def model_from_title(c):
    m=re.search(r'для (.+)$',c["title"]); s=m.group(1) if m else c["title"]
    s=re.sub(r'\s*\(.*?\)','',s); s=re.sub(r'\s*/.*$','',s).strip()
    CONN={"и","с","для","на","не","или","and","the"}
    def cap(w):
        if w.lower() in CONN: return w.lower()
        u=w.upper()
        if u in ("5G","4G","NFC","GT","FE","SE"): return u
        if u in ("PRO","MAX","PLUS","ULTRA","LITE","NEO","MINI"): return u.title()
        return w.capitalize()
    return " ".join(cap(w) for w in s.split())
def model_disp(sku,c):
    cn=compat_name(sku,c)
    if cn:
        d=cn[6:] if cn.startswith("Apple ") else cn
        return d.replace("Iphone","iPhone")
    return model_from_title(c)
CALIAS={"фуксия":"Фуксия","ярко-розовый":"Фуксия","розовый неон":"Фуксия","апельсин":"Оранжевый","графит":"Темно-серый"}
def card_color(c):
    wc=next((ch["value"] for ch in c["characteristics"] if ch["name"]=="Цвет"),[])
    for v in wc:
        if v.lower() in color_lc: return next(k for k in color_opts if k.lower()==v.lower())
    for v in wc:
        if v.lower() in CALIAS: return CALIAS[v.lower()]
    return None
TITLE={"c7":"Чехол для %s %s из пластика с металлической камерой-подставкой и MagSafe",
 "c10":"Дизайнерский чехол для %s %s из пластика с MagSafe и защитой камеры",
 "c6":"Мягкий тканевый чехол для %s %s с soft-touch покрытием и защитой камеры",
 "c5":"Кожаный чехол для %s %s с кольцом-подставкой и поддержкой беспроводной зарядки",
 "c2":"Чехол с кольцом-подставкой для %s %s из пластика с защитой камеры",
 "softtouch":"Чехол Soft Touch для %s %s из силикона с защитой камеры",
 "book":"Чехол-книжка для %s %s из экокожи с отделением для карт и подставкой"}
def type_of(sku):
    p=sku.split("-")[0]
    if p in ("c7","c10","c5","c6","c2"): return p
    if p in ("b1","b2","b3","b5"): return "book"
    return "softtouch"
tpl=openpyxl.load_workbook(SP+"/merge_tpl.xlsx")
MERGE=[tpl["значения"].cell(r,1).value for r in range(2,tpl["значения"].max_row+1) if tpl["значения"].cell(r,1).value]
MERGE_lc={m.lower():m for m in MERGE}
MAP={"Малиновый":"Фуксия","Графитовый":"Темно-серый","Золотой":"Золотистый","Серебряный":"Серебристый",
 "Кремовый":"Светло-бежевый","Молочный":"Белый","Лавандовый":"Сиреневый","Терракотовый":"Коричневый",
 "Многоцветный":"Мультиколор","Пудровый":"Светло-розовый","Хамелеон":"Мультиколор","Мятный":"Светло-зеленый",
 "Лимонный":"Светло-желтый","Темно-бордовый":"Бордовый"}
def to_merge(col):
    if col is None: return None
    if col.lower() in MERGE_lc: return MERGE_lc[col.lower()]
    return MAP.get(col)
def family(sku): return re.sub(r'-parent-.*$','',sku)
fam=collections.defaultdict(list)
for sku in cards: fam[family(sku)].append(sku)
multi={k:v for k,v in fam.items() if len(v)>1}
rows=[]; miss=[]
for famkey in sorted(multi):
    for sku in sorted(multi[famkey]):
        c=cards[sku]; typ=type_of(sku); col=to_merge(card_color(c))
        if not col: miss.append((sku,card_color(c))); continue
        name=TITLE[typ]%(model_disp(sku,c),card_color(c).lower())
        rows.append((sku,name,famkey,col))
ws=tpl["Товары для объединения"]
for r,(sku,nm,vc,col) in enumerate(rows,start=2):
    ws.cell(r,1,sku); ws.cell(r,2,nm); ws.cell(r,3,vc); ws.cell(r,4,col)
tpl.save(SP+"/merge_filled.xlsx")
print("rows:",len(rows)," families:",len(multi)," missing:",len(miss))
for m in miss: print("  MISS",m)
