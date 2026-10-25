#!/usr/bin/env python3
"""Génère data/*.js depuis raw/cardinfo.json + raw/cardsets.json.
Rafraîchir: python3 build.py --download"""
import json, urllib.request, os, re, sys, datetime, subprocess
B=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(B,'raw'); D=os.path.join(B,'data')
if '--download' in sys.argv:
    os.makedirs(R,exist_ok=True)
    for f in ('cardinfo','cardsets'):
        subprocess.check_call(['curl','-s','-o',os.path.join(R,f+'.json'),f'https://db.ygoprodeck.com/api/v7/{f}.php'])
# Taux USD->EUR (Frankfurter/BCE). Prix convertis à la construction, arrondis par carte; totaux = somme des prix affichés.
try:
    _fx=json.load(urllib.request.urlopen(urllib.request.Request('https://api.frankfurter.dev/v1/latest?from=USD&to=EUR',headers={'User-Agent':'site-yugioh-build'}),timeout=20)); RATE=_fx['rates']['EUR']; RATE_DATE=_fx['date']
    json.dump(_fx,open(os.path.join(R,'fx.json'),'w'))
except Exception:
    _fx=json.load(open(os.path.join(R,'fx.json'))); RATE=_fx['rates']['EUR']; RATE_DATE=_fx['date']
cards=json.load(open(os.path.join(R,'cardinfo.json')))['data']
meta={s['set_name']:s for s in json.load(open(os.path.join(R,'cardsets.json')))}
def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')[:60] or 'set'
def price(p):
    try: return float(p)
    except: return 0.0
# Cascade de prix par impression: src 0=exact, 1=impression soeur (même carte/extension/rareté), 2=prix moyen carte, 3=indispo
def num(code): m=re.search(r'(\d+)$',code or ''); return int(m.group(1)) if m else None
sets={};dups=0;CI={}
for c in cards:
    img=c['card_images'][0]['id'] if c.get('card_images') else 0
    CI[img]=dict(t=c.get('type',''),d=c.get('desc',''),r=c.get('race',''),a=c.get('attribute',''),l=c.get('level'),k=c.get('atk'),f=c.get('def'))
    cp=(c.get('card_prices') or [{}])[0]
    cardp=price(cp.get('tcgplayer_price'))
    if cardp<=0: cardp=next((price(cp.get(k)) for k in ('ebay_price','amazon_price','coolstuffinc_price') if price(cp.get(k))>0),0.0)
    seen=set();prs=[]
    for p in c.get('card_sets') or []:
        key=(p['set_name'],p.get('set_code',''),p.get('set_rarity',''))
        if key in seen: dups+=1; continue
        seen.add(key);prs.append(p)
    for p in prs:
        v=price(p.get('set_price'));src=0
        if v<=0:
            sib=[price(q.get('set_price')) for q in prs if q is not p and q['set_name']==p['set_name'] and q.get('set_rarity')==p.get('set_rarity') and price(q.get('set_price'))>0]
            same=[x for q,x in zip(prs,[price(q.get('set_price')) for q in prs]) if q is not p and q['set_name']==p['set_name'] and q.get('set_rarity')==p.get('set_rarity') and x>0 and num(q.get('set_code'))==num(p.get('set_code'))]
            if same or sib: v=(same or sib)[0];src=1
            elif cardp>0: v=cardp;src=2
            else: src=3
        sets.setdefault(p['set_name'],[]).append([c['name'],p.get('set_code',''),p.get('set_rarity',''),round(v*RATE,2),img,c.get('type',''),src])
os.makedirs(D,exist_ok=True)
for f in os.listdir(D): os.remove(os.path.join(D,f))
idx=[];used=set();grand=0;n=0;cnt=[0,0,0,0]
for name,rows in sets.items():
    s=slug(name);k=s;i=2
    while k in used: k=f'{s}-{i}';i+=1
    used.add(k)
    tot=round(sum(r[3] for r in rows),2); miss=sum(1 for r in rows if r[6]==3); est=round(sum(r[3] for r in rows if r[6] in(1,2)),2); ne=sum(1 for r in rows if r[6] in(1,2))
    m=meta.get(name,{})
    idx.append(dict(n=name,s=k,c=(m.get('set_code') or (rows[0][1].split('-')[0])),d=m.get('tcg_date',''),p=len(rows),t=tot,m=miss,e=est,ne=ne,i=1 if m.get('set_code') and os.path.exists(os.path.join(B,'img','s',m['set_code']+'.webp')) else 0))
    grand+=tot;n+=len(rows)
    for r in rows: cnt[r[6]]+=1
    with open(os.path.join(D,f'set-{k}.js'),'w') as f:
        info_c={r[4]:CI[r[4]] for r in rows}
        f.write('window.YGO_SET='+json.dumps(dict(n=name,rows=rows,cards=info_c),ensure_ascii=False,separators=(',',':'))+';')
info=dict(rate=RATE,rate_date=RATE_DATE,date=datetime.date.today().isoformat(),grand=round(grand,2),printings=n,sets=len(idx),src=cnt,dups=dups,est=round(sum(x['e'] for x in idx),2))
with open(os.path.join(D,'sets-index.js'),'w') as f:
    f.write('window.YGO_INFO='+json.dumps(info)+';window.YGO_SETS='+json.dumps(idx,ensure_ascii=False,separators=(',',':'))+';')
print(info)
