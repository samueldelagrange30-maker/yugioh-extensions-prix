#!/usr/bin/env python3
"""Télécharge (une fois) et ré-héberge les images en WebP: img/c/<id>.webp (cartes), img/s/<CODE>.webp (extensions).
Ne retélécharge pas ce qui existe déjà. Respecte la demande de YGOPRODeck de ne pas hotlinker."""
import json,os,io,urllib.request,time
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
B=os.path.dirname(os.path.abspath(__file__))
C=json.load(open(f'{B}/raw/cardinfo.json'))['data'];S=json.load(open(f'{B}/raw/cardsets.json'))
jobs=[(f'https://images.ygoprodeck.com/images/cards_small/{c["card_images"][0]["id"]}.jpg',f'{B}/img/c/{c["card_images"][0]["id"]}.webp',None) for c in C if c.get('card_sets') and c.get('card_images')]
jobs+=[(s.get('set_image') or f'https://images.ygoprodeck.com/images/sets/{s["set_code"]}.jpg',f'{B}/img/s/{s["set_code"]}.webp',300) for s in S]
os.makedirs(f'{B}/img/c',exist_ok=True);os.makedirs(f'{B}/img/s',exist_ok=True)
fail=[]
def go(j):
    u,o,w=j
    if os.path.exists(o): return
    for a in range(3):
        try:
            d=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'site-yugioh-build'}),timeout=30).read()
            im=Image.open(io.BytesIO(d)).convert('RGB')
            if w and im.width>w: im=im.resize((w,int(im.height*w/im.width)))
            im.save(o,'WEBP',quality=72);time.sleep(0.1);return
        except Exception as e: err=e;time.sleep(1)
    fail.append((u,str(err)))
with ThreadPoolExecutor(6) as ex: list(ex.map(go,jobs))
print('jobs',len(jobs),'fails',len(fail));json.dump(fail,open(f'{B}/img/fails.json','w'))
