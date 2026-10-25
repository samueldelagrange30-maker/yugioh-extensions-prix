#!/usr/bin/env python3
"""Télécharge (avec cache) les données FR: raw/cardinfo_fr.json (YGOPRODeck language=fr) et raw/sets_fr.json
(noms FR des extensions depuis l'infobox fr_name de Yugipedia, requêtes groupées par 50, 1 req/s). --force pour rafraîchir."""
import json,os,re,sys,time,urllib.request,urllib.parse
B=os.path.dirname(os.path.abspath(__file__));R=os.path.join(B,'raw');F='--force' in sys.argv
UA={'User-Agent':'SiteYugiohPrix/1.0 (static fan site; https://samueldelagrange30-maker.github.io/yugioh-extensions-prix/)'}
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
p=os.path.join(R,'cardinfo_fr.json')
if F or not os.path.exists(p): json.dump(get('https://db.ygoprodeck.com/api/v7/cardinfo.php?language=fr'),open(p,'w'))
p=os.path.join(R,'sets_fr.json')
if F or not os.path.exists(p):
    names=sorted({s['set_name'] for s in json.load(open(os.path.join(R,'cardsets.json')))});out={}
    for i in range(0,len(names),50):
        b=names[i:i+50]
        q=urllib.parse.urlencode(dict(action='query',titles='|'.join(b),prop='revisions',rvprop='content',rvslots='main',redirects=1,format='json',formatversion=2))
        d=get('https://yugipedia.com/api.php?'+q)['query'];m={t:t for t in b}
        for k in ('normalized','redirects'):
            for x in d.get(k,[]):
                for o,t in list(m.items()):
                    if t==x['from']: m[o]=x['to']
        pg={x['title']:x for x in d.get('pages',[])}
        for o,t in m.items():
            try:
                c=pg[t]['revisions'][0]['slots']['main']['content'];r=re.search(r'^\|\s*fr_name\s*=\s*(.+?)\s*$',c,re.M)
                if r:
                    v=re.sub(r'<[^>]+>|\{\{[^}]*\}\}|\[\[(?:[^|\]]*\|)?([^\]]*)\]\]',lambda z:z.group(1) or '',r.group(1)).replace("''",'').strip()
                    if v: out[o]=v
            except (KeyError,IndexError): pass
        time.sleep(1.5)
    json.dump(out,open(p,'w'),ensure_ascii=False,indent=0)
print('ok')
