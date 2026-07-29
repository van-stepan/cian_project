# -*- coding: utf-8 -*-
# Wait for the 3 new-type test cards to clear moderation, then batch soft-touch(64)+book(22)
# accordingly, then rebuild+push the FULL price-list. Autonomous; writes FINAL_STATUS.json.
import requests, json, time, os, subprocess
SP="/tmp/claude-0/-home-user-cian-project/86d433ab-8129-51c0-9d4f-b1a23c7ce53d/scratchpad"
TESTS={"softtouch_compat":638619,"softtouch_nocompat":638620,"book":638623}
def tok():
    cid=sec=None
    for line in open("/home/user/cian_project/.env",encoding="utf-8"):
        if line.startswith("HALYK_CLIENT_ID="): cid=line.split("=",1)[1].strip()
        if line.startswith("HALYK_CLIENT_SECRET="): sec=line.split("=",1)[1].strip()
    for _ in range(8):
        try:
            r=requests.post("https://halykmarket.kz/gw/auth/token",json={"grant_type":"client_credentials","client_id":cid,"client_secret":sec},timeout=30)
            if r.status_code==200: return r.json()["access_token"]
        except: pass
        time.sleep(3)
    return None
def stat(T,i):
    try:
        d=requests.get("https://halykmarket.kz/gw/merchant/public/draft/product/%d"%i,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json"},timeout=30).json()
        p=d.get("productDraftResponse",{}); return p.get("status"), (d.get("comment") or "")
    except: return None,""
def wstat(o): json.dump(o,open(SP+"/FINAL_STATUS.json","w"),ensure_ascii=False,indent=1)

st={"phase":"waiting-moderation","verdicts":{},"softtouch":None,"book":None,"price":None}
verdicts={}
for cyc in range(80):                          # up to ~4h at 180s
    T=tok()
    if not T: time.sleep(180); continue
    for name,i in TESTS.items():
        if name in verdicts: continue
        s,c=stat(T,i)
        if s in ("SUCCESS","REJECT","REJECTED"):
            verdicts[name]={"status":s,"comment":c[:200]}
    st["verdicts"]=verdicts; wstat(st)
    if len(verdicts)==len(TESTS): break
    time.sleep(180)

def run(mode,env=None):
    e=dict(os.environ); e.update(env or {})
    r=subprocess.run(["python3",SP+"/batch_all.py",mode],capture_output=True,text=True,timeout=6000,env=e)
    open(SP+"/final_%s.log"%mode,"w").write(r.stdout+"\n---ERR---\n"+r.stderr)
    return r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "no-out"

st["phase"]="batching"; wstat(st)
# book
bv=verdicts.get("book",{}).get("status")
if bv=="SUCCESS": st["book"]=run("book")
else: st["book"]="HELD (book test verdict=%s)"%bv
# soft-touch
sc=verdicts.get("softtouch_compat",{}).get("status")
sn=verdicts.get("softtouch_nocompat",{}).get("status")
if sc=="SUCCESS" and sn=="SUCCESS":
    st["softtouch"]=run("softtouch")                     # blank compat is fine
elif sc=="SUCCESS":
    st["softtouch"]=run("softtouch",{"SOFTTOUCH_UNIVERSAL":"1"})  # no-compat rejected -> use Универсальный
else:
    st["softtouch"]="HELD (softtouch compat test verdict=%s)"%sc
wstat(st)

# rebuild + push full price-list
st["phase"]="pricing"; wstat(st)
subprocess.run(["python3",SP+"/build_price.py"],capture_output=True,text=True,timeout=300)
T=tok(); xml=open(SP+"/price_all.xml","rb").read()
pr=None
for _ in range(8):
    r=requests.post("https://api.halykmarket.com/api/merchant/v1/offers/upload",headers={"Authorization":"Bearer "+T},files={"file":("price_all.xml",xml,"application/xml")},timeout=90)
    if r.status_code==200:
        uid=r.json().get("id")
        for _ in range(40):
            time.sleep(6)
            try:
                d=requests.get("https://api.halykmarket.com/api/merchant/v1/offers/upload/status/%s"%uid,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json"},timeout=30).json()
                if d.get("status")!="PROCESSING":
                    pr="status=%s total=%s success=%s notMapped=%s fail=%s"%(d.get("status"),d.get("totalCount"),d.get("successCount"),d.get("notMappedCount"),d.get("failCount")); break
            except: pass
        break
    time.sleep(20); T=tok()
st["price"]=pr or "offers-upload still failing"
st["phase"]="done"; wstat(st)
print(json.dumps(st,ensure_ascii=False,indent=1))
