#!/usr/bin/env python3
"""Génère data/*.js depuis raw/cardinfo.json + raw/cardsets.json.
Rafraîchir: python3 build.py --download"""
import json, os, re, sys, datetime, subprocess
B=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(B,'raw'); D=os.path.join(B,'data')
if '--download' in sys.argv:
    os.makedirs(R,exist_ok=True)
    for f in ('cardinfo','cardsets'):
        subprocess.check_call(['curl','-s','-o',os.path.join(R,f+'.json'),f'https://db.ygoprodeck.com/api/v7/{f}.php'])
cards=json.load(open(os.path.join(R,'cardinfo.json')))['data']
meta={s['set_name']:s for s in json.load(open(os.path.join(R,'cardsets.json')))}
def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')[:60] or 'set'
def price(p):
    try: return float(p)
    except: return 0.0
sets={}
for c in cards:
    img=c['card_images'][0]['image_url_small'] if c.get('card_images') else ''
    for p in c.get('card_sets') or []:
        sets.setdefault(p['set_name'],[]).append([c['name'],p.get('set_code',''),p.get('set_rarity',''),round(price(p.get('set_price')),2),img,c.get('type','')])
os.makedirs(D,exist_ok=True)
for f in os.listdir(D): os.remove(os.path.join(D,f))
idx=[];used=set();grand=0;n=0
for name,rows in sets.items():
    s=slug(name);k=s;i=2
    while k in used: k=f'{s}-{i}';i+=1
    used.add(k)
    tot=round(sum(r[3] for r in rows),2); miss=sum(1 for r in rows if r[3]==0)
    m=meta.get(name,{})
    idx.append(dict(n=name,s=k,c=(m.get('set_code') or (rows[0][1].split('-')[0])),d=m.get('tcg_date',''),p=len(rows),t=tot,m=miss,i=m.get('set_image','')))
    grand+=tot;n+=len(rows)
    with open(os.path.join(D,f'set-{k}.js'),'w') as f:
        f.write('window.YGO_SET='+json.dumps(dict(n=name,rows=rows),ensure_ascii=False,separators=(',',':'))+';')
info=dict(date=datetime.date.today().isoformat(),grand=round(grand,2),printings=n,sets=len(idx))
with open(os.path.join(D,'sets-index.js'),'w') as f:
    f.write('window.YGO_INFO='+json.dumps(info)+';window.YGO_SETS='+json.dumps(idx,ensure_ascii=False,separators=(',',':'))+';')
print(info)
