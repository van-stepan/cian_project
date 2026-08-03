# -*- coding: utf-8 -*-
# Rebuild price_all.xml covering EVERY resolvable WB SKU (FULL upload). Maps by SKU=vendorCode;
# offers whose card isn't created yet come back notMapped (harmless). Uses same title templates
# so <model> matches the card name.
import json, re, html, os, datetime
BASE=os.path.dirname(os.path.abspath(__file__))
DATA=BASE+"/data"
OUT=BASE+"/out"
os.makedirs(OUT,exist_ok=True)
def wtok():
    for line in open("/home/user/cian_project/.env",encoding="utf-8"):
        if line.startswith("WB_KZ_TOKEN="): return line.split("=",1)[1].strip()
import requests
compat_opts=json.load(open(DATA+"/compat_opts.json")); compat_lc={k.lower():v for k,v in compat_opts.items()}
color_opts=json.load(open(DATA+"/color_opts.json")); color_lc={k.lower() for k in color_opts}
cards={c["vendorCode"]:c for c in json.load(open(DATA+"/wb_cards.json"))}
prices={g["nmID"]:g for g in requests.get("https://discounts-prices-api.wildberries.ru/api/v2/list/goods/filter?limit=1000",headers={"Authorization":wtok()},timeout=40).json()["data"]["listGoods"]}
stock=json.load(open(DATA+"/stock.json"))
def norm(s): return re.sub(r'\s+',' ',s.strip().lower()).replace('ё','е')
CANON_ID={norm(k):v for k,v in compat_opts.items()}
CANON_NM={norm(k):k for k in compat_opts}
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
COLOR_ALIAS={"фуксия":"Малиновый","ярко-розовый":"Малиновый","розовый неон":"Малиновый","апельсин":"Оранжевый","графит":"Темно-серый"}
def color_of(c):
    wc=next((ch["value"] for ch in c["characteristics"] if ch["name"]=="Цвет"),[])
    for v in wc:
        if v.lower() in color_lc: return next(k for k in color_opts if k.lower()==v.lower())
    for v in wc:
        if v.lower() in COLOR_ALIAS: return COLOR_ALIAS[v.lower()]
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
        d=cn[6:] if cn.startswith("apple ") else cn
        return d.title().replace("Iphone","iPhone").replace(" Fe"," FE").replace(" Se"," SE")
    return model_from_title(c)
def type_of(sku):
    p=sku.split("-")[0]
    if p in ("c7","c10","c5","c6","c2"): return p
    if p in ("b1","b2","b3","b5"): return "book"
    return "softtouch"
TITLE={"c7":"Чехол для %s %s из пластика с металлической камерой-подставкой и MagSafe",
 "c10":"Дизайнерский чехол для %s %s из пластика с MagSafe и защитой камеры",
 "c6":"Мягкий тканевый чехол для %s %s с soft-touch покрытием и защитой камеры",
 "c5":"Кожаный чехол для %s %s с кольцом-подставкой и поддержкой беспроводной зарядки",
 "c2":"Чехол с кольцом-подставкой для %s %s из пластика с защитой камеры",
 "softtouch":"Чехол Soft Touch для %s %s из силикона с защитой камеры",
 "book":"Чехол-книжка для %s %s из экокожи с отделением для карт и подставкой"}
offers=[]; skipped=0
for sku in sorted(cards):
    c=cards[sku]; typ=type_of(sku); m=model_disp(sku,c); col=color_of(c); g=prices.get(c["nmID"])
    if not (m and col and g): skipped+=1; continue
    price=int(round(g["sizes"][0]["discountedPrice"])); qty=stock.get(sku,[0]*13)[12]
    if typ=="book":
        slots="3 отделениями" if sku.split("-")[0] in ("b1","b2","b5") else "несколькими отделениями"
        raw="Чехол-книжка для %s %s из экокожи с %s для карт и подставкой"%(m,col.lower(),slots)
    else:
        raw=TITLE[typ]%(m,col.lower())
    title=html.escape(raw); bc=c["sizes"][0]["skus"][0]
    offers.append('<offer sku="%s"><model>%s</model><brand>No Name</brand><barcodes><barcode>%s</barcode></barcodes><stocks><stock available="yes" storeId="Bricase KZ_pp1" isPP="yes" stockLevel="%d"/></stocks><price>%d</price><loanPeriod>3</loanPeriod></offer>'%(sku,title,bc,qty,price))
today=datetime.date.today().isoformat()
xml='<?xml version="1.0" encoding="utf-8"?>\n<merchant_offers date="%s" xmlns="halyk_market" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n<company>Bricase KZ</company>\n<merchantid>000117600035</merchantid>\n<offers>'%today+"".join(offers)+'</offers>\n</merchant_offers>'
open(OUT+"/price_all.xml","w",encoding="utf-8").write(xml)
print("price_all.xml rebuilt: %d offers, %d skipped(unresolvable)"%(len(offers),skipped))
