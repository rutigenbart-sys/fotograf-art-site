#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор страниц фотографа: районы Москвы, ЗАГСы, Подмосковье, хабы, блок на главной, sitemap.

Запуск из корня репозитория:  python3 tools/build.py
Фото-обложки подхватываются автоматически, если лежат в:
  img/moskva/<slug>.jpg   img/zags/<key>.jpg   img/podmoskove/<slug>.jpg
(16:9, лучше 1600x900, JPG до ~300 КБ). Нет файла — страница выходит без обложки.
"""
import os, re, sys, json, html, hashlib
sys.path.insert(0, os.path.dirname(__file__))
from data import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = "2026-11-04"
DEFAULT_OG = SITE + "/img/og-cover.jpg"

# ------------------------------------------------------------------ утилиты
TR = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
              ["a","b","v","g","d","e","e","zh","z","i","j","k","l","m","n","o","p","r","s","t","u","f","h","c","ch","sh","sch","","y","","e","yu","ya"]))
def slug(s):
    s = s.lower().replace("«","").replace("»","")
    out = "".join(TR.get(c, c) for c in s)
    return re.sub(r"[^a-z0-9]+", "-", out).strip("-")

def pick(seed, opts):
    return opts[int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(opts)]

def plural(n, forms):
    n10, n100 = n % 10, n % 100
    if n10 == 1 and n100 != 11: return forms[0]
    if 2 <= n10 <= 4 and not 12 <= n100 <= 14: return forms[1]
    return forms[2]

esc = html.escape
def attr(s): return esc(s, quote=True)
def P(t): return f'<p class="rv">{t}</p>'
def exists(rel): return os.path.exists(os.path.join(ROOT, rel))
NB_RE = re.compile(r"(\d) (\d{3}) ₽")
def nb(t): return NB_RE.sub("\\1\u00a0\\2\u00a0₽", t)   # цены не переносятся строкой
def write(rel, content):
    content = nb(content)
    path = os.path.join(ROOT, rel); os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: f.write(content)

# ------------------------------------------------------------------ данные -> модели
districts = []   # dict
seen = set()
for okr, rows in D.items():
    for (name, env, zk, places) in rows:
        sl = slug(name); assert sl not in seen, sl; seen.add(sl)
        districts.append(dict(name=name, slug=sl, okr=okr, env=env, zags=zk, places=places, kind="район", url=f"/moskva/{sl}.html", dir="moskva"))
for (name, kind, env, places) in NAO:
    sl = slug(name); assert sl not in seen, sl; seen.add(sl)
    districts.append(dict(name=name, slug=sl, okr="НАО", env=env, zags=[], places=places, kind=kind, url=f"/moskva/{sl}.html", dir="moskva"))
MSK_REAL = [d for d in districts if d["okr"] != "НАО"]
assert len(MSK_REAL) == 125, len(MSK_REAL)
for k in ZAGS: pass
for d in districts:
    for z in d["zags"]: assert z in ZAGS, (d["name"], z)

cities = []
for (name, env, addr, places) in PODM:
    sl = slug(name)
    cities.append(dict(name=name, slug=sl, env=env, addr=addr, places=places, url=f"/podmoskove/{sl}.html"))

by_okr = {}
for d in districts: by_okr.setdefault(d["okr"], []).append(d)

def zinfo(k):
    nom, loc, gen, ins, addr, okr, kind = ZAGS[k]
    return dict(key=k, nom=nom, loc=loc, gen=gen, ins=ins, addr=addr, okr=okr, kind=kind, url=f"/zags/{k}.html")


# ------------------------------------------------------------------ обложки из портфолио
import zlib
_W="img/svadebnyj-fotograf-moskva-"
def _load_portfolio():
    g = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    out = {}
    for src, alt in re.findall(r'"src": "(svadebnyj-fotograf-moskva-[^"]+)", "cat": "[^"]*", "alt": "((?:[^"\\]|\\.)*)"', g):
        out[src[len("svadebnyj-fotograf-moskva-"):]] = json.loads('"%s"' % alt).split(". ")[0].rstrip(".")
    return out
PORTFOLIO = _load_portfolio()   # все свадебные фото из галереи: имя -> краткое описание
COVER_POOL = {"gen": [k for k in PORTFOLIO if not k.startswith("fotograf-v-zags")],
              "zags": [k for k in PORTFOLIO if k.startswith("fotograf-v-zags")]}
_POOLMAP = {"msk": "gen", "podm": "gen", "palace": "zags", "zags": "zags"}
_used = {}
def portfolio_cover(pool, key):
    """Фото идут по кругу: пока не использованы все, повторов нет; соседние страницы получают разные кадры."""
    pool = _POOLMAP[pool]; lst = COVER_POOL[pool]
    i = _used.get(pool, zlib.crc32(pool.encode()) % len(lst)); _used[pool] = (i + 1) % len(lst)
    return lst[i]
_dims = {}
def _dim(cover):
    if cover not in _dims:
        from PIL import Image
        _dims[cover] = Image.open(os.path.join(ROOT, cover)).size
    return _dims[cover]
def cover_img(cover, alt, eager=True):
    """<img> для обложки; фото портфолио отдаём с srcset (760w и 2000w)."""
    ld = 'loading="eager"' if eager else 'loading="lazy"'
    if cover.startswith("img/svadebnyj-fotograf-moskva-"):
        b = "/" + cover[:-4]
        return f'<img src="{b}-s.jpg" srcset="{b}-s.jpg 760w, {b}.jpg 2000w" sizes="(min-width:1200px) 1200px, 100vw" alt="{attr(alt)}" width="{_dim(cover)[0]}" height="{_dim(cover)[1]}" {ld} decoding="async">'
    return f'<img src="/{cover}" alt="{attr(alt)}" width="1600" height="900" {ld} decoding="async">'
def long_alt(photo_key, where, kind_note):
    """Развёрнутое описание: что на фото + к какой теме страницы относится. Без утверждений, что снято именно в этом месте."""
    return (f"{PORTFOLIO[photo_key]}. Пример работы свадебного фотографа Дмитрия (Фотограф.art), Москва. "
            f"Иллюстрация к статье: {where}. {kind_note}")

# ------------------------------------------------------------------ тексты
ENV = {
 "center": [
  "Район {n} — это старая Москва: небольшие улицы, бульвары, дворы и фасады разных эпох. Декорации здесь не нужны: достаточно найти правильный угол и свет. Рано утром и ближе к закату центр почти безлюден, и пару можно снимать без случайных прохожих.",
  "Центр — это архитектура, тихие переулки и бульвары, где легко построить романтическую прогулку пешком. Если вы расписываетесь рядом с районом {n}, мы снимаем в двух-трёх точках и не тратим время на переезды: больше кадров за те же часы."],
 "park": [
  "В районе {n} много зелени, и это главный союзник свадебного фотографа: листва мягко рассеивает свет, а аллеи и поляны дают чистый фон. Прогулку после росписи можно устроить без долгих переездов и спокойно выбрать красивые места.",
  "Зелёные зоны района {n} хороши в любое время года: весной цветение, летом глубокая тень, осенью золото, зимой снег и иней. Подберу точку под ваш сезон и стиль, чтобы кадры не походили на чужие."],
 "river": [
  "У воды свет живее: отражения, простор и закат дают кадры, которые не получить во дворе. В районе {n} прогулку можно построить вдоль набережной или поймы, а к вечеру поймать золотой час.",
  "Набережные и поймы около района {n} дают пространство для кадров с движением: пара идёт вдоль воды, фата и платье работают на ветру. В холодное время получаются графичные зимние истории."],
 "estate": [
  "Рядом с районом {n} есть исторические ансамбли, усадьбы и храмы: архитектура, колонны и ухоженные аллеи выглядят дорого без лишнего декора. Часть площадок работает по своим правилам съёмки, поэтому условия лучше уточнить заранее, и я подскажу, с чего начать.",
  "Исторические места района {n} подходят и для свадебной прогулки, и для венчания или крещения. Важно заранее проверить график и правила: для храмов и музеев-заповедников они свои."],
 "sleeper": [
  "Район {n} — типичная жилая Москва: дворы, высотки, парки и закатное небо над крышами. Здесь важно не угадывать, а подбирать: я заранее смотрю карту и свет, чтобы выбрать места, где кадр получается живым и чистым, без случайных машин и мусорных баков.",
  "В жилом районе вроде {n} лучшие кадры часто рядом: парк в десяти минутах, пруд, смотровая площадка или современный двор с интересной архитектурой. Заранее проверяю маршрут, чтобы прогулка после ЗАГС не превратилась в поиск парковки."],
 "industrial": [
  "Район {n} интересен фактурой: кирпичные стены, промышленная архитектура, вода и большое небо. Для пары, которая не хочет «как у всех», это сильный городской сюжет в духе loft и документальной съёмки.",
  "Индустриальная среда даёт контраст: нежное платье и грубые фактуры, мягкий закат и металл. В районе {n} получается стильная репортажная история без банальных парковых кадров."],
 "newm": [
  "В районе {n} много новой архитектуры, просторных дворов и свободных участков зелени. Здесь мало людей, и пару можно снимать спокойно, без суеты, а чистые линии современных зданий дают аккуратный минималистичный фон.",
  "Новая застройка и близкая природа делают район {n} удобным для свадебной съёмки: рядом можно найти и современный фон, и парк или водоём. Маршрут продумываем заранее, чтобы не терять время на дорогу."],
 "city": [
  "Рядом с районом {n} есть место, где свадебные кадры выглядят как кино: стекло, высотки и отражения. Лучше всего это работает вечером, когда включается подсветка, и утром, когда пусто."],
 "temple": [
  "Храмы и монастыри рядом с районом {n} подходят для венчания и крещения: тёплый золотой свет, фрески и тишина. Правила съёмки внутри устанавливает настоятель, поэтому договариваемся заранее."],
}

LEAD = {
 "center": "Исторические дворы, бульвары и архитектура дают фон, который не нужно придумывать.",
 "park": "Зелёные аллеи и мягкий свет рядом с ЗАГСом: роспись и прогулка без долгих переездов.",
 "river": "Вода, простор и закат: роспись в ЗАГСе и прогулка на набережной в одном ритме.",
 "estate": "Усадьбы, храмы и исторические ансамбли рядом с ЗАГСом дают красивые кадры без декораций.",
 "sleeper": "Подбираю места для кадров заранее: парки, набережные и дворы, где получается живо и чисто.",
 "industrial": "Фактурные кирпичные стены, вода и большое небо: нестандартный городской сюжет.",
 "newm": "Современная архитектура и просторные парки: свадьба без толпы и лишней суеты.",
 "city": "Стекло, высотки и отражения: динамичный современный сюжет.",
}

WALK = {
 "center": "Пешая прогулка по бульварам и переулкам рядом с ЗАГСом: две-три точки без переездов.",
 "park": "Прогулка по парку или у воды: выбираем места с лучшим светом и без толпы.",
 "river": "Прогулка на набережной или пойме, ловим золотой час, если банкет вечером.",
 "estate": "Прогулка у усадьбы или храма (правила съёмки уточняем заранее), затем романтические кадры в аллеях.",
 "sleeper": "Прогулка в ближайшем парке, на набережной или в красивом дворе: маршрут продумываем заранее.",
 "industrial": "Городская прогулка: кирпичные фактуры, набережная и открытое небо.",
 "newm": "Прогулка по современной архитектуре и ближайшим зелёным зонам.",
 "city": "Вечерняя или утренняя прогулка среди стекла и высоток.",
}

STEPS_BASE = [
 ("Сборы", "Начинаю со сборов жениха и невесты: образ, платье, детали, кольца и письма. Хорошие кадры получаются, когда никто не торопится, поэтому на сборы стоит заложить около часа."),
 ("Приезд к ЗАГСу", "Приезжаю заранее, смотрю свет и вход, обсуждаю с персоналом, где лучше встать для семейных фото. Так церемония проходит спокойно, без суеты."),
 ("Роспись", "Снимаю церемонию с лучших точек зала: клятвы, кольца, первый поцелуй и реакции гостей. Эмоции здесь честнее любой постановки, и я стараюсь не мешать, а наблюдать."),
 ("Поздравления и семейные фото", "Пока гости не разошлись, делаем групповые кадры: родители, друзья, свидетели. Держу тайминг, чтобы не терять время и не утомлять пару."),
 ("Прогулка", None),
 ("Банкет", "Приезжаю к началу банкета: выход пары, первые тосты, танцы и детали сервировки. Остаюсь по договорённости, оплата считается по часам."),
]

PRICE_ROWS = [
 ("Роспись в ЗАГСе", "5 000 ₽"),
 ("Первый час съёмки", "5 000 ₽"),
 ("Каждый следующий час", "3 000 ₽"),
 ("3 часа: ЗАГС и прогулка", "11 000 ₽"),
 ("6 часов: сборы, ЗАГС, прогулка, начало банкета", "20 000 ₽"),
 ("10 часов: весь свадебный день", "32 000 ₽"),
]

def rows_html():
    return '<div class="dz-rows rv">' + "".join(f"<div><span>{a}</span><b>{b}</b></div>" for a, b in PRICE_ROWS) + "</div>"

def steps_html(env):
    out = []
    for i, (t, x) in enumerate(STEPS_BASE):
        if x is None: x = WALK[env[0]]
        out.append(f'<div class="dz-step"><b>{t}</b><span>{x}</span></div>')
    return '<div class="dz-steps">' + "".join(out) + "</div>"

SERVICE_LINKS = [
 ("/svadebnyj-fotograf.html", "Свадебный фотограф"),
 ("/fotograf-na-kreshhenie.html", "Крещение"),
 ("/detskij-fotograf.html", "Детские праздники"),
 ("/fotograf-na-vypusknoj.html", "Выпускной"),
 ("/fotograf-na-vystavku.html", "Выставки и мероприятия"),
 ("/uslugi.html", "Все услуги"),
]
def service_chips():
    return '<div class="dz-links">' + "".join(f'<a class="chip" href="{u}">{t}</a>' for u, t in SERVICE_LINKS) + "</div>"

def place_cards(places):
    if not places: return ""
    out = "".join(f'<div class="dz-pl"><b>{n}</b><span>{PLACE_KIND[k]}</span></div>' for n, k in places)
    return f'<div class="dz-pls">{out}</div>'

def zags_cards(keys):
    out = []
    for k in keys:
        z = zinfo(k)
        out.append(f'<a class="dz-zc" href="{z["url"]}"><small>{z["okr"]}</small><b>{z["nom"]}</b><span>Москва, {z["addr"]}</span></a>')
    return '<div class="dz-zcs">' + "".join(out) + "</div>"

def zlist_text(keys):
    return "; ".join(f'{zinfo(k)["nom"]} ({zinfo(k)["addr"]})' for k in keys)

# ------------------------------------------------------------------ оболочка страницы
_src = open(os.path.join(ROOT, "svadebnyj-fotograf.html"), encoding="utf-8").read()
SPRITE = re.search(r'<svg width="0" height="0".*?</svg>', _src, re.S).group(0)  # иконки берём из рабочей страницы

MAX_URL = "https://max.ru/u/f9LHodD0cOI7ZeKXz67Z6f0I3CiNXraTTkri54r-b8vGDxQoJ5eY6ctCnNg"

HEADER = f"""<header class="hdr" id="hdr">
  <div class="wrap hdr-in">
    <a class="logo" href="/" aria-label="Фотограф Дмитрий, на главную">
      <svg viewBox="-50 -50 100 100" aria-hidden="true"><use href="#ap"/></svg>
      <span class="logo-t"><b>DMITRY</b><small>Photographer</small></span>
    </a>
    <nav class="nav" aria-label="Разделы">
      <a href="/svadebnyj-fotograf.html">Свадьбы</a>
      <a href="/uslugi.html">Услуги</a>
      <a href="/moskva/">Районы</a>
      <a href="/zags/">ЗАГСы</a>
      <a href="/#prices">Цены</a>
      <a href="#contact">Контакты</a>
    </nav>
    <a class="hdr-tel" href="tel:{TEL}">{PHONE}</a>
    <button class="burger" id="burger" aria-label="Меню" aria-expanded="false"><i></i></button>
  </div>
</header>
<div class="mnav" id="mnav">
  <a href="/svadebnyj-fotograf.html">Свадьбы</a>
  <a href="/uslugi.html">Услуги</a>
  <a href="/moskva/">Районы</a>
  <a href="/zags/">ЗАГСы</a>
  <a href="#contact">Контакты</a>
  <div class="mnav-c">
    <a href="tel:{TEL}">{PHONE}</a>
    <span>WhatsApp, Telegram @i_s_moscow, <a href="{MAX_URL}" target="_blank" rel="noopener" style="font-size:14px">Max</a></span>
  </div>
</div>"""

FOOTER = f"""<footer class="ftr">
  <div class="wrap ftr-in">
    <a class="logo" href="/"><svg viewBox="-50 -50 100 100" aria-hidden="true"><use href="#ap"/></svg><span class="logo-t"><b>DMITRY</b><small>Photographer</small></span></a>
    <nav aria-label="Ссылки"><a href="tel:{TEL}">{PHONE}</a><a href="https://t.me/i_s_moscow" target="_blank" rel="noopener">Telegram</a><a href="{MAX_URL}" target="_blank" rel="noopener">Max</a><a href="/privacy.html">Политика конфиденциальности</a></nav>
    <span>© <span id="yr">2026</span> Фотограф Дмитрий, Москва</span>
    <nav class="ftr-svc" aria-label="Услуги фотографа"><a href="/svadebnyj-fotograf.html">Свадебный фотограф</a><a href="/fotograf-na-kreshhenie.html">Крещение</a><a href="/fotograf-na-vypusknoj.html">Выпускной</a><a href="/fotograf-na-vystavku.html">Выставки и мероприятия</a><a href="/uslugi.html">Все услуги</a><a href="/moskva/">Районы Москвы</a><a href="/zags/">ЗАГСы Москвы</a><a href="/podmoskove/">Подмосковье</a></nav>
  </div>
</footer>
<nav class="fab" id="fab" aria-label="Быстрая связь">
  <a href="tel:{TEL}"><svg><use href="#i-phone"/></svg>Звонок</a>
  <a class="wa" href="https://wa.me/79268542333" target="_blank" rel="noopener"><svg><use href="#i-wa"/></svg>WhatsApp</a>
  <a href="https://t.me/i_s_moscow" target="_blank" rel="noopener"><svg><use href="#i-tg"/></svg>Telegram</a>
  <a class="mx" href="{MAX_URL}" target="_blank" rel="noopener"><svg><use href="#i-max"/></svg>Max</a>
</nav>"""

def contact_block(h="Давайте обсудим <em>вашу</em> съёмку"):
    return f"""<section class="sec contact sp-contact" id="contact">
  <div class="wrap ct">
    <div class="ct-l rv">
      <div class="eyebrow">Контакты</div>
      <h2>{h}</h2>
      <p class="lead" style="color:var(--on-night-2)">Напишите дату, место и время. Я сразу отвечу, свободен ли, и назову стоимость.</p>
      <a class="big-tel" href="tel:{TEL}">{PHONE}</a>
    </div>
    <div class="ct-l rv">
      <div class="ct-btns">
        <a class="btn btn-light" href="tel:{TEL}"><svg><use href="#i-phone"/></svg>Позвонить</a>
        <a class="btn btn-ghost" href="https://wa.me/79268542333" target="_blank" rel="noopener"><svg><use href="#i-wa"/></svg>WhatsApp</a>
        <a class="btn btn-ghost" href="https://t.me/i_s_moscow" target="_blank" rel="noopener"><svg><use href="#i-tg"/></svg>Telegram</a>
        <a class="btn btn-ghost" href="{MAX_URL}" target="_blank" rel="noopener"><svg><use href="#i-max"/></svg>Max</a>
      </div>
    </div>
  </div>
</section>"""

def faq_html(qas):
    items = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in qas)
    return f'<div class="faq rv">{items}</div>'

def strip_tags(s): return re.sub(r"<[^>]+>", "", s)

def page(path, title, desc, h1, lead, crumbs, body, tags=(), cover=None, cover_alt="", faq=None, area=None, geo="RU-MOW", place="Москва", extra_schema=None, aside=None, toc=None):
    url = SITE + path
    og = SITE + "/" + cover if (cover and not cover.startswith("img/svadebnyj-fotograf-moskva-")) else DEFAULT_OG
    bc_items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (u, n) in enumerate(crumbs)]
    graph = [
        {"@type": "WebPage", "@id": url + "#page", "url": url, "name": title, "description": desc, "inLanguage": "ru-RU", "dateModified": TODAY, "isPartOf": {"@id": SITE + "/#site"}, "about": {"@id": SITE + "/#business"}},
        {"@type": "BreadcrumbList", "itemListElement": bc_items},
    ]
    if area:
        graph.append({"@type": "Service", "name": h1, "serviceType": "Свадебная фотосъёмка, фотосъёмка в ЗАГСе", "provider": {"@id": SITE + "/#business"}, "areaServed": area,
                      "offers": {"@type": "Offer", "price": "5000", "priceCurrency": "RUB", "description": "Первый час съёмки 5 000 ₽, каждый следующий час 3 000 ₽. Роспись в ЗАГСе 5 000 ₽."}})
    if faq:
        graph.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": strip_tags(q), "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in faq]})
    if extra_schema: graph += extra_schema
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    crumb_html = "".join(f'<li><a href="{u}">{n}</a></li>' for u, n in crumbs[:-1]) + f"<li>{crumbs[-1][1]}</li>"
    tags_html = "".join(f"<span>{t}</span>" for t in tags)
    cover_html = ""
    if cover:
        _cap = "Пример работы из портфолио" if cover.startswith("img/svadebnyj-fotograf-moskva-") else cover_alt.split(". ")[0]
        _w, _h = _dim(cover); _port = _h > _w
        _fig = f'class="dz-cover is-p" style="--bg:url(/{cover[:-4]}-s.jpg)"' if _port else 'class="dz-cover"'
        cover_html = f'<div class="wrap" style="padding-top:8px"><figure {_fig}>{cover_img(cover, cover_alt)}<figcaption>{esc(_cap)}</figcaption></figure></div>'
    toc_html = ""
    if toc:
        toc_html = '<nav class="dz-toc" aria-label="Содержание"><b>Содержание</b><ol>' + "".join(f'<li><a href="#{a}">{t}</a></li>' for a, t in toc) + "</ol></nav>"
    aside_html = aside or ""
    return f"""<!doctype html>
<html lang="ru" prefix="og: https://ogp.me/ns#">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{attr(desc)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{url}">
<meta name="geo.region" content="{geo}">
<meta name="geo.placename" content="{attr(place)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="ru_RU">
<meta property="og:site_name" content="Фотограф.art">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{attr(title)}">
<meta property="og:description" content="{attr(desc)}">
<meta property="og:image" content="{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#000000">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,300;1,400;1,500&family=Forum&family=Montserrat:wght@300;400;500;600&display=swap">
<link rel="stylesheet" href="/css/style.css">
<link rel="stylesheet" href="/css/black.css">
<script type="application/ld+json">{ld}</script>
<script>document.documentElement.classList.add('js')</script>
<script src="/js/analytics.js"></script>
</head>
<body>
<noscript><div><img src="https://mc.yandex.ru/watch/114134641" style="position:absolute;left:-9999px" alt=""></div></noscript>
{SPRITE}
{HEADER}
<main id="top">
<section class="dz-intro" id="hero">
  <div class="wrap">
    <ol class="crumbs">{crumb_html}</ol>
    <h1 class="sp-h1">{h1}</h1>
    <p class="sp-lead">{lead}</p>
    <div class="dz-tags">{tags_html}</div>
    <div class="hero-cta">
      <a class="btn btn-light" href="#contact">Забронировать дату</a>
      <a class="btn btn-ghost" href="tel:{TEL}">{PHONE}</a>
    </div>
  </div>
</section>
{cover_html}
<section class="dz-sec">
  <div class="wrap dz-layout">
    <div class="dz-art">
{body}
    </div>
    <aside class="dz-aside">
      <div class="dz-cta"><small class="eyebrow">Стоимость</small><div class="sum">5 000 ₽<span>роспись в ЗАГСе</span></div><p>Первый час съёмки 5 000 ₽, каждый следующий 3 000 ₽. Без пакетов и скрытых доплат.</p><a class="btn btn-light" href="#contact">Узнать, свободна ли дата</a></div>
      {toc_html}
      {aside_html}
    </aside>
  </div>
</section>
{contact_block()}
</main>
{FOOTER}
<script src="/js/lenis.min.js"></script>
<script src="/js/site.js"></script>
<script src="/js/fx.js"></script>
</body>
</html>
"""

BUSINESS_AREA_MSK = [{"@type": "City", "name": "Москва"}, {"@type": "AdministrativeArea", "name": "Московская область"}]

def section(sid, title, inner):
    return f'<section id="{sid}"><h2>{title}</h2>\n{inner}\n</section>'

# ------------------------------------------------------------------ страницы районов
def kind_loc(d):  # «в районе X» / «в городе X» / «в поселении X»
    return {"район": "в районе", "город": "в городе", "поселение": "в поселении"}[d["kind"]]
def kind_acc(d):  # «в район X» / «в город X» / «в поселение X»
    return {"район": "в район", "город": "в город", "поселение": "в поселение"}[d["kind"]]
def kind_nom(d):
    return f'{d["kind"]} {d["name"]}'

def build_district(d, siblings):
    n = d["name"]; okr = d["okr"]; okr_full = OKRUGS[okr][0]
    kloc = kind_loc(d); knom = kind_nom(d)
    zs = [zinfo(k) for k in d["zags"]]
    z1 = zs[0] if zs else None
    env = d["env"]
    path = d["url"]
    title = f"Свадебный фотограф {kloc} {n} — ЗАГС, свадьба, банкет | Фотограф.art"
    if len(title) > 72: title = f"Фотограф {kloc} {n}: ЗАГС, свадьба, банкет | Фотограф.art"
    z_desc = f" Рядом: {z1['nom']}." if z1 else ""
    desc = f"Свадебный фотограф {kloc} {n} ({OKRUGS[okr][1]}).{z_desc} Роспись 5 000 ₽, первый час 5 000 ₽, далее 3 000 ₽/час. Живые кадры, быстрая обработка."
    if len(desc) > 165: desc = desc[:162].rsplit(" ", 1)[0] + "…"
    h1 = f"Свадебный фотограф {kloc} {n}"
    lead = f"Снимаю росписи в ЗАГСе, свадьбы, венчания и банкеты {kloc} {n}. " + LEAD[env[0]] + " Первый час 5 000 ₽, дальше 3 000 ₽ за час."
    tags = [f"<b>{OKRUGS[okr][1]}</b> · {okr}", "Первый час <b>5 000 ₽</b>", "ЗАГС <b>5 000 ₽</b>"]
    if z1: tags.append(f"ЗАГС рядом: <b>{z1['nom'].replace('ЗАГС ','')}</b>")

    # раздел 1
    p1 = P(f"Меня зовут Дмитрий, я снимаю свадьбы, росписи в ЗАГСе, венчания, банкеты и семейные события по всей Москве и Подмосковью. Приеду {kind_acc(d)} {n} и сниму ваш день целиком или только нужные часы: оплата считается по времени съёмки, без пакетов и скрытых доплат.")
    has_hist = any(k in ("estate", "temple") for _, k in d["places"])
    envs = [e for e in env if e != "estate" or has_hist] or ["sleeper"]
    env_txt = "".join(P(pick(n + e, ENV[e]).format(n=n)) for e in envs[:2])
    p3 = P("Мой подход простой: живые фотографии вместо поз. Я не командую «повернитесь и улыбнитесь», а наблюдаю и ловлю настоящие эмоции: смех родителей, дрожащие руки перед клятвой, взгляд жениха на невесту. Готовые кадры обрабатываю быстро и отдаю по ссылке.")
    s1 = section("kto", f"Свадебный фотограф {kloc} {n}: что и как я снимаю", p1 + env_txt + p3)

    # раздел 2: ЗАГС
    if zs:
        zi = P(f"В Москве заявление в ЗАГС, как правило, можно подать в любой отдел независимо от места жительства, поэтому район не ограничивает выбор. Для жителей района {n} и тех, кто хочет расписаться поблизости, удобны такие варианты:")
        zc = zags_cards(d["zags"])
        zt = f"""<h3>Как выбрать ЗАГС для свадьбы</h3>
<ul>
<li><b>Ориентируйтесь на маршрут дня.</b> Посмотрите, как ехать от ЗАГС к месту прогулки и банкету: меньше переездов, больше кадров.</li>
<li><b>Спросите про зал и свет.</b> Для фото важны окна, высота потолков и фон: при подаче заявления уточните, какой зал вам предложат.</li>
<li><b>Уточните число гостей и правила съёмки.</b> Они зависят от конкретного ЗАГС и могут меняться.</li>
<li><b>Планируйте заранее.</b> Заявление подают через Госуслуги, регистрация, как правило, проходит не раньше чем через месяц после подачи, а популярные даты занимают быстро.</li>
</ul>
<div class="dz-note rv">Адреса и правила могут меняться, поэтому перед визитом перепроверьте их на mos.ru или в Госуслугах.</div>"""
        s2 = section("zags", f"ЗАГС рядом с районом {n}: адреса и выбор", zi + zc + zt)
    else:
        zi = P(f"Точный ЗАГС для {knom} зависит от того, где вы живёте и какой зал выбираете: в Москве есть дворцы бракосочетания и районные отделы, и на роспись можно записаться в любой из них. Посмотрите <a href=\"/zags/\">справочник ЗАГСов Москвы с адресами</a> и выберите ближайший к вам или самый красивый.")
        zt = f"""<ul>
<li><b>Сравните маршруты.</b> От района {n} до центра или до районного отдела ехать по-разному, и это влияет на тайминг дня.</li>
<li><b>Заранее проверьте дату.</b> Заявление подают через Госуслуги, регистрация обычно проходит не раньше чем через месяц после подачи.</li>
<li><b>Если выбираете выездную регистрацию,</b> уточняйте условия на Госуслугах и у организаторов площадки.</li>
</ul>"""
        s2 = section("zags", f"ЗАГС для {knom}: как выбрать", zi + zt)

    # раздел 3: места
    if d["places"]:
        pl_intro = P(f"Вот места, которые я бы рассмотрел для прогулки и портретов {kloc} {n} и рядом с ним. Ниже кратко, чем каждое хорошо для кадра:")
        pl = place_cards(d["places"])
        pl_tail = P("Если у вас есть любимое место, например, где познакомились или сделали предложение, скажите: построим маршрут вокруг него.")
        s3 = section("mesta", f"Где снимать свадьбу {kloc} {n}", pl_intro + pl + pl_tail)
    else:
        s3 = section("mesta", f"Где снимать свадьбу {kloc} {n}", P(f"Конкретные места {kloc} {n} лучше подбирать под вашу дату, время и ЗАГС: свет меняется по сезону и по часам, а в выходные популярные точки заполняются. Перед съёмкой я смотрю карту и предлагаю два-три варианта, а вы выбираете то, что нравится."))

    # раздел 4: план дня
    s4 = section("plan", f"Свадебный день {kloc} {n}: пример плана съёмки",
        P("Ниже типичный день для пары, которая расписывается и идёт на банкет. План гибкий: я подстраиваюсь под ваш тайминг и убираю то, что вам не нужно.") + steps_html(env) +
        P("Если вы выбираете короткий формат, снимаю только роспись и прогулку: это от одного до трёх часов. Для полной свадьбы с банкетом чаще всего берут 6 или 10 часов."))

    # раздел 5: банкет
    s5 = section("banket", f"Банкет, юбилеи и семейные события {kloc} {n}",
        P(f"Кроме свадеб снимаю банкеты в ресторанах и банкетных залах, юбилеи, семейные праздники, крещения и детские дни рождения. Приезжаю заранее, смотрю свет и расстановку, согласую тайминг с организатором или ведущим. {kloc.capitalize()} {n} или по соседству есть много площадок, и я работаю на любых: от небольшого зала до загородного дома.") +
        P("Для банкета чаще всего достаточно трёх-четырёх часов: первые тосты, танцы и ключевые моменты вечера. Если хотите больше, продлим по 3 000 ₽ за каждый следующий час.") +
        service_chips())

    # раздел 6: цены
    s6 = section("ceny", f"Сколько стоит фотограф {kloc} {n}",
        P(f"Цены одинаковы для всех районов Москвы: платите только за время съёмки. Вот примеры:") + rows_html() +
        P("Это ориентиры, точную стоимость назову после вашего сообщения. Фотографии отбираю, обрабатываю и отдаю по ссылке."))

    # FAQ
    zq_ans = (f"Для района {n} удобны: " + zlist_text(d["zags"]) + ". Расписаться можно и в любом другом отделе Москвы: ориентируйтесь на маршрут дня и зал.") if zs else "В Москве можно выбрать любой отдел ЗАГС. Смотрите справочник на странице ЗАГСов и ориентируйтесь на удобство маршрута и интерьер зала."
    walk_ans = (f"Хорошие варианты: " + ", ".join(p[0] for p in d["places"][:3]) + ". Точный маршрут подберу под ваш ЗАГС, сезон и время.") if d["places"] else f"Подберу парк, набережную или двор рядом с вашим ЗАГС: заранее смотрю карту и свет, чтобы кадры получились чистыми."
    faq = [
        (f"Сколько стоит свадебный фотограф {kloc} {n}?", "Роспись в ЗАГСе стоит 5 000 ₽. При съёмке по часам первый час 5 000 ₽, каждый следующий 3 000 ₽: например, ЗАГС и прогулка на 3 часа обойдутся в 11 000 ₽, а день на 6 часов в 20 000 ₽. Без пакетов и скрытых доплат."),
        (f"В какой ЗАГС идти из района {n}?" if d["kind"] == "район" else f"В какой ЗАГС идти из {d['kind']}а {n}?" if d["kind"] == "город" else f"В какой ЗАГС идти из поселения {n}?", zq_ans),
        (f"Где сделать прогулку после ЗАГС {kloc} {n}?", walk_ans),
        ("Можно ли расписаться в ЗАГСе не по месту регистрации?", "Как правило, да: в Москве заявление можно подать в любой отдел независимо от места жительства. Перед выбором уточните актуальные правила и свободные даты на Госуслугах или mos.ru."),
        ("Как быстро я получу фотографии?", "Обрабатываю быстро и отдаю готовые кадры по ссылке. Точный срок называю при бронировании, он зависит от объёма съёмки."),
        (f"Вы выезжаете {kloc} {n}?", f"Да, снимаю по всей Москве и Подмосковью, {knom} ({okr_full}) не исключение. Напишите дату, ЗАГС и время, и я сразу отвечу, свободен ли."),
    ]
    s7 = section("faq", "Частые вопросы", '<div class="dz-faq">' + faq_html(faq) + "</div>")

    # соседние
    sib = [x for x in siblings if x["slug"] != d["slug"]]
    sib_html = '<div class="dz-links">' + "".join(f'<a class="chip" href="{x["url"]}">{x["name"]}</a>' for x in sib[:14]) + "</div>"
    other = ""
    if sib:
        other = section("sosedi", f"Другие районы: {OKRUGS[okr][1]}", sib_html + P('<a href="/moskva/">Все районы Москвы</a> · <a href="/zags/">Все ЗАГСы Москвы</a> · <a href="/podmoskove/">Подмосковье</a>'))
    body = "\n".join([s1, s2, s3, s4, s5, s6, s7, other])
    toc = [("kto", "Что и как снимаю"), ("zags", "ЗАГС и выбор"), ("mesta", "Где снимать"), ("plan", "План дня"), ("banket", "Банкет и события"), ("ceny", "Цены"), ("faq", "Вопросы")]
    cover = f"img/moskva/{d['slug']}.jpg"
    if exists(cover): cover_alt = f"Район {n}: атмосфера для свадебной прогулки"
    else:
        pk = portfolio_cover("msk", d["slug"]); cover = _W + pk + ".jpg"
        cover_alt = long_alt(pk, f"свадебная фотосъёмка, ЗАГС, прогулка и банкет — район {n}, Москва", "Фотограф приезжает на роспись, венчание, прогулку и банкет в любой район Москвы и Подмосковья, съёмка от 5 000 ₽.")
    area = [{"@type": "Place", "name": f"{n}, Москва"}] + BUSINESS_AREA_MSK
    crumbs = [("/", "Главная"), ("/moskva/", "Районы Москвы"), (path, n)]
    return page(path, title, desc, h1, lead, crumbs, body, tags=tags, cover=cover, cover_alt=cover_alt, faq=faq, area=area, place=f"{n}, Москва", toc=toc)

# ------------------------------------------------------------------ Подмосковье
def build_city(c, others):
    n = c["name"]; env = c["env"]; path = c["url"]
    title = f"Свадебный фотограф в городе {n} — ЗАГС, свадьба, банкет | Фотограф.art"
    z_txt = f" ЗАГС: {c['addr']}." if c["addr"] else ""
    desc = f"Свадебный фотограф в городе {n} (Подмосковье): роспись в ЗАГСе, свадьба, венчание, банкет.{z_txt} Первый час 5 000 ₽, далее 3 000 ₽/час."
    if len(desc) > 165: desc = desc[:162].rsplit(" ", 1)[0] + "…"
    h1 = f"Свадебный фотограф в городе {n}"
    lead = f"Выезжаю на росписи в ЗАГСе, свадьбы, венчания и банкеты в городе {n} и по Подмосковью. " + LEAD[env[0]] + " Первый час 5 000 ₽, дальше 3 000 ₽ за час."
    tags = ["<b>Подмосковье</b>", "Первый час <b>5 000 ₽</b>", "ЗАГС <b>5 000 ₽</b>"]
    p1 = P(f"Меня зовут Дмитрий, я снимаю свадьбы и семейные события по Москве и Подмосковью. В городе {n} сниму ваш день целиком или только нужные часы. Платите за время съёмки, без пакетов и скрытых доплат.")
    env_txt = "".join(P(pick(n + e, ENV[e]).format(n=n)) for e in env[:2])
    s1 = section("kto", f"Свадебный фотограф в городе {n}: как проходит съёмка", p1 + env_txt + P("Мой подход: живые фотографии вместо поз. Наблюдаю, ловлю эмоции и быстро отдаю готовые кадры по ссылке."))
    if c["addr"]:
        zc = f'<div class="dz-zcs"><div class="dz-zc"><small>Подмосковье</small><b>Отдел ЗАГС города {n}</b><span>{c["addr"]}</span></div></div>'
        z_body = P(f"Для регистрации брака в городе {n} обычно обращаются в местный отдел ЗАГС. По открытым справочникам он находится по адресу: {c['addr']}. Адрес и режим работы стоит перепроверить на сайте Главного управления ЗАГС Московской области или в Госуслугах.") + zc
    else:
        z_body = P(f"Адрес отдела ЗАГС города {n}, график и условия записи лучше смотреть на сайте Главного управления ЗАГС Московской области или в Госуслугах. Подать заявление можно и в Москве: выбирайте то, что удобнее для вас и гостей.")
    z_body += """<ul>
<li><b>Запишитесь заранее.</b> Заявление подают через Госуслуги, регистрация, как правило, проходит не раньше чем через месяц после подачи.</li>
<li><b>Продумайте дорогу.</b> Если банкет в другом городе, закладывайте время на переезд.</li>
<li><b>Выездная регистрация.</b> В Подмосковье многие площадки предлагают её: условия уточняйте у организаторов.</li>
</ul>"""
    s2 = section("zags", f"ЗАГС в городе {n}: адрес и запись", z_body)
    if c["places"]:
        s3 = section("mesta", f"Где снимать свадьбу в городе {n}", P(f"Вот места, которые я бы рассмотрел для прогулки и портретов в городе {n} и рядом:") + place_cards(c["places"]) + P("Правила съёмки на территории музеев, монастырей и усадеб могут отличаться: для храмов, музеев-заповедников и частных территорий лучше согласовать съёмку заранее."))
    else:
        s3 = section("mesta", f"Где снимать свадьбу в городе {n}", P(f"Места для съёмки в городе {n} подбираю под вашу дату и время суток: парк, набережная, двор или загородная площадка. Перед съёмкой смотрю карту и предлагаю два-три варианта."))
    s4 = section("plan", f"Свадебный день в городе {n}: пример плана", steps_html(env) + P("План гибкий: подстраиваюсь под ваш тайминг, убираю лишнее и добавляю нужное. За пределами Москвы подробности выезда уточняем при бронировании."))
    s5 = section("banket", f"Банкеты и семейные события в городе {n}", P(f"Снимаю банкеты в ресторанах, банкетных залах и загородных домах, юбилеи, крещения, детские праздники. Приезжаю заранее, смотрю свет, договариваюсь с организатором о тайминге.") + service_chips())
    s6 = section("ceny", f"Сколько стоит фотограф в городе {n}", rows_html() + P("Это ориентиры. Точную стоимость назову после вашего сообщения."))
    faq = [
        (f"Сколько стоит свадебный фотограф в городе {n}?", "Роспись в ЗАГСе стоит 5 000 ₽. При съёмке по часам первый час 5 000 ₽, каждый следующий 3 000 ₽: например, ЗАГС и прогулка на 3 часа обойдутся в 11 000 ₽, а день на 6 часов в 20 000 ₽."),
        (f"Вы выезжаете в город {n}?", f"Да, снимаю по Москве и Подмосковью, город {n} не исключение. Напишите дату, место и время, и я сразу отвечу, свободен ли."),
        ("Можно ли расписаться в другом городе или в Москве?", "Как правило, да: заявление можно подать не только по месту жительства. Правила и свободные даты уточняйте на Госуслугах или у местного отдела ЗАГС."),
        ("Как быстро я получу фотографии?", "Обрабатываю быстро и отдаю готовые кадры по ссылке. Точный срок называю при бронировании."),
    ]
    s7 = section("faq", "Частые вопросы", '<div class="dz-faq">' + faq_html(faq) + "</div>")
    oth = section("goroda", "Другие города Подмосковья", '<div class="dz-links">' + "".join(f'<a class="chip" href="{x["url"]}">{x["name"]}</a>' for x in others if x["slug"] != c["slug"]) + '</div>' + P('<a href="/podmoskove/">Все города</a> · <a href="/moskva/">Районы Москвы</a> · <a href="/zags/">ЗАГСы Москвы</a>'))
    body = "\n".join([s1, s2, s3, s4, s5, s6, s7, oth])
    toc = [("kto", "Как проходит съёмка"), ("zags", "ЗАГС и запись"), ("mesta", "Где снимать"), ("plan", "План дня"), ("banket", "Банкет и события"), ("ceny", "Цены"), ("faq", "Вопросы")]
    cover = f"img/podmoskove/{c['slug']}.jpg"
    if exists(cover): cover_alt = f"Город {n}: атмосфера для свадебной прогулки"
    else:
        pk = portfolio_cover("podm", c["slug"]); cover = _W + pk + ".jpg"
        cover_alt = long_alt(pk, f"свадебный фотограф, ЗАГС, венчание и свадебная прогулка — {n}, Московская область", "Выезд свадебного фотографа в Подмосковье: роспись, венчание, прогулка, банкет, съёмка от 5 000 ₽.")
    area = [{"@type": "City", "name": n}, {"@type": "AdministrativeArea", "name": "Московская область"}]
    return page(path, title, desc, h1, lead, [("/", "Главная"), ("/podmoskove/", "Подмосковье"), (path, n)], body, tags=tags, cover=cover, cover_alt=cover_alt, faq=faq, area=area, geo="RU-MOS", place=f"{n}, Московская область", toc=toc)

# ------------------------------------------------------------------ страницы ЗАГСов
ZAGS_STEPS = [
 ("Приезд и встреча", "Приезжаю за 30–40 минут до времени церемонии, оцениваю свет в холле и зале и согласую с сотрудниками, где можно снимать."),
 ("Ожидание и детали", "Пока гости собираются, снимаю детали: букет, кольца, образы, первые волнения. Это те кадры, которые потом хочется пересматривать."),
 ("Церемония", "Снимаю роспись с нескольких точек: клятвы, кольца, подпись, первый поцелуй, лица родителей. Не мешаю и не командую."),
 ("Поздравления", "Объятия, слёзы, смех и шампанское. Лучшие эмоции обычно случаются сразу после росписи."),
 ("Групповые фото", "Родители, друзья, свидетели: быстро делаю общие кадры у входа или в зале, чтобы дальше ехать на прогулку."),
 ("Выход и дорога", "Снимаю выход пары, лепестки, рис или мыльные пузыри (если в ЗАГС это разрешено) и провожаю до машины."),
]

def build_zags(k, same_okr, near_districts):
    z = zinfo(k); nom = z["nom"]; okr = z["okr"]
    path = z["url"]
    short_loc = z["loc"].split(" «")[0] if z["kind"] == "palace" else z["loc"]
    title = f"Фотограф {short_loc}: адрес, съёмка росписи | Фотограф.art" if z["kind"] == "otdel" else f"Фотограф {short_loc}: адрес и съёмка | Фотограф.art"
    desc = f"Фотограф для росписи {z['loc']}. Адрес: Москва, {z['addr']}. Роспись 5 000 ₽, прогулка и банкет считаются по часам."
    if len(desc) > 165: desc = desc[:162].rsplit(" ", 1)[0] + "…"
    h1 = f"Фотограф {z['loc']}"
    lead = f"Снимаю росписи {z['loc']}: приезжаю заранее, работаю тихо и ловлю живые эмоции. Роспись 5 000 ₽, прогулка после ЗАГС оплачивается по часам."
    tags = [f"<b>{okr}</b>", f"Адрес: <b>{z['addr']}</b>", "Роспись <b>5 000 ₽</b>"]
    s1 = section("adres", f"Адрес: {nom}",
        P(f"<b>Адрес:</b> Москва, {z['addr']}.") +
        P("Часы работы, запись и правила проведения церемонии могут меняться, поэтому перед визитом перепроверьте их на mos.ru или в Госуслугах. Это важно, если вы приглашаете большую компанию гостей.") +
        ('<div class="dz-note rv">Во дворцах бракосочетания, как правило, несколько залов и просторный холл, поэтому уточните, какой зал вам назначили: от него зависит свет и фон для кадров.</div>' if z["kind"] == "palace" else '<div class="dz-note rv">В районных отделах залы обычно компактнее дворцовых. Заранее уточните число гостей и правила съёмки внутри.</div>'))
    s2 = section("kak", f"Как проходит роспись {z['loc']} и что я снимаю",
        P("Типичный ход церемонии выглядит так. Порядок и время зависят от конкретного ЗАГС, поэтому я подстраиваюсь под него.") +
        '<div class="dz-steps">' + "".join(f'<div class="dz-step"><b>{t}</b><span>{x}</span></div>' for t, x in ZAGS_STEPS) + "</div>" +
        P("Сама церемония, как правило, короткая, до получаса вместе с поздравлениями. Поэтому важно расставить приоритеты заранее: кого именно из гостей вы хотите видеть на фото."))
    tips = """<ul>
<li><b>Приезжайте заранее.</b> Закладывайте минимум полчаса до начала: нужно найти парковку, переодеться, собраться.</li>
<li><b>Уточните правила съёмки внутри.</b> Они зависят от ЗАГС и могут отличаться: лучше узнать при подаче заявления.</li>
<li><b>Продумайте дорогу.</b> В пятницу и субботу трафик плотнее, особенно в центре: заложите запас.</li>
<li><b>Договоритесь о составе.</b> Определите, кто идёт в зал, а кто ждёт: так проще расставить гостей для общих фото.</li>
</ul>"""
    s3 = section("podgotovka", "Как подготовиться к съёмке", tips)
    # где гулять
    near_places = []
    for dd in near_districts:
        for p in dd["places"]:
            near_places.append((p, dd))
    if near_places:
        sel = near_places[:6]
        cards = '<div class="dz-pls">' + "".join(f'<div class="dz-pl"><b>{p[0]}</b><span>Район <a href="{dd["url"]}">{dd["name"]}</a>. {PLACE_KIND[p[1]]}</span></div>' for p, dd in sel) + "</div>"
        walk = P(f"После росписи удобно ехать на прогулку недалеко от ЗАГС. По данным справочников, неподалёку расположены такие места, и я бы рассмотрел их в первую очередь:") + cards + P("Точный маршрут подберу под ваш тайминг, сезон и количество гостей.")
    else:
        walk = P("Место для прогулки после росписи подбираю под ваш маршрут: парк, набережная или двор. Заранее смотрю карту и предлагаю два-три варианта.")
    if near_districts:
        walk += '<div class="dz-links">' + "".join(f'<a class="chip" href="{dd["url"]}">{dd["name"]}</a>' for dd in near_districts[:12]) + "</div>"
    s4 = section("progulka", f"Где погулять после росписи {z['loc']}", walk)
    s5 = section("ceny", "Сколько стоит съёмка", P("Платите только за время съёмки: роспись фиксирована, прогулка и банкет считаются по часам.") + rows_html())
    faq = [
        (f"Где находится {nom}?", f"Адрес: Москва, {z['addr']}. Режим работы и правила уточняйте на mos.ru или в Госуслугах."),
        ("Можно ли снимать внутри ЗАГС?", "Как правило, да, но правила зависят от конкретного ЗАГС и зала. Уточните при подаче заявления и сообщите мне: я подстроюсь."),
        ("Во сколько приезжать на церемонию?", "Лучше приехать минимум за полчаса до начала. Я стараюсь быть на месте раньше, чтобы оценить свет и успеть снять детали."),
        ("Сколько стоит фотограф на роспись?", "Роспись в ЗАГСе стоит 5 000 ₽. Если после ЗАГС идёте на прогулку или банкет, считаем по часам: первый час 5 000 ₽, каждый следующий 3 000 ₽."),
        ("Как быстро получу фото?", "Обрабатываю быстро и отдаю по ссылке. Точный срок называю при бронировании."),
    ]
    s6 = section("faq", "Частые вопросы", '<div class="dz-faq">' + faq_html(faq) + "</div>")
    others = [x for x in same_okr if x != k]
    s7 = section("eshche", f"Другие ЗАГСы: {OKRUGS[okr][1]}", '<div class="dz-links">' + "".join(f'<a class="chip" href="/zags/{x}.html">{zinfo(x)["nom"]}</a>' for x in others) + "</div>" + P('<a href="/zags/">Все ЗАГСы Москвы</a> · <a href="/moskva/">Районы Москвы</a>')) if others else section("eshche", "Ещё ЗАГСы", P('<a href="/zags/">Все ЗАГСы Москвы</a> · <a href="/moskva/">Районы Москвы</a>'))
    body = "\n".join([s1, s2, s3, s4, s5, s6, s7])
    toc = [("adres", "Адрес"), ("kak", "Как проходит роспись"), ("podgotovka", "Подготовка"), ("progulka", "Где погулять"), ("ceny", "Цены"), ("faq", "Вопросы")]
    cover = f"img/zags/{k}.jpg"
    if exists(cover): cover_alt = f"{nom}: атмосфера места"
    else:
        pk = portfolio_cover("palace" if z["kind"] == "palace" else "zags", k); cover = _W + pk + ".jpg"
        cover_alt = long_alt(pk, f"фотограф в ЗАГС: {nom}, {z['addr']}, Москва", "Съёмка росписи в ЗАГСе от 5 000 ₽: встреча у входа, церемония, первые поздравления и фото на память. Кадр показывает стиль работы, а не интерьер этого ЗАГСа.")
    extra = [{"@type": "GovernmentOffice", "name": nom, "address": {"@type": "PostalAddress", "streetAddress": z["addr"], "addressLocality": "Москва", "addressCountry": "RU"}}]
    return page(path, title, desc, h1, lead, [("/", "Главная"), ("/zags/", "ЗАГСы Москвы"), (path, nom)], body, tags=tags, cover=cover, cover_alt=cover_alt, faq=faq, area=BUSINESS_AREA_MSK, place="Москва", extra_schema=extra, toc=toc)

# ------------------------------------------------------------------ хабы
def okr_block(compact=False):
    out = []
    for code, (full, short, _) in OKRUGS.items():
        ds = by_okr.get(code, [])
        if not ds: continue
        cnt = len(ds)
        label = plural(cnt, ("район", "района", "районов")) if code != "НАО" else plural(cnt, ("населённый пункт", "населённых пункта", "населённых пунктов"))
        chips = "".join(f'<a class="chip" href="{d["url"]}">{d["name"]}</a>' for d in ds)
        out.append(f'<details class="okr"><summary><span>{short} · {code}<small>{cnt} {label}</small></span></summary><div class="okr-in">{chips}</div></details>')
    return '<div class="okr-g">' + "".join(out) + "</div>"

def home_block():
    return f"""<!--RAJONY-START-->
<section class="sec rn" id="rajony">
  <div class="wrap">
    <div class="rn-h">
      <div style="display:grid;gap:18px"><div class="eyebrow">Где снимаю</div><h2>Фотограф по <em>районам</em> Москвы</h2></div>
      <p class="lead">Выбирайте свой район: расскажу про ближайшие ЗАГСы с адресами, места для прогулки и стоимость съёмки.</p>
    </div>
    <div class="rn-tools"><input class="rn-q" id="rnQ" type="search" placeholder="Найти район, например Кузьминки" aria-label="Найти район" autocomplete="off"></div>
    {okr_block()}
    <div class="rn-more">
      <a class="btn btn-light" href="/moskva/">Все районы Москвы</a>
      <a class="btn btn-ghost" href="/zags/">ЗАГСы Москвы</a>
      <a class="btn btn-ghost" href="/podmoskove/">Подмосковье</a>
    </div>
  </div>
</section>
<!--RAJONY-END-->
"""

def hub_moskva():
    n_all = len(MSK_REAL)
    body = section("o", "Как выбрать свой район",
        P(f"Я снимаю свадьбы, росписи в ЗАГСе, венчания, банкеты и семейные события во всех {n_all} районах Москвы и в Подмосковье. На странице каждого района вы найдёте ближайшие ЗАГСы с адресами, места для свадебной прогулки, примерный план дня и цены.") +
        P("Расписаться в Москве, как правило, можно в любом отделе ЗАГС независимо от места жительства, поэтому выбирайте не по прописке, а по маршруту дня: от ЗАГС до места прогулки и банкета.") +
        P('Если вы ищете именно ЗАГС, откройте <a href="/zags/">справочник ЗАГСов Москвы</a>, а если событие за городом, посмотрите <a href="/podmoskove/">города Подмосковья</a>.')) + \
        section("rajony", "Районы Москвы по округам", '<div class="rn-tools"><input class="rn-q" id="rnQ" type="search" placeholder="Найти район, например Кузьминки" aria-label="Найти район" autocomplete="off"></div>' + okr_block()) + \
        section("ceny", "Сколько это стоит", P("Цены одинаковы для всех районов: платите только за время съёмки.") + rows_html() + service_chips())
    faq = [
        ("Вы снимаете во всех районах Москвы?", "Да, снимаю по всей Москве и Подмосковью. Напишите дату и место, и я сразу отвечу, свободен ли."),
        ("Есть ли доплата за выезд в другой район?", "Стоимость считается по времени съёмки, без пакетов и скрытых доплат. Детали выезда обсуждаем при бронировании."),
        ("Можно ли расписаться в ЗАГСе не по месту жительства?", "Как правило, да: в Москве заявление подают в любой отдел независимо от места жительства. Правила уточняйте на Госуслугах."),
    ]
    body += section("faq", "Частые вопросы", '<div class="dz-faq">' + faq_html(faq) + "</div>")
    title = f"Свадебный фотограф по районам Москвы — все {n_all} районов | Фотограф.art"
    desc = f"Свадебный фотограф во всех {n_all} районах Москвы: ЗАГСы с адресами, места для прогулки, цены. Роспись 5 000 ₽, первый час 5 000 ₽, далее 3 000 ₽/час."
    return page("/moskva/", title, desc, "Свадебный фотограф по районам Москвы", f"Все {n_all} районов Москвы и Новая Москва: ближайшие ЗАГСы, места для прогулки и цены. Выберите свой район.", [("/", "Главная"), ("/moskva/", "Районы Москвы")], body, tags=[f"<b>{n_all}</b> районов", "Первый час <b>5 000 ₽</b>"], faq=faq, area=BUSINESS_AREA_MSK)

def hub_zags():
    groups = {}
    for k in ZAGS: groups.setdefault(ZAGS[k][5], []).append(k)
    out = []
    for code in OKRUGS:
        ks = groups.get(code)
        if not ks: continue
        out.append(f'<h3>{OKRUGS[code][0]}</h3>' + zags_cards(ks))
    guide = section("kak", "Как выбрать ЗАГС в Москве",
        P("В Москве есть дворцы бракосочетания и районные отделы ЗАГС. Дворцы, как правило, просторнее и торжественнее, районные отделы компактнее и уютнее. Выбор зависит от числа гостей, бюджета на оформление и маршрута дня.") +
        """<ul>
<li><b>Определите число гостей.</b> От него зависит выбор зала.</li>
<li><b>Посмотрите на маршрут.</b> От ЗАГС до места прогулки и банкета должно быть удобно ехать.</li>
<li><b>Спросите про зал и свет.</b> Для фото важны окна, высота потолка и фон.</li>
<li><b>Подайте заявление заранее.</b> Через Госуслуги, регистрация, как правило, проходит не раньше чем через месяц после подачи.</li>
</ul>""" +
        '<div class="dz-note rv">Адреса собраны из открытых справочников. Перед визитом перепроверьте их и режим работы на mos.ru или в Госуслугах.</div>')
    spisok = section("spisok", f"ЗАГСы Москвы: адреса ({len(ZAGS)})", "".join(out))
    price = section("ceny", "Сколько стоит фотограф на роспись", rows_html() + service_chips())
    faq = [
        ("Сколько стоит фотограф на роспись в ЗАГСе?", "Роспись в ЗАГСе стоит 5 000 ₽. Если после росписи идёте на прогулку или банкет, считаем по часам: первый час 5 000 ₽, каждый следующий 3 000 ₽."),
        ("В каком ЗАГС Москвы лучше расписаться?", "Лучший ЗАГС — тот, который удобен вам и гостям по маршруту и подходит по залу. Посмотрите страницы ЗАГСов и районов: на них я описал места для прогулки рядом."),
        ("Можно ли расписаться не по месту регистрации?", "Как правило, да, в Москве заявление можно подать в любой отдел. Уточните правила на Госуслугах."),
    ]
    body = guide + spisok + price + section("faq", "Частые вопросы", '<div class="dz-faq">' + faq_html(faq) + "</div>")
    title = f"ЗАГСы Москвы: адреса, как выбрать, фотограф на роспись | Фотограф.art"
    desc = f"Справочник ЗАГСов Москвы: {len(ZAGS)} адресов, как выбрать ЗАГС, где гулять после росписи. Фотограф на роспись: 5 000 ₽."
    return page("/zags/", title, desc, "ЗАГСы Москвы: адреса и фотограф на роспись", f"Справочник из {len(ZAGS)} ЗАГСов и дворцов бракосочетания Москвы с адресами, подсказками по выбору и местами для прогулки рядом.", [("/", "Главная"), ("/zags/", "ЗАГСы Москвы")], body, tags=[f"<b>{len(ZAGS)}</b> ЗАГСов", "Роспись <b>5 000 ₽</b>"], faq=faq, area=BUSINESS_AREA_MSK)

def hub_podm():
    chips = '<div class="dz-links">' + "".join(f'<a class="chip" href="{c["url"]}">{c["name"]}</a>' for c in cities) + "</div>"
    withz = [c for c in cities if c["addr"]]
    zl = '<div class="dz-zcs">' + "".join(f'<a class="dz-zc" href="{c["url"]}"><small>Подмосковье</small><b>{c["name"]}</b><span>{c["addr"]}</span></a>' for c in withz) + "</div>"
    body = section("o", "Свадебный фотограф в Подмосковье", P("Снимаю росписи в ЗАГСе, свадьбы, венчания, банкеты и семейные события в городах Подмосковья. Выбирайте свой город: на странице найдёте адрес отдела ЗАГС, места для съёмки и цены.") + P("Расписаться можно по месту жительства или в Москве: правила уточняйте на Госуслугах. Подробности выезда за пределы Москвы согласуем при бронировании.")) + \
           section("goroda", "Города Подмосковья", chips) + \
           section("zags", "Отделы ЗАГС Подмосковья: адреса", P("По открытым справочникам, перепроверьте перед визитом на сайте Главного управления ЗАГС Московской области.") + zl) + \
           section("ceny", "Сколько это стоит", rows_html() + service_chips())
    faq = [
        ("Вы снимаете в Подмосковье?", "Да, снимаю по всей Москве и Подмосковью. Напишите дату, город и место, и я сразу отвечу, свободен ли."),
        ("Сколько стоит фотограф в Подмосковье?", "Роспись в ЗАГСе 5 000 ₽, первый час съёмки 5 000 ₽, каждый следующий 3 000 ₽. Подробности выезда обсуждаем при бронировании."),
    ]
    body += section("faq", "Частые вопросы", '<div class="dz-faq">' + faq_html(faq) + "</div>")
    return page("/podmoskove/", "Свадебный фотограф в Подмосковье — города, ЗАГСы, цены | Фотограф.art", f"Свадебный фотограф в {len(cities)} городах Подмосковья: адреса ЗАГСов, места для съёмки, цены. Роспись 5 000 ₽, первый час 5 000 ₽.", "Свадебный фотограф в Подмосковье", f"{len(cities)} городов: Балашиха, Химки, Красногорск, Одинцово, Подольск и другие. Адреса ЗАГСов и места для съёмки.", [("/", "Главная"), ("/podmoskove/", "Подмосковье")], body, tags=[f"<b>{len(cities)}</b> городов", "Первый час <b>5 000 ₽</b>"], faq=faq, area=BUSINESS_AREA_MSK, geo="RU-MOS", place="Московская область")

# ------------------------------------------------------------------ сборка
def patch_index():
    p = os.path.join(ROOT, "index.html")
    s = open(p, encoding="utf-8").read()
    blk = nb(home_block())
    if "<!--RAJONY-START-->" in s:
        s = re.sub(r"<!--RAJONY-START-->.*?<!--RAJONY-END-->\n?", blk, s, flags=re.S)
    else:
        assert "<!-- SEO TEXT + FAQ -->" in s
        s = s.replace("<!-- SEO TEXT + FAQ -->", blk + "\n<!-- SEO TEXT + FAQ -->", 1)
    open(p, "w", encoding="utf-8").write(s)

LINKS_FOOT = '<a href="/moskva/">Районы Москвы</a><a href="/zags/">ЗАГСы Москвы</a><a href="/podmoskove/">Подмосковье</a>'
def patch_existing_footers():
    import glob
    for p in glob.glob(os.path.join(ROOT, "*.html")):
        if os.path.basename(p).startswith("yandex_"): continue
        s = open(p, encoding="utf-8").read()
        if 'class="ftr-svc"' in s and 'href="/zags/"' not in s:
            s = re.sub(r'(<nav class="ftr-svc"[^>]*>.*?)(</nav>)', lambda m: m.group(1) + LINKS_FOOT + m.group(2), s, count=1, flags=re.S)
            open(p, "w", encoding="utf-8").write(s)

def sitemap(urls):
    p = os.path.join(ROOT, "sitemap.xml")
    s = open(p, encoding="utf-8").read()
    s = re.sub(r"<!--GEN-->.*?<!--/GEN-->\n?", "", s, flags=re.S)
    rows = []
    for u, pr in urls:
        rows.append(f"<url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>{pr}</priority></url>")
    gen = "<!--GEN-->\n" + "\n".join(rows) + "\n<!--/GEN-->\n"
    s = s.replace("</urlset>", gen + "</urlset>")
    open(p, "w", encoding="utf-8").write(s)

def main():
    import glob
    for d in ("moskva", "zags", "podmoskove"):          # убираем старые сгенерированные страницы
        for f in glob.glob(os.path.join(ROOT, d, "*.html")): os.remove(f)
    urls = []
    write("moskva/index.html", hub_moskva()); urls.append(("/moskva/", "0.9"))
    write("zags/index.html", hub_zags()); urls.append(("/zags/", "0.9"))
    write("podmoskove/index.html", hub_podm()); urls.append(("/podmoskove/", "0.9"))
    for d in districts:
        sib = by_okr[d["okr"]]
        write(f"moskva/{d['slug']}.html", build_district(d, sib)); urls.append((d["url"], "0.7"))
    for c in cities:
        write(f"podmoskove/{c['slug']}.html", build_city(c, cities)); urls.append((c["url"], "0.6"))
    groups = {}
    for k in ZAGS: groups.setdefault(ZAGS[k][5], []).append(k)
    for k in ZAGS:
        near = [d for d in districts if k in d["zags"]]
        # районы, у которых этот ЗАГС первый, показываем первыми
        near.sort(key=lambda d: (d["zags"].index(k), d["name"]))
        write(f"zags/{k}.html", build_zags(k, groups[ZAGS[k][5]], near)); urls.append((f"/zags/{k}.html", "0.7"))
    patch_index(); patch_existing_footers(); sitemap(urls)
    print("districts:", len(districts), "(Москва:", len(MSK_REAL), ") cities:", len(cities), "zags:", len(ZAGS), "urls:", len(urls))

if __name__ == "__main__":
    main()
