const $=i=>document.getElementById(i),usd=v=>'$'+v.toLocaleString('fr-FR',{minimumFractionDigits:2,maximumFractionDigits:2}),esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function home(){const S=YGO_SETS,I=YGO_INFO;$('dt').textContent=I.date;
$('stat').innerHTML=`<b>${I.sets}</b> extensions · <b>${I.printings.toLocaleString('fr-FR')}</b> cartes (impressions) · Total global : <b>${usd(I.grand)}</b>`;
[...new Set(S.map(s=>(s.d||'').slice(0,4)).filter(x=>x))].sort().reverse().forEach(y=>$('y').add(new Option(y,y)));
const r=()=>{const q=$('q').value.toLowerCase(),y=$('y').value,[k,o]=[$('s').value[0],$('s').value[1]];
let L=S.filter(s=>(!q||(s.n+' '+s.c).toLowerCase().includes(q))&&(!y||(s.d||'').startsWith(y)));
L.sort((a,b)=>{let x=a[k]||'',z=b[k]||'';let c=typeof x=='number'?x-z:String(x).localeCompare(String(z));return o=='+'?c:-c});
$('tb').innerHTML=L.map(s=>`<tr><td><a href="set.html?s=${s.s}">${esc(s.n)}</a>${s.m?` <span class="mut warn">(${s.m} prix indisponible${s.m>1?'s':''})</span>`:''}</td><td class="hide-m mut">${esc(s.c)}</td><td class="mut">${s.d||'—'}</td><td class="num">${s.p}</td><td class="num"><b>${usd(s.t)}</b></td></tr>`).join('')};
['q','y','s'].forEach(i=>$(i).oninput=r);r()}
function setPage(){const k=new URLSearchParams(location.search).get('s'),m=YGO_SETS.find(s=>s.s==k);$('dt').textContent=YGO_INFO.date;
if(!m){$('h').textContent='Extension introuvable';return}document.title=m.n+' – Yu-Gi-Oh!';$('h').textContent=m.n;
const sc=document.createElement('script');sc.src='data/set-'+k+'.js';sc.onload=()=>{const R=YGO_SET.rows;let sk=3,so=-1;
$('stat').innerHTML=`Prix total de l'extension : <b>${usd(m.t)}</b> · ${m.p} cartes · ${m.c} · ${m.d||''}${m.m?` · <span class="warn">${m.m} prix indisponible(s)</span>`:''}`;
[...new Set(R.map(x=>x[2]))].sort().forEach(x=>$('r').add(new Option(x,x)));
const d=()=>{const q=$('q').value.toLowerCase(),ra=$('r').value;let L=R.filter(x=>(!q||(x[0]+' '+x[1]).toLowerCase().includes(q))&&(!ra||x[2]==ra));
L.sort((a,b)=>(sk==3?a[3]-b[3]:String(a[sk]).localeCompare(b[sk]))*so);const t=L.reduce((s,x)=>s+x[3],0);
$('tb').innerHTML=L.map(x=>`<tr><td class="hide-m"><img class="th" loading="lazy" src="${x[4]}" alt=""></td><td>${esc(x[0])}<div class="mut">${esc(x[5])}</div></td><td class="mut">${esc(x[1])}</td><td>${esc(x[2])}</td><td class="num">${x[3]?usd(x[3]):'<span class="warn">indispo.</span>'}</td></tr>`).join('')+(L.length!=R.length?`<tr><td colspan=5 class="num">Total filtré : <b>${usd(t)}</b></td></tr>`:'')};
document.querySelectorAll('th[data-k]').forEach(th=>th.onclick=()=>{const n=+th.dataset.k;so=sk==n?-so:1;sk=n;d()});['q','r'].forEach(i=>$(i).oninput=d);d()};document.head.appendChild(sc)}
