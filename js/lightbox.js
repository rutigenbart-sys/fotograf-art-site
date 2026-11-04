/* Галерея: просмотр фото на весь экран.
   Свайп/перетаскивание работает в обе стороны (вперёд и назад), по кругу.
   Вертикальный свайп вниз закрывает. Системная кнопка «Назад» закрывает галерею,
   а не уходит со страницы. API: PLB.open(items, index, openerEl)
   items: [{full, thumb, alt, exif}] */
(()=>{
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
const ARROW='<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.4" d="M4 12h16m-6-6 6 6-6 6"/></svg>';
const ARROW_L='<svg viewBox="0 0 24 24" aria-hidden="true" style="transform:scaleX(-1)"><path fill="none" stroke="currentColor" stroke-width="1.4" d="M4 12h16m-6-6 6 6-6 6"/></svg>';
let root,st,tr,slides,cnt,capB,capS,btnX,btnP,btnN;
let items=[],cur=0,isOpen=false,opener=null,w=0,busy=false,drag=null,hinted=false;

function build(){
  root=document.createElement('div');
  root.className='plb'; root.hidden=true; root.setAttribute('role','dialog'); root.setAttribute('aria-modal','true'); root.setAttribute('aria-label','Просмотр фото');
  root.innerHTML='<div class="plb-top"><span class="plb-n"></span><button class="plb-x" type="button" aria-label="Закрыть"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5l14 14M19 5L5 19" stroke="currentColor" stroke-width="1.4" fill="none"/></svg></button></div>'
   +'<div class="plb-st"><div class="plb-tr">'+'<figure class="plb-sl"><img alt="" draggable="false"></figure>'.repeat(3)+'</div>'
   +'<button class="plb-nav plb-p" type="button" aria-label="Предыдущее фото">'+ARROW_L+'</button><button class="plb-nav plb-nx" type="button" aria-label="Следующее фото">'+ARROW+'</button></div>'
   +'<div class="plb-cap"><b></b><span></span></div><div class="plb-hint">Листайте влево и вправо</div>';
  document.body.appendChild(root);
  st=root.querySelector('.plb-st'); tr=root.querySelector('.plb-tr'); slides=[...tr.children];
  cnt=root.querySelector('.plb-n'); capB=root.querySelector('.plb-cap b'); capS=root.querySelector('.plb-cap span');
  btnX=root.querySelector('.plb-x'); btnP=root.querySelector('.plb-p'); btnN=root.querySelector('.plb-nx');
  btnX.addEventListener('click',()=>close());
  btnP.addEventListener('click',()=>go(-1)); btnN.addEventListener('click',()=>go(1));
  st.addEventListener('pointerdown',down); st.addEventListener('pointermove',move);
  st.addEventListener('pointerup',up); st.addEventListener('pointercancel',up);
  st.addEventListener('lostpointercapture',up);
  addEventListener('keydown',key); addEventListener('resize',()=>{if(isOpen){measure();rest(false)}});
  addEventListener('popstate',()=>{if(isOpen)close(true)});
}
const mod=i=>((i%items.length)+items.length)%items.length;
const measure=()=>{w=st.clientWidth||innerWidth};
const X=px=>`translate3d(${-w+px}px,0,0)`;
function rest(anim){
  tr.style.transition=anim&&!reduce?'transform .45s cubic-bezier(.16,1,.3,1)':'none';
  tr.style.transform=X(0);
}
function fill(sl,idx){
  const it=items[idx], im=sl.querySelector('img');
  if(sl.dataset.k===String(idx)&&im.getAttribute('src')===it.full)return;
  sl.dataset.k=idx; im.classList.remove('ld');
  sl.style.backgroundImage=it.thumb?`url("${it.thumb}")`:'';
  im.alt=it.alt||'';
  im.onload=()=>im.classList.add('ld');
  im.src=it.full; if(im.complete&&im.naturalWidth)im.classList.add('ld');
}
function paint(){
  // slides[0]=предыдущее, [1]=текущее, [2]=следующее
  fill(slides[0],mod(cur-1)); fill(slides[1],cur); fill(slides[2],mod(cur+1));
  const it=items[cur];
  cnt.textContent=String(cur+1).padStart(2,'0')+' / '+String(items.length).padStart(2,'0');
  capB.textContent=(it.alt||'').split('. ')[0]; capS.textContent=it.exif||'';
  slides.forEach((s,i)=>s.setAttribute('aria-hidden',i===1?'false':'true'));
  root.classList.toggle('one',items.length<2);
}
function go(dir){
  if(busy||items.length<2)return; busy=true; measure();
  tr.style.transition=reduce?'none':'transform .45s cubic-bezier(.16,1,.3,1)';
  tr.style.transform=X(-dir*w);
  let done=false;
  const fin=()=>{ if(done)return; done=true;
    cur=mod(cur+dir);
    if(dir>0){tr.appendChild(tr.firstElementChild)} else {tr.insertBefore(tr.lastElementChild,tr.firstElementChild)}
    slides=[...tr.children];
    tr.style.transition='none'; tr.style.transform=X(0);
    paint(); busy=false; };
  reduce?fin():(tr.addEventListener('transitionend',function h(e){if(e.target!==tr)return;tr.removeEventListener('transitionend',h);fin()}),setTimeout(fin,600));
}
function down(e){
  if(busy||(e.pointerType==='mouse'&&e.button!==0)||e.target.closest('.plb-nav'))return;
  measure();
  drag={id:e.pointerId,x:e.clientX,y:e.clientY,dx:0,dy:0,mode:null,lx:e.clientX,lt:performance.now(),v:0};
  try{st.setPointerCapture(e.pointerId)}catch(_){}
  tr.style.transition='none';
}
function move(e){
  if(!drag||e.pointerId!==drag.id)return;
  drag.dx=e.clientX-drag.x; drag.dy=e.clientY-drag.y;
  if(!drag.mode){
    if(Math.abs(drag.dx)<7&&Math.abs(drag.dy)<7)return;
    drag.mode=Math.abs(drag.dx)>=Math.abs(drag.dy)?'h':'v';
  }
  const now=performance.now(), dt=now-drag.lt;
  if(dt>0)drag.v=.8*drag.v+.2*((e.clientX-drag.lx)/dt);
  drag.lx=e.clientX; drag.lt=now;
  if(items.length<2&&drag.mode==='h'){tr.style.transform=X(drag.dx*.25);return}
  if(drag.mode==='h'){ tr.style.transform=X(drag.dx); }
  else{ const p=Math.min(1,Math.abs(drag.dy)/320); tr.style.transform=`translate3d(${-w}px,${drag.dy}px,0) scale(${1-p*.12})`; root.style.opacity=String(1-p*.7); }
}
function up(e){
  if(!drag||(e&&e.pointerId!==undefined&&e.pointerId!==drag.id))return;
  const d=drag; drag=null; root.style.opacity='';
  try{st.releasePointerCapture(d.id)}catch(_){}
  if(d.mode==='h'){
    const th=Math.min(110,w*.16);
    if(items.length>1&&(Math.abs(d.dx)>th||(Math.abs(d.v)>.4&&Math.abs(d.dx)>24))){go(d.dx<0?1:-1)} else rest(true);
  }else if(d.mode==='v'){
    if(Math.abs(d.dy)>110){close();return}
    tr.style.transition=reduce?'none':'transform .4s cubic-bezier(.16,1,.3,1)'; tr.style.transform=X(0);
  }else if(e&&e.type==='pointerup'){
    // тап мимо самой фотографии закрывает галерею
    const im=slides[1].querySelector('img'), r=im.getBoundingClientRect();
    const inside=e.clientX>=r.left&&e.clientX<=r.right&&e.clientY>=r.top&&e.clientY<=r.bottom;
    if(!inside)close();
  }
}
function key(e){
  if(!isOpen)return;
  if(e.key==='Escape'){close()}
  else if(e.key==='ArrowRight'){go(1)}
  else if(e.key==='ArrowLeft'){go(-1)}
  else if(e.key==='Home'){cur=0;paint()}
  else if(e.key==='End'){cur=items.length-1;paint()}
  else if(e.key==='Tab'){
    const f=[btnX,...(items.length>1?[btnP,btnN]:[])];
    const i=f.indexOf(document.activeElement);
    e.preventDefault(); f[(i+(e.shiftKey?-1:1)+f.length)%f.length].focus();
  }
}
function open(list,index,from){
  if(!list||!list.length)return;
  if(!root)build();
  items=list; cur=Math.max(0,Math.min(index||0,items.length-1)); opener=from||document.activeElement;
  root.hidden=false; isOpen=true; busy=false;
  document.documentElement.classList.add('plb-open');
  if(window.__lenis)window.__lenis.stop();
  measure(); slides.forEach(s=>{s.dataset.k='';}); paint(); rest(false);
  requestAnimationFrame(()=>{measure();rest(false);root.classList.add('open')});
  try{history.pushState({plb:1},'')}catch(_){}
  btnX.focus({preventScroll:true});
  if(!hinted&&items.length>1&&matchMedia('(hover:none)').matches){hinted=true;root.classList.add('hint');setTimeout(()=>root.classList.remove('hint'),2600)}
}
function close(fromPop){
  if(!isOpen)return; isOpen=false;
  root.classList.remove('open'); document.documentElement.classList.remove('plb-open');
  if(window.__lenis)window.__lenis.start();
  setTimeout(()=>{if(!isOpen)root.hidden=true},420);
  if(!fromPop&&history.state&&history.state.plb){try{history.back()}catch(_){}}
  if(opener&&opener.focus)try{opener.focus({preventScroll:true})}catch(_){}
}
window.PLB={open,close};
})();
