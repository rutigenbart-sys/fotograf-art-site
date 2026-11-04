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
grid.addEventListener('click',e=>{const b=e.target.closest('.gi'); if(!b||!window.PLB)return;
  const list=items.map(x=>{const t=x.querySelector('img'); return {full:x.dataset.full,thumb:t.currentSrc||t.src,alt:t.alt}});
  PLB.open(list,items.indexOf(b),b);});
})();
