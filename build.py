import re,json
raw=json.load(open("raw.json"))
KW=re.compile(r"torin|toro|granat|superga|meroni|pulici|graziani|mazzola|mondonico|belotti",re.I)
def secs(l):
  p=[int(x) for x in l.split(":")] if l else [0];s=0
  for x in p:s=s*60+x
  return s
def dec(y):
  if y<1950:return "40"
  if y<1970:return "5060"
  return str(y//10*10)[2:] if y<2000 else str(y//10*10)
def season(t):
  m=re.search(r"(19[3-9]\d|20[0-2]\d)\s*[-/]\s*(\d{2,4})",t)
  if m:
    a=int(m.group(1));b=int(m.group(2)[-2:])
    if b==(a+1)%100:return a
  m=re.search(r"(\d{1,2})[./-](\d{1,2})[./-](19[3-9]\d|20[0-2]\d|\d{2})\b",t)
  if m:
    y=int(m.group(3));y=y if y>100 else (1900+y if y>30 else 2000+y);mo=int(m.group(2))
    if 1<=mo<=12:return y if mo>=8 else y-1
  m=re.search(r"\b(19[3-9]\d|20[0-2]\d)\b",t)
  if m:return int(m.group(1))-1  # year alone: assume spring
  return None
def giornata(t):
  m=re.search(r"(\d{1,2})\s*[aª°]?\s*giornata",t,re.I);return int(m.group(1)) if m else 99
def comp(t):
  for k,v in [("uefa","Coppa UEFA"),("europa league","Europa League"),("coppa italia","Coppa Italia"),("coppa coppe","Coppa delle Coppe"),("serie b","Serie B"),("playoff","Playoff Serie B"),("serie a","Serie A")]:
    if k in t.lower():return v
  return ""
seen=set();D={}
names={"40":"Anni '40 · Il Grande Torino","5060":"Anni '50-'60 · La Farfalla Granata","70":"Anni '70 · Lo Scudetto 1976","80":"Anni '80","90":"Anni '90 · Coppa UEFA 1992","2000":"Anni 2000","2010":"Anni 2010 · Europa League","2020":"Anni 2020 · Il Toro di oggi"}
for qd,vs in raw.items():
  for v in vs:
    if v["id"] in seen or not KW.search(v["t"]) or not v["len"]:continue
    seen.add(v["id"]);s=season(v["t"]);d=dec(s+1 if s and s%10==9 and False else s) if s else qd
    if s and d!=qd and abs(int(re.sub('5060','1950',d if len(d)==4 else '19'+d))-0)<0:pass
    sec=secs(v["len"]);ismatch=sec>=600 and re.search(r"\d\s*-\s*\d|\bvs\b|partita|completa| - [A-Z]",v["t"],re.I)
    sk=f"{s}-{str(s+1)[-2:]}" if s else "Varie"
    sc=re.search(r"(\d{1,2})\s*-\s*(\d{1,2})(?!\d)",v["t"])
    D.setdefault(d,{}).setdefault(sk,{"partite":[],"servizi":[]})["partite" if ismatch else "servizi"].append(
      {"id":v["id"],"titolo":v["t"],"durata":v["len"],"competizione":comp(v["t"]),"risultato":sc.group(0).replace(" ","") if sc and ismatch else "","giornata":giornata(v["t"])})
out=[]
for k in names:
  ss=D.get(k,{})
  stag=[]
  for sk in sorted(ss,key=lambda x:(x=="Varie",x)):
    p=ss[sk];p["partite"].sort(key=lambda x:x["giornata"])
    for L in p.values():
      for x in L:
        if x["giornata"]==99:del x["giornata"]
    stag.append({"stagione":sk,**p})
  out.append({"id":"d"+k,"nome":names[k],"stagioni":stag})
json.dump(out,open("videos.json","w"),ensure_ascii=False,indent=1)
open("videos.js","w").write("// Dati generati da videos.json: decennio > stagione > partite/servizi\nconst ARCHIVIO = "+json.dumps(out,ensure_ascii=False)+";\n")
for c in out:print(c["id"],"partite",sum(len(s["partite"]) for s in c["stagioni"]),"servizi",sum(len(s["servizi"]) for s in c["stagioni"]),[s["stagione"] for s in c["stagioni"]])
