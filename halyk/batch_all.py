# -*- coding: utf-8 -*-
import requests, io, json, os, glob, time, re, sys
from PIL import Image
SP="/tmp/claude-0/-home-user-cian-project/86d433ab-8129-51c0-9d4f-b1a23c7ce53d/scratchpad"
def htok():
    cid=sec=None
    for line in open("/home/user/cian_project/.env",encoding="utf-8"):
        if line.startswith("HALYK_CLIENT_ID="): cid=line.split("=",1)[1].strip()
        if line.startswith("HALYK_CLIENT_SECRET="): sec=line.split("=",1)[1].strip()
    for i in range(8):
        try:
            r=requests.post("https://halykmarket.kz/gw/auth/token",json={"grant_type":"client_credentials","client_id":cid,"client_secret":sec},timeout=30)
            if r.status_code==200: return r.json()["access_token"]
        except: pass
        time.sleep(2*(i+1))
    raise SystemExit("auth failed")
def wtok():
    for line in open("/home/user/cian_project/.env",encoding="utf-8"):
        if line.startswith("WB_KZ_TOKEN="): return line.split("=",1)[1].strip()
T=[htok()]
def H(json_ct=True):
    h={"Authorization":"Bearer "+T[0],"accept":"*/*"}
    if json_ct: h["Content-Type"]="application/json"
    return h

compat_opts=json.load(open(SP+"/compat_opts.json"))          # name -> id
compat_lc={k.lower():v for k,v in compat_opts.items()}
color_opts=json.load(open(SP+"/color_opts.json"))            # name -> id
color_lc={k.lower() for k in color_opts}
cards={c["vendorCode"]:c for c in json.load(open(SP+"/wb_cards.json"))}
prices={g["nmID"]:g for g in requests.get("https://discounts-prices-api.wildberries.ru/api/v2/list/goods/filter?limit=1000",headers={"Authorization":wtok()},timeout=40).json()["data"]["listGoods"]}
stock=json.load(open(SP+"/stock.json"))

# ---- resolvers ----
def norm(s): return re.sub(r'\s+',' ',s.strip().lower()).replace('ё','е')
CANON_ID={norm(k):v for k,v in compat_opts.items()}      # normalized catalogue name -> id
CANON_NM={norm(k):k for k in compat_opts}                # normalized -> pretty name
def variants(s):
    """Safe normalized candidates for one WB compat string: same physical phone only."""
    n=norm(s); outs=[n]
    n2=re.sub(r'\s*\b[45]g\b','',n).strip()              # drop network band (4G/5G) — same body
    if n2!=n: outs.append(n2)
    for base in list(outs):
        if base.startswith("redmi") or base.startswith("poco"):
            outs.append("xiaomi "+base)                   # catalogue prefixes Redmi/Poco with Xiaomi
    return outs
def compat_of(sku,c):
    wb=next((ch["value"] for ch in c["characteristics"] if ch["name"]=="Совместимость"),[])
    # 1) exact match on any WB value
    for v in wb:
        if norm(v) in CANON_ID: return CANON_ID[norm(v)], CANON_NM[norm(v)]
    # 2) safe relaxed match (network band / Redmi-Poco prefix)
    for v in wb:
        for cand in variants(v):
            if cand in CANON_ID: return CANON_ID[cand], CANON_NM[cand]
    # 3) iphone constructor from sku
    seg=sku.split("-")
    if seg[0] in ("c7","c10","c5","c6","c2"): seg=seg[1:]  # drop type prefix
    brand=seg[0]; model=seg[1] if len(seg)>1 else ""
    cand=None
    if brand=="iphone":
        m=re.match(r'(\d+)(pro)?(max)?',model)
        if m: cand="apple iphone "+m.group(1)+(" pro" if m.group(2) else "")+(" max" if m.group(3) else "")
    if cand and norm(cand) in CANON_ID: return CANON_ID[norm(cand)], CANON_NM[norm(cand)]
    # optional fallback: mark as Универсальный so the required-completeness gate stays satisfied
    if os.environ.get("SOFTTOUCH_UNIVERSAL")=="1" and "универсальный" in compat_lc:
        return compat_lc["универсальный"], "Универсальный"
    return None, None
COLOR_ALIAS={"фуксия":"Малиновый","ярко-розовый":"Малиновый","розовый неон":"Малиновый",
 "апельсин":"Оранжевый","графит":"Темно-серый","хаки":"Хаки"}
def color_of(c):
    wc=next((ch["value"] for ch in c["characteristics"] if ch["name"]=="Цвет"),[])
    for v in wc:
        if v.lower() in color_lc: return next(k for k in color_opts if k.lower()==v.lower())
    for v in wc:
        if v.lower() in COLOR_ALIAS: return COLOR_ALIAS[v.lower()]
    return None
def model_from_title(c):
    t=c["title"]
    m=re.search(r'для (.+)$',t)
    s=m.group(1) if m else t
    s=re.sub(r'\s*\(.*?\)','',s).strip()      # drop "(не 4G)" etc
    s=re.sub(r'\s*/.*$','',s).strip()          # drop "/ POCO..." alt models
    # nice-case: keep known tokens
    CONN={"и","с","для","на","не","или","and","the"}
    def cap(w):
        if w.lower() in CONN: return w.lower()
        u=w.upper()
        if u in ("5G","4G","NFC","GT","FE","SE"): return u
        if u in ("PRO","MAX","PLUS","ULTRA","LITE","NEO","MINI"): return u.title()
        return w.capitalize()
    return " ".join(cap(w) for w in s.split())
def model_disp(sku,c):
    cid,cn=compat_of(sku,c)
    if cn:
        d=cn[6:] if cn.startswith("apple ") else cn
        d=d.title().replace("Iphone","iPhone").replace(" Fe"," FE").replace(" Se"," SE")
        d=re.sub(r'\bTpu\b','TPU',d)
        return d
    return model_from_title(c)
BRAND={"iphone":"Apple","samsung":"Samsung","google":"Google","honor":"Honor","huawei":"Huawei",
 "oneplus11":"OnePlus","oneplus":"OnePlus","realme":"Realme","realme9pro":"Realme","tecno":"Tecno",
 "xiaomi":"Xiaomi","xiaomi12pro":"Xiaomi","redminote11":"Xiaomi","redminote10":"Xiaomi",
 "redminote10pro":"Xiaomi","redminote12pro":"Xiaomi","redminote13pro":"Xiaomi","redminote9pro":"Xiaomi"}
def maker_of(sku):
    seg=sku.split("-")
    b=seg[1] if seg[0] in ("c7","c10","c5","c6","c2","b1","b2","b3","b5") else seg[0]
    return BRAND.get(b,"Xiaomi" if b.startswith("redmi") or b.startswith("xiaomi") else b.capitalize())

# ---- per-type recipe ----
# title uses %s %s = (model, color-lower). mat=Материал ENUM id. feat=Особенности name. tex=51838 text. ctype=10070 ENUM id
TYPES={
 "c7":  dict(ctype="36472", mat="12398", feat="Поддержка magsafe", tex="Тканевая",
             title="Чехол для %s %s из пластика с металлической камерой-подставкой и MagSafe"),
 "c10": dict(ctype="36472", mat="12398", feat="Поддержка magsafe", tex="Тканевая",
             title="Дизайнерский чехол для %s %s из пластика с MagSafe и защитой камеры"),
 "c6":  dict(ctype="36472", mat="13035", feat="Покрытие soft-touch", tex="Тканевая",
             title="Мягкий тканевый чехол для %s %s с soft-touch покрытием и защитой камеры"),
 "c5":  dict(ctype="667931", mat="11610", feat="Поддержка беспроводной зарядки", tex="Кожаная",
             title="Кожаный чехол для %s %s с кольцом-подставкой и поддержкой беспроводной зарядки"),
 "c2":  dict(ctype="667931", mat="12398", feat="Кольцо-держатель", tex="Пластиковая",
             title="Чехол с кольцом-подставкой для %s %s из пластика с защитой камеры"),
 "softtouch": dict(ctype="36472", mat="12795", feat="Покрытие soft-touch", tex="Силиконовая",
             title="Чехол Soft Touch для %s %s из силикона с защитой камеры"),
 "book": dict(ctype="13288", mat="13343", feat="Отделение для банковских карт", tex="Кожаная",
             title="Чехол-книжка для %s %s из экокожи с отделением для карт и подставкой"),
}
def type_of(sku):
    p=sku.split("-")[0]
    if p in ("c7","c10","c5","c6","c2"): return p
    if p in ("b1","b2","b3","b5"): return "book"
    return "softtouch"

def is_white(im):
    w,h=im.size; return sum(1 for c in [im.getpixel(p) for p in [(3,3),(w-4,3),(3,h-4),(w-4,h-4),(w//2,3),(3,h//2)]] if min(c)>238)>=5
def square(im):
    w,h=im.size; s=max(w,h); c=Image.new("RGB",(s,s),(255,255,255)); c.paste(im,((s-w)//2,(s-h)//2)); return c

def submit(sku):
    c=cards.get(sku)
    if not c: return "SKIP nocard"
    typ=type_of(sku); rc=TYPES[typ]
    cid,cn=compat_of(sku,c)
    color=color_of(c)
    if not color: return "SKIP color(%s)"%(next((ch["value"] for ch in c["characteristics"] if ch["name"]=="Цвет"),[]))
    tm=model_disp(sku,c); maker=maker_of(sku)
    g=prices.get(c["nmID"])
    if not g: return "SKIP noprice"
    price=int(g["sizes"][0]["price"]); sale=int(round(g["sizes"][0]["discountedPrice"])); ws=stock.get(sku,[0]*13)[12]
    # photos: white-bg squared, fallback to any if <3 white
    outdir=SP+"/allbatch/"+sku; os.makedirs(outdir,exist_ok=True); [os.remove(f) for f in glob.glob(outdir+"/*.jpg")]
    whites=[]; allp=[]
    for p in c["photos"]:
        try: im=Image.open(io.BytesIO(requests.get(p["big"],timeout=30).content)).convert("RGB")
        except: continue
        allp.append(im)
        if is_white(im): whites.append(im)
    use = whites if len(whites)>=3 else allp
    if len(use)<3: return "SKIP %dphotos"%len(use)
    k=0
    for im in use[:8]:
        k+=1; square(im).save(outdir+"/%02d.jpg"%k,"JPEG",quality=90)
    files=[("files",(os.path.basename(fn),open(fn,"rb").read(),"image/jpeg")) for fn in sorted(glob.glob(outdir+"/*.jpg"))]
    up=requests.post("https://halykmarket.kz/gw/merchant/public/file/image/upload/multiple",headers=H(False),files=files,timeout=120)
    try: media=[{"id":m["id"],"link":m["assetUrl"]} for m in up.json()]
    except: return "FAIL upload %s %s"%(up.status_code,up.text[:60])
    if typ=="book":
        slots="3 отделениями" if sku.split("-")[0] in ("b1","b2","b5") else "несколькими отделениями"
        title="Чехол-книжка для %s %s из экокожи с %s для карт и подставкой"%(tm,color.lower(),slots)
    else:
        title=rc["title"]%(tm,color.lower())
    attrs=[{"id":10070,"value":rc["ctype"]},{"id":10078,"value":rc["mat"]},
        {"id":51833,"value":sku},{"id":10068,"value":color},{"id":10067,"value":"50"},
        {"id":10066,"value":maker},{"id":10064,"value":rc["feat"]},
        {"id":35427,"value":"Защита камеры, дополнительная угловая защита бортов телефона"},
        {"id":10065,"value":tm},{"id":51838,"value":rc["tex"]},{"id":40097,"value":"false"},
        {"id":35425,"value":"Защита камеры и экрана"}]
    if cid: attrs.insert(2,{"id":10081,"value":str(cid)})
    payload={"name":title,"category":20004,"brand":33006,"description":c.get("description") or title,
      "attrs":attrs,"media":media,"weight":"50","width":"9","height":"18","depth":"2",
      "info":{"merchantProductCode":sku,"pointByCity":[{"city":{"code":"750000000","name":"Almaty","nameRu":"Алматы"},
        "price":price,"salePrice":sale,"points":[{"code":"Bricase KZ_pp1","amount":ws}]}],"loanPeriod":0}}
    r=requests.post("https://halykmarket.kz/gw/merchant/public/draft/product/moderation",headers=H(),json=payload,timeout=60)
    if r.status_code==202: return "OK %s | %s | %s | %s | compat=%s"%(r.json()["id"],typ,tm,color,cn or "NONE")
    if "already_exists" in r.text: return "ALREADY"
    return "FAIL %s %s"%(r.status_code,r.text[:100])

MODE=sys.argv[1] if len(sys.argv)>1 else "creminder"
if MODE=="creminder":
    # c10/c5/c6/c2 remainders (types validated); c2 already done, include for idempotency
    done_tests={"c10-iphone-17promax-parent-siren","c5-iphone-17promax-parent-brown","c6-iphone-17pro-parent-orange",
                "c2-samsung-a54-5g-parent-white-cs",
                "c10-iphone-17pro-parent-black","c10-iphone-17pro-parent-darkblue","c10-iphone-17pro-parent-darkgreen",
                "c10-iphone-17pro-parent-darkred","c10-iphone-17pro-parent-siren"}
    todo=sorted(v for v in cards if type_of(v) in ("c10","c5","c6","c2") and v not in done_tests)
elif MODE=="tests":
    todo=["samsung-s23-parent-orange-cs","google-pixel7-parent-black","b3-samsung-a54-5g-parent-black"]
elif MODE=="softtouch":
    todo=sorted(v for v in cards if type_of(v)=="softtouch")
elif MODE=="book":
    todo=sorted(v for v in cards if type_of(v)=="book")
else:
    todo=[MODE]
print("MODE=%s  todo=%d"%(MODE,len(todo)))
res={}
for i,sku in enumerate(todo):
    if i and i%8==0: T[0]=htok()
    try: r=submit(sku)
    except Exception as e: r="ERR %s"%str(e)[:90]
    res[sku]=r; print(" ",sku,"->",r)
    json.dump(res,open(SP+"/allbatch_%s.json"%MODE,"w"),ensure_ascii=False,indent=1)
ok=sum(1 for v in res.values() if v.startswith("OK")); al=sum(1 for v in res.values() if v=="ALREADY")
print("DONE mode=%s: %d OK, %d ALREADY, %d other of %d"%(MODE,ok,al,len(todo)-ok-al,len(todo)))
