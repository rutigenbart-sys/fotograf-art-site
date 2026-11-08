/* Плавность: инерционный скролл (Lenis), появление заголовков по буквам,
   плавное проявление блоков и фото, прогресс прокрутки.
   Без JS или при «уменьшить анимацию» всё остаётся видимым и работает. */
(()=>{
const html=document.documentElement, body=document.body;
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------- плавный скролл ---------- */
let lenis=null;
if(!reduce&&window.Lenis){
  try{
    lenis=new Lenis({duration:.6,easing:t=>Math.min(1,1.001-Math.pow(2,-10*t)),smoothWheel:true,wheelMultiplier:1.6,touchMultiplier:1.5});
    window.__lenis=lenis;
    const raf=t=>{lenis.raf(t);requestAnimationFrame(raf)}; requestAnimationFrame(raf);
    // открытое меню блокирует прокрутку
    new MutationObserver(()=>{body.classList.contains('menu-open')?lenis.stop():(html.classList.contains('plb-open')||lenis.start())}).observe(body,{attributes:true,attributeFilter:['class']});
    // плавные якоря
    document.addEventListener('click',e=>{
      const a=e.target.closest('a[href*="#"]'); if(!a||e.defaultPrevented||e.metaKey||e.ctrlKey)return;
      const u=new URL(a.href,location.href); if(u.pathname!==location.pathname||u.origin!==location.origin)return;
      if(!u.hash||u.hash==='#'){return}
      const t=document.getElementById(decodeURIComponent(u.hash.slice(1))); if(!t)return;
      e.preventDefault(); lenis.scrollTo(t,{offset:-72,duration:1.4}); history.replaceState(null,'',u.hash);
    });
  }catch(_){lenis=null}
}

/* ---------- полоса прогресса ---------- */
const bar=document.createElement('div'); bar.className='fx-bar'; bar.setAttribute('aria-hidden','true'); body.appendChild(bar);
const prog=()=>{const h=html.scrollHeight-innerHeight; bar.style.transform=`scaleX(${h>0?Math.min(1,scrollY/h):0})`};
addEventListener('scroll',prog,{passive:true}); addEventListener('resize',prog); prog();

/* ---------- заголовки по буквам ---------- */
const splitEl=(el)=>{
  if(el.dataset.split)return; el.dataset.split='1';
  const txt=el.textContent.replace(/\s+/g,' ').trim(); if(!txt)return;
  el.setAttribute('aria-label',txt);
  const byWord=txt.length>90; let k=0;
  const walk=node=>[...node.childNodes].forEach(ch=>{
    if(ch.nodeType===3){
      const frag=document.createDocumentFragment();
      ch.textContent.split(/(\s+)/).forEach(p=>{
        if(!p)return;
        if(/^\s+$/.test(p)){frag.appendChild(document.createTextNode(' '));return}
        const w=document.createElement('span'); w.className='w'; w.setAttribute('aria-hidden','true');
        if(byWord){const s=document.createElement('span');s.className='ch';s.style.setProperty('--i',k++);s.textContent=p;w.appendChild(s)}
        else [...p].forEach(c=>{const s=document.createElement('span');s.className='ch';s.style.setProperty('--i',k++);s.textContent=c;w.appendChild(s)});
        frag.appendChild(w);
      });
      ch.replaceWith(frag);
    }else if(ch.nodeType===1&&!ch.matches('br,svg,img')){walk(ch)}
  });
  walk(el); el.classList.add('fx-split');
};
const heads=[...document.querySelectorAll('h1,h2,.hero-h,.sp-h1')].filter(h=>!h.closest('.lb,.plb'));
if(!reduce)heads.forEach(splitEl);

/* ---------- появление ---------- */
const SEL='.rv,.gi,.card,.sv,.tk,.about-ph,.sp-art,.faq details,.steps li,.calc,.form,.dz-fact,.dz-zc,.dz-pl,.dz-cover,.dz-cta,.okr,.dz-aside>*,.dz-step,.fx-split';
const targets=[...new Set([...document.querySelectorAll(SEL)])];
let ready=!document.getElementById('pre'); // на главной ждём окончания прелоадера
const heroLate=[];
const show=(el,delay)=>{ if(delay)el.style.transitionDelay=delay+'ms'; el.classList.add('in'); };
if(!('IntersectionObserver' in window)||reduce){targets.forEach(el=>el.classList.add('in'))}
else{
  const io=new IntersectionObserver(es=>{
    let n=0;
    es.filter(e=>e.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top||a.boundingClientRect.left-b.boundingClientRect.left).forEach(e=>{
      const el=e.target; io.unobserve(el);
      if(!ready&&el.closest('.hero')){heroLate.push(el);return}
      show(el,el.classList.contains('fx-split')?0:Math.min(n++,7)*70);
    });
  },{rootMargin:'0px 0px -6% 0px',threshold:.06});
  targets.forEach(el=>io.observe(el));
  if(!ready){
    const go=()=>{ if(!body.classList.contains('loaded'))return; ready=true; setTimeout(()=>heroLate.splice(0).forEach((el,i)=>show(el,i*60)),350); mo.disconnect(); };
    const mo=new MutationObserver(go); mo.observe(body,{attributes:true,attributeFilter:['class']}); go();
  }
}
/* фото, догрузившиеся позже, остаются плавными */
document.querySelectorAll('img[loading="lazy"]').forEach(im=>{ if(!im.complete)im.addEventListener('load',()=>im.classList.add('ld'),{once:true}); else im.classList.add('ld'); });

/* ---------- блок районов: поиск и раскрытие ---------- */
const q=document.getElementById('rnQ');
if(q){
  const chips=[...document.querySelectorAll('.okr .chip')], okrs=[...document.querySelectorAll('.okr')];
  const wide=matchMedia('(min-width:900px)').matches; okrs.forEach(o=>{o.open=wide});
  const norm=s=>s.toLowerCase().replace(/ё/g,'е');
  q.addEventListener('input',()=>{
    const v=norm(q.value.trim());
    chips.forEach(c=>{c.hidden=v&&!norm(c.textContent).includes(v)});
    okrs.forEach(o=>{const any=[...o.querySelectorAll('.chip')].some(c=>!c.hidden); o.hidden=!any; if(v&&any)o.open=true});
  });
}
})();
