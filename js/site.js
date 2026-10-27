(()=>{
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const body=document.body; requestAnimationFrame(()=>body.classList.add('loaded'));
const yr=$('#yr'); if(yr) yr.textContent=new Date().getFullYear();
const hdr=$('#hdr'), fab=$('#fab');
const onScroll=()=>{const y=scrollY; hdr&&hdr.classList.toggle('solid',y>40); fab&&fab.classList.toggle('show',y>innerHeight*.5);};
addEventListener('scroll',onScroll,{passive:true}); onScroll();
const burger=$('#burger');
const setMenu=o=>{body.classList.toggle('menu-open',o);burger.setAttribute('aria-expanded',o);body.style.overflow=o?'hidden':''};
if(burger){burger.onclick=()=>setMenu(!body.classList.contains('menu-open')); $$('#mnav a').forEach(a=>a.addEventListener('click',()=>setMenu(false)));}
document.addEventListener('click',e=>{const a=e.target.closest('a[href]'); if(!a)return; const h=a.getAttribute('href');
  const goal=h.startsWith('tel:')?'call':h.includes('wa.me')?'whatsapp':h.includes('t.me')?'telegram':h.includes('max.ru')?'max':null; if(goal&&window.siteGoal)window.siteGoal(goal);},true);
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
if('IntersectionObserver' in window&&!reduce){
  const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{rootMargin:'0px 0px -8% 0px'});
  $$('.rv').forEach(el=>{const r=el.getBoundingClientRect(); if(r.top<innerHeight)el.classList.add('in'); else io.observe(el);});
}else $$('.rv').forEach(el=>el.classList.add('in'));
})();

/* ---- service page gallery + lightbox ---- */
(()=>{
const grid=document.getElementById('sgrid'); if(!grid)return;
const $=s=>document.querySelector(s), items=[...grid.querySelectorAll('.gi')], more=$('#smore');
const STEP=matchMedia('(max-width:759px)').matches?10:12; let limit=STEP;
items.forEach(b=>{const im=b.querySelector('img'); if(im.complete)im.classList.add('ld'); else im.addEventListener('load',()=>im.classList.add('ld'),{once:true});});
const render=()=>{items.forEach((b,i)=>b.hidden=i>=limit); more.parentElement.hidden=items.length<=limit;};
more.onclick=()=>{limit+=STEP;render();}; render();
const lb=$('#lb'), img=$('#lbImg'); let li=0, last=null;
const show=k=>{li=(k+items.length)%items.length; const b=items[li], t=b.querySelector('img');
  img.classList.add('sw'); const n=new Image(); n.src=b.dataset.full;
  const put=()=>{img.src=n.src; img.alt=t.alt; img.classList.remove('sw');}; n.decode?n.decode().then(put,put):(n.onload=put);
  $('#lbN').textContent=String(li+1).padStart(2,'0')+' / '+String(items.length).padStart(2,'0'); $('#lbAlt').textContent=t.alt;
  [items[li+1],items[li-1]].forEach(x=>{if(x){const p=new Image();p.src=x.dataset.full}});};
const open=i=>{last=document.activeElement; lb.hidden=false; requestAnimationFrame(()=>lb.classList.add('open')); document.body.style.overflow='hidden'; show(i); $('#lbX').focus();};
const close=()=>{lb.classList.remove('open'); document.body.style.overflow=''; setTimeout(()=>{lb.hidden=true},350); last&&last.focus();};
grid.addEventListener('click',e=>{const b=e.target.closest('.gi'); if(b)open(items.indexOf(b));});
$('#lbX').onclick=close; $('#lbP').onclick=()=>show(li-1); $('#lbNx').onclick=()=>show(li+1);
$('#lbSt').addEventListener('click',e=>{if(e.target.id==='lbSt')close();});
addEventListener('keydown',e=>{if(lb.hidden)return; if(e.key==='Escape')close(); if(e.key==='ArrowRight')show(li+1); if(e.key==='ArrowLeft')show(li-1);});
let sx=0,sy=0;
lb.addEventListener('touchstart',e=>{sx=e.touches[0].clientX;sy=e.touches[0].clientY},{passive:true});
lb.addEventListener('touchend',e=>{const dx=e.changedTouches[0].clientX-sx, dy=e.changedTouches[0].clientY-sy;
  if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy))show(li+(dx<0?1:-1)); else if(dy>90&&Math.abs(dy)>Math.abs(dx))close();},{passive:true});
})();
