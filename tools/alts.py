# -*- coding: utf-8 -*-
"""Однократно (идемпотентно) расширяет alt у всех картинок корневых страниц до подробных описаний.
Запуск: python3 tools/alts.py"""
import re, glob, os, json, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WED = "свадебный фотограф в Москве: роспись в ЗАГСе, венчание, свадебная прогулка, банкет и детали свадьбы"
TOPIC = {
 "index.html": "свадебный фотограф в Москве и Подмосковье, а также интерьерная, предметная, архитектурная и событийная фотосъёмка",
 "svadebnyj-fotograf.html": WED,
 "uslugi.html": "услуги фотографа в Москве и Подмосковье: свадьбы, ЗАГС, интерьеры, предметка, архитектура, события",
 "arhitekturnaya-fotosemka.html": "архитектурная фотосъёмка жилых комплексов, домов и коттеджей в Москве и Подмосковье",
 "avtofotograf.html": "автофотограф в Москве: съёмка автомобилей для продажи, рекламы и на память",
 "detskij-fotograf.html": "детский фотограф в Москве: дни рождения, праздники и семейные съёмки",
 "fotograf-na-kreshhenie.html": "фотограф на крещение в Москве: таинство, храм и семейные кадры",
 "fotograf-na-vypusknoj.html": "фотограф на выпускной в Москве: школа, сад, торжественная часть и вечеринка",
 "fotograf-na-vystavku.html": "фотограф на выставку, конференцию и корпоратив в Москве, событийная съёмка",
 "fotosessiya-zhivotnyh.html": "фотосессия животных в Москве: домашние питомцы в студии и на улице",
 "interernaya-fotosemka.html": "фотосъёмка квартир, домов и интерьеров в Москве для продажи, аренды и портфолио дизайнеров",
 "motofotograf.html": "мотофотограф в Москве: съёмка мотоциклов и байкеров",
 "predmetnaya-fotosemka.html": "предметная фотосъёмка товаров для маркетплейсов, каталогов и рекламы в Москве",
 "promyshlennaya-fotosemka.html": "промышленная фотосъёмка заводов, цехов и производств в Москве и Московской области",
 "semka-videourokov.html": "видеозапись и съёмка видеоуроков в Москве",
 "sozdanie-logotipa.html": "создание логотипа и фирменного стиля под ключ",
 "privacy.html": "фотограф Дмитрий, Фотограф.art",
}
TPL = [
 "{o}. Фотография из портфолио фотографа Дмитрия (Фотограф.art): {t}. Работаю в Москве и Московской области, готовые фото отдаю по ссылке.",
 "{o}. Кадр из работ Фотограф.art: {t}. Естественный стиль, мягкий свет, быстрая обработка, выезд по Москве и Подмосковью.",
 "{o}. Пример работы фотографа Дмитрия, Москва: {t}. Условия и стоимость съёмки указаны на сайте, связаться можно в мессенджере или по телефону.",
]
MARK = ("Фотограф.art", "Дмитрия")
def long(o, t, n):
    o = html.unescape(o).strip().rstrip(".")
    if len(o) > 150 or any(m in o for m in MARK): return None
    return TPL[n % 3].format(o=o, t=t)
tot = 0
for f in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
    b = os.path.basename(f)
    if b not in TOPIC: continue
    s = open(f, encoding="utf-8").read(); n = 0; t = TOPIC[b]
    def img(m):
        global tot, n
        tag = m.group(0)
        if "mc.yandex" in tag or re.search(r"class=\"[^\"]*logo", tag): return tag
        a = re.search(r'alt="([^"]*)"', tag)
        if not a or not a.group(1).strip(): return tag
        l = long(a.group(1), t, n)
        if not l: return tag
        n += 1; tot += 1
        return tag.replace(a.group(0), 'alt="%s"' % html.escape(l, quote=True), 1)
    s2 = re.sub(r"<img\b[^>]*>", img, s)
    def js(m):
        global tot, n
        o = json.loads('"%s"' % m.group(1))
        l = long(o, t, n)
        if not l: return m.group(0)
        n += 1; tot += 1
        return '"alt": ' + json.dumps(l, ensure_ascii=False)
    s2 = re.sub(r'"alt": "((?:[^"\\]|\\.)*)"', js, s2)
    if s2 != s: open(f, "w", encoding="utf-8").write(s2)
print("alt расширено:", tot)
