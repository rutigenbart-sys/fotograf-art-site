#!/usr/bin/env python3
"""Одноразовый (идемпотентный) патч существующих страниц под чёрную тему,
новую галерею и ссылку «Районы». Запускать из корня репозитория."""
import re, glob, io

SCRIPTS = ('<script src="js/lenis.min.js"></script>\n<script src="js/lightbox.js"></script>\n<script src="js/fx.js"></script>\n')
LB_RE = re.compile(r'<div class="lb" id="lb".*?<div class="lb-cap">.*?</div>\s*</div>\n?', re.S)

for p in sorted(glob.glob('*.html')):
    if p.startswith('yandex_'): continue
    s = open(p, encoding='utf-8').read(); o = s
    # стили
    if 'css/black.css' not in s:
        s = s.replace('<link rel="stylesheet" href="css/style.css">',
                      '<link rel="stylesheet" href="css/style.css">\n<link rel="stylesheet" href="css/black.css">')
    s = s.replace('<meta name="theme-color" content="#141211">', '<meta name="theme-color" content="#000000">')
    # старая галерея → новая
    s = LB_RE.sub('', s)
    if 'js/fx.js' not in s:
        if '<script src="js/site.js"></script>' in s:
            s = s.replace('<script src="js/site.js"></script>', '<script src="js/lenis.min.js"></script>\n<script src="js/site.js"></script>\n<script src="js/lightbox.js"></script>\n<script src="js/fx.js"></script>')
        elif p == 'index.html':
            s = s.replace('<script>\nconst G=', SCRIPTS + '<script>\nconst G=', 1)
    # ссылка «Районы» в меню
    if 'href="/moskva/"' not in s:
        s = s.replace('<a href="uslugi.html">Услуги</a>', '<a href="uslugi.html">Услуги</a>\n      <a href="/moskva/">Районы</a>', 1) if False else s
        s = re.sub(r'(<a href="uslugi\.html">Услуги</a>)', r'\1<a href="/moskva/">Районы</a>', s)
    if s != o:
        open(p, 'w', encoding='utf-8').write(s); print('patched', p)

# index.html: встроенный lightbox → PLB
p = 'index.html'
s = open(p, encoding='utf-8').read()
a = s.find('/* ---- lightbox ---- */'); b = s.find('/* ---- calculator ---- */')
if a != -1 and b != -1:
    new = """/* ---- lightbox (js/lightbox.js) ---- */
grid.addEventListener('click',e=>{const b=e.target.closest('.gi'); if(!b||!window.PLB)return;
  const arr=list.map(j=>({full:`img/${G[j].src}.jpg`,thumb:`img/${G[j].src}-s.jpg`,alt:G[j].alt,exif:G[j].exif||''}));
  PLB.open(arr,list.indexOf(+b.dataset.i),b);});

"""
    s = s[:a] + new + s[b:]
    open(p, 'w', encoding='utf-8').write(s); print('index lightbox replaced')
