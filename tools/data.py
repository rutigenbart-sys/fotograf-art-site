# -*- coding: utf-8 -*-
"""Данные для генерации страниц: районы Москвы, ЗАГСы, города Подмосковья.

ВАЖНО про достоверность: адреса ЗАГСов сверены по нескольким открытым справочникам
(lexpages.ru, limo-vip.ru, столичный-риелтор.рф, fotkay-msk.ru). Перед печатью/рекламой
их стоит перепроверить на mos.ru / gosuslugi.ru. Достопримечательности указаны только
те, в которых автор данных уверен; если не уверен — поле пустое (страница тогда описывает
тип среды района, а не конкретные места).
"""

SITE = "https://xn--80af6aaljmg.art"
PHONE = "+7 926 854-23-33"
TEL = "+79268542333"

# ---------------------------------------------------------------- ЗАГСы Москвы
# key: (nom, loc, gen, ins, addr, okrug_code, kind)
def _o(name):  # отдел ЗАГС «name»
    return (f"ЗАГС «{name}»", f"в ЗАГСе «{name}»", f"ЗАГСа «{name}»", f"ЗАГСом «{name}»")

def _p(num, nick=None):
    t = f"№ {num}" + (f" «{nick}»" if nick else "")
    return (f"Дворец бракосочетания {t}", f"во Дворце бракосочетания {t}", f"Дворца бракосочетания {t}", f"Дворцом бракосочетания {t}")

ZAGS = {
 "dvorec-1":        (*_p(1, "Грибоедовский"), "Малый Харитоньевский пер., 10", "ЦАО", "palace"),
 "dvorec-3":        (*_p(3), "ул. Юных Ленинцев, 35", "ЮВАО", "palace"),
 "dvorec-4":        (*_p(4, "Савёловский"), "Бутырская ул., 17", "САО", "palace"),
 "dvorec-5":        (*_p(5, "Дворец Счастья"), "Измайловское шоссе, 73ж", "ВАО", "palace"),
 "akademicheskij":  (*_o("Академический"), "Профсоюзная ул., 13/12", "ЮЗАО", "otdel"),
 "babushkinskij":   (*_o("Бабушкинский"), "ул. Менжинского, 23, корп. 1", "СВАО", "otdel"),
 "bogorodskij":     (*_o("Богородский"), "бульвар Маршала Рокоссовского, 21/21", "ВАО", "otdel"),
 "vernadskij":      (*_o("Вернадский"), "ул. Лобачевского, 2", "ЗАО", "otdel"),
 "gagarinskij":     (*_o("Гагаринский"), "Ленинский проспект, 44", "ЮЗАО", "otdel"),
 "dmitrovskij":     (*_o("Дмитровский"), "Коровинское шоссе, 6, корп. 2", "САО", "otdel"),
 "zelenogradskij":  (*_o("Зеленоградский"), "Зеленоград, корпус 240", "ЗелАО", "otdel"),
 "izmajlovskij":    (*_o("Измайловский"), "9-я Парковая ул., 5А", "ВАО", "otdel"),
 "kuncevskij":      (*_o("Кунцевский"), "Полоцкая ул., 23/17", "ЗАО", "otdel"),
 "kutuzovskij":     (*_o("Кутузовский"), "Кутузовский проспект, 23", "ЗАО", "otdel"),
 "levoberezhnyj":   (*_o("Левобережный"), "Фестивальная ул., 9", "САО", "otdel"),
 "lyublinskij":     (*_o("Люблинский"), "8-я ул. Текстильщиков, 14", "ЮВАО", "otdel"),
 "medvedkovskij":   (*_o("Медведковский"), "ул. Молодцова, 1А", "СВАО", "otdel"),
 "meshchanskij":    (*_o("Мещанский"), "проспект Мира, 16", "ЦАО", "otdel"),
 "nagatinskij":     (*_o("Нагатинский"), "Нагатинская набережная, 34", "ЮАО", "otdel"),
 "perovskij":       (*_o("Перовский"), "Перовская ул., 43", "ВАО", "otdel"),
 "ryazanskij":      (*_o("Рязанский"), "1-я Новокузьминская ул., 3", "ЮВАО", "otdel"),
 "solncevskij":     (*_o("Солнцевский"), "Боровский проезд, 2", "ЗАО", "otdel"),
 "taganskij":       (*_o("Таганский"), "Таганская ул., 44", "ЦАО", "otdel"),
 "tverskoj":        (*_o("Тверской"), "3-я Тверская-Ямская ул., 52", "ЦАО", "otdel"),
 "tushinskij":      (*_o("Тушинский"), "Химкинский бульвар, 14", "СЗАО", "otdel"),
 "hamovnicheskij":  (*_o("Хамовнический"), "1-й Вражский пер., 4", "ЦАО", "otdel"),
 "horoshevskij":    (*_o("Хорошёвский"), "ул. Народного Ополчения, 23, корп. 2", "СЗАО", "otdel"),
 "caricynskij":     (*_o("Царицынский"), "ул. Кантемировская, 9", "ЮАО", "otdel"),
 "cheremushkinskij":(*_o("Черёмушкинский"), "ул. Миклухо-Маклая, 20", "ЮЗАО", "otdel"),
 "chertanovskij":   (*_o("Чертановский"), "ул. Ялтинская, 1А", "ЮАО", "otdel"),
 "zamoskvoreckij":  (*_o("Замоскворецкий"), "Озерковский пер., 4", "ЦАО", "otdel"),
}

# ---------------------------------------------------------------- Округа Москвы
# code: (full name, short, genitive-ish phrase used in text)
OKRUGS = {
 "ЦАО":   ("Центральный административный округ", "Центр", "cao"),
 "САО":   ("Северный административный округ", "Север", "sao"),
 "СВАО":  ("Северо-Восточный административный округ", "Северо-Восток", "svao"),
 "ВАО":   ("Восточный административный округ", "Восток", "vao"),
 "ЮВАО":  ("Юго-Восточный административный округ", "Юго-Восток", "yuvao"),
 "ЮАО":   ("Южный административный округ", "Юг", "yuao"),
 "ЮЗАО":  ("Юго-Западный административный округ", "Юго-Запад", "yuzao"),
 "ЗАО":   ("Западный административный округ", "Запад", "zao"),
 "СЗАО":  ("Северо-Западный административный округ", "Северо-Запад", "szao"),
 "ЗелАО": ("Зеленоградский административный округ", "Зеленоград", "zelao"),
 "НАО":   ("Новая Москва (Новомосковский и Троицкий округа)", "Новая Москва", "tinao"),
}

# Типы мест -> короткое описание (без выдуманных фактов)
PLACE_KIND = {
 "park":     "Зелёные аллеи, пруды и поляны: мягкий свет и много укромных мест для прогулки после росписи и love story.",
 "estate":   "Исторический ансамбль: архитектура, аллеи и фактуры, которые выглядят дорого в любое время года.",
 "temple":   "Храм или монастырь: подходит для венчания и крещения. Правила съёмки внутри лучше уточнить заранее.",
 "emb":      "Набережная или пойма: вода, простор и закат. Хорошо работает летом и зимой при морозном воздухе.",
 "monument": "Узнаваемое место: сильный фон для свадебных кадров и семейных фотографий.",
 "city":     "Городская среда: стекло, высотки и отражения. Динамичный современный сюжет.",
}

# ---------------------------------------------------------------- Районы Москвы
# (название, [env], [zags], [(место, тип)], kind)
# env: center, park, river, estate, sleeper, industrial, newm, city
D = {}
def add(okr, rows):
    D[okr] = rows

add("ЦАО", [
 ("Арбат", ["center", "estate"], ["hamovnicheskij","tverskoj","zamoskvoreckij"], [("Храм Христа Спасителя","temple"),("Улица Арбат","monument"),("Гоголевский бульвар","park")]),
 ("Басманный", ["center"], ["dvorec-1","meshchanskij","taganskij"], [("Чистые пруды","park"),("Сад имени Баумана","park")]),
 ("Замоскворечье", ["center","estate"], ["zamoskvoreckij","taganskij","hamovnicheskij"], [("Марфо-Мариинская обитель","temple"),("Третьяковская галерея","monument")]),
 ("Красносельский", ["center"], ["dvorec-1","meshchanskij","tverskoj"], [("Красные Ворота","monument")]),
 ("Мещанский", ["center"], ["meshchanskij","dvorec-1","tverskoj"], [("Екатерининский парк","park")]),
 ("Пресненский", ["center","city"], ["tverskoj","hamovnicheskij","kutuzovskij"], [("Москва-Сити","city"),("Патриаршие пруды","park"),("Парк «Красная Пресня»","park")]),
 ("Таганский", ["center","estate"], ["taganskij","zamoskvoreckij","dvorec-1"], [("Новоспасский монастырь","temple"),("Крутицкое подворье","temple"),("Таганский парк","park")]),
 ("Тверской", ["center"], ["tverskoj","dvorec-1","meshchanskij"], [("Красная площадь","monument"),("Парк «Зарядье»","park"),("Тверской бульвар","park")]),
 ("Хамовники", ["center","river","estate"], ["hamovnicheskij","gagarinskij","kutuzovskij"], [("Новодевичий монастырь","temple"),("Лужники","emb"),("Фрунзенская набережная","emb")]),
 ("Якиманка", ["center","river"], ["zamoskvoreckij","hamovnicheskij","gagarinskij"], [("Парк «Музеон»","park"),("Крымская набережная","emb")]),
])
add("САО", [
 ("Аэропорт", ["sleeper","park"], ["dvorec-4","horoshevskij","tverskoj"], [("Петровский путевой дворец","estate")]),
 ("Беговой", ["sleeper"], ["dvorec-4","horoshevskij","tverskoj"], [("Московский ипподром","monument"),("Ходынское поле","park")]),
 ("Бескудниковский", ["sleeper"], ["dmitrovskij","dvorec-4","levoberezhnyj"], []),
 ("Войковский", ["sleeper","park"], ["levoberezhnyj","dvorec-4","horoshevskij"], []),
 ("Восточное Дегунино", ["sleeper"], ["dmitrovskij","dvorec-4","levoberezhnyj"], []),
 ("Головинский", ["sleeper","river"], ["levoberezhnyj","dvorec-4","dmitrovskij"], [("Головинские пруды","park")]),
 ("Дмитровский", ["sleeper"], ["dmitrovskij","dvorec-4","levoberezhnyj"], []),
 ("Западное Дегунино", ["sleeper"], ["dmitrovskij","levoberezhnyj","dvorec-4"], []),
 ("Коптево", ["sleeper","industrial"], ["dvorec-4","dmitrovskij","horoshevskij"], []),
 ("Левобережный", ["river","park"], ["levoberezhnyj","dmitrovskij","dvorec-4"], [("Северный речной вокзал","emb"),("Химкинское водохранилище","emb"),("Парк Дружбы","park")]),
 ("Молжаниновский", ["park","newm"], ["levoberezhnyj","dmitrovskij"], []),
 ("Савёловский", ["sleeper","center"], ["dvorec-4","tverskoj","horoshevskij"], []),
 ("Сокол", ["estate","sleeper"], ["horoshevskij","dvorec-4","tverskoj"], [("Посёлок художников на Соколе","monument")]),
 ("Тимирязевский", ["park","estate"], ["dvorec-4","dmitrovskij","levoberezhnyj"], [("Тимирязевская академия","estate")]),
 ("Ховрино", ["sleeper"], ["levoberezhnyj","dmitrovskij","dvorec-4"], []),
 ("Хорошёвский", ["sleeper","park"], ["horoshevskij","dvorec-4","tverskoj"], [("Ходынское поле","park")]),
])
add("СВАО", [
 ("Алексеевский", ["sleeper"], ["meshchanskij","babushkinskij","dvorec-4"], []),
 ("Алтуфьевский", ["sleeper"], ["medvedkovskij","dmitrovskij","babushkinskij"], []),
 ("Бабушкинский", ["sleeper","park"], ["babushkinskij","medvedkovskij","meshchanskij"], [("Парк Бабушкина","park")]),
 ("Бибирево", ["sleeper","park"], ["medvedkovskij","babushkinskij","dmitrovskij"], []),
 ("Бутырский", ["sleeper"], ["dvorec-4","meshchanskij","babushkinskij"], []),
 ("Лианозово", ["sleeper","park"], ["medvedkovskij","dmitrovskij","babushkinskij"], [("Лианозовский парк","park")]),
 ("Лосиноостровский", ["park"], ["babushkinskij","medvedkovskij","meshchanskij"], [("Национальный парк «Лосиный остров»","park")]),
 ("Марфино", ["sleeper"], ["dvorec-4","meshchanskij","medvedkovskij"], []),
 ("Марьина Роща", ["center","sleeper"], ["dvorec-4","meshchanskij","tverskoj"], []),
 ("Останкинский", ["estate","sleeper"], ["meshchanskij","babushkinskij","dvorec-4"], [("ВДНХ","estate"),("Останкинский дворец-музей","estate"),("Останкинская телебашня","monument")]),
 ("Отрадное", ["sleeper","park"], ["babushkinskij","medvedkovskij","dmitrovskij"], []),
 ("Ростокино", ["sleeper"], ["babushkinskij","meshchanskij","medvedkovskij"], [("Ростокинский акведук","monument")]),
 ("Свиблово", ["sleeper","river"], ["babushkinskij","medvedkovskij","meshchanskij"], []),
 ("Северное", ["sleeper"], ["medvedkovskij","dmitrovskij","babushkinskij"], []),
 ("Северное Медведково", ["sleeper"], ["medvedkovskij","babushkinskij","dmitrovskij"], []),
 ("Южное Медведково", ["sleeper"], ["medvedkovskij","babushkinskij","dmitrovskij"], []),
 ("Ярославский", ["sleeper"], ["babushkinskij","meshchanskij","medvedkovskij"], []),
])
add("ВАО", [
 ("Богородское", ["sleeper","park"], ["bogorodskij","perovskij","izmajlovskij"], [("Национальный парк «Лосиный остров»","park")]),
 ("Вешняки", ["sleeper","estate"], ["perovskij","ryazanskij","bogorodskij"], [("Усадьба Кусково","estate")]),
 ("Восточное Измайлово", ["park"], ["izmajlovskij","dvorec-5","perovskij"], [("Измайловский лесопарк","park")]),
 ("Восточный", ["sleeper"], ["bogorodskij","perovskij","izmajlovskij"], []),
 ("Гольяново", ["sleeper","park"], ["bogorodskij","perovskij","izmajlovskij"], []),
 ("Ивановское", ["sleeper"], ["perovskij","izmajlovskij","bogorodskij"], []),
 ("Измайлово", ["park","estate"], ["dvorec-5","izmajlovskij","perovskij"], [("Измайловский кремль","estate"),("Измайловский парк","park"),("Серебряно-Виноградный пруд","park")]),
 ("Косино-Ухтомский", ["park","newm"], ["perovskij","ryazanskij","bogorodskij"], [("Косинские озёра","park")]),
 ("Метрогородок", ["sleeper","park"], ["bogorodskij","izmajlovskij","perovskij"], []),
 ("Новогиреево", ["sleeper"], ["perovskij","izmajlovskij","ryazanskij"], []),
 ("Новокосино", ["sleeper","newm"], ["perovskij","ryazanskij","lyublinskij"], []),
 ("Перово", ["sleeper","park"], ["perovskij","izmajlovskij","ryazanskij"], [("Перовский парк","park")]),
 ("Преображенское", ["center","park"], ["bogorodskij","izmajlovskij","meshchanskij"], []),
 ("Северное Измайлово", ["park"], ["izmajlovskij","dvorec-5","bogorodskij"], [("Измайловский парк","park")]),
 ("Соколиная Гора", ["sleeper","industrial"], ["izmajlovskij","perovskij","bogorodskij"], []),
 ("Сокольники", ["park","estate"], ["bogorodskij","meshchanskij","izmajlovskij"], [("Парк «Сокольники»","park"),("Храм Воскресения Христова в Сокольниках","temple")]),
])
add("ЮВАО", [
 ("Выхино-Жулебино", ["sleeper"], ["ryazanskij","lyublinskij","dvorec-3"], []),
 ("Капотня", ["industrial","river"], ["lyublinskij","ryazanskij","caricynskij"], []),
 ("Кузьминки", ["park","estate"], ["dvorec-3","ryazanskij","lyublinskij"], [("Усадьба Кузьминки","estate"),("Парк Кузьминки-Люблино","park")]),
 ("Лефортово", ["estate","center"], ["taganskij","izmajlovskij","ryazanskij"], [("Лефортовский парк","park"),("Екатерининский дворец в Лефортове","estate")]),
 ("Люблино", ["park","estate"], ["lyublinskij","dvorec-3","ryazanskij"], [("Усадьба Люблино","estate"),("Люблинские пруды","park")]),
 ("Марьино", ["sleeper","river"], ["lyublinskij","caricynskij","ryazanskij"], [("Марьинский парк","park")]),
 ("Некрасовка", ["newm"], ["lyublinskij","ryazanskij","perovskij"], []),
 ("Нижегородский", ["industrial","sleeper"], ["ryazanskij","taganskij","perovskij"], []),
 ("Печатники", ["industrial","river"], ["lyublinskij","nagatinskij","ryazanskij"], []),
 ("Рязанский", ["sleeper"], ["ryazanskij","dvorec-3","perovskij"], []),
 ("Текстильщики", ["sleeper"], ["dvorec-3","lyublinskij","ryazanskij"], []),
 ("Южнопортовый", ["industrial","river"], ["nagatinskij","taganskij","lyublinskij"], []),
])
add("ЮАО", [
 ("Бирюлёво Восточное", ["sleeper"], ["chertanovskij","caricynskij","nagatinskij"], []),
 ("Бирюлёво Западное", ["sleeper"], ["chertanovskij","caricynskij","nagatinskij"], []),
 ("Братеево", ["river","park"], ["caricynskij","nagatinskij","lyublinskij"], [("Братеевский каскадный парк","park")]),
 ("Даниловский", ["center","estate"], ["nagatinskij","zamoskvoreckij","taganskij"], [("Даниловский монастырь","temple")]),
 ("Донской", ["center","estate"], ["gagarinskij","nagatinskij","zamoskvoreckij"], [("Донской монастырь","temple")]),
 ("Зябликово", ["sleeper"], ["caricynskij","chertanovskij","lyublinskij"], []),
 ("Москворечье-Сабурово", ["river","sleeper"], ["caricynskij","nagatinskij","chertanovskij"], []),
 ("Нагатино-Садовники", ["estate","river"], ["nagatinskij","caricynskij","chertanovskij"], [("Коломенское","estate"),("Церковь Вознесения в Коломенском","temple")]),
 ("Нагатинский Затон", ["river"], ["nagatinskij","caricynskij","chertanovskij"], [("Нагатинская набережная","emb")]),
 ("Нагорный", ["sleeper"], ["chertanovskij","nagatinskij","caricynskij"], []),
 ("Орехово-Борисово Северное", ["sleeper"], ["caricynskij","chertanovskij","nagatinskij"], []),
 ("Орехово-Борисово Южное", ["sleeper","park"], ["caricynskij","chertanovskij","lyublinskij"], [("Борисовские пруды","park")]),
 ("Царицыно", ["estate","park"], ["caricynskij","chertanovskij","nagatinskij"], [("Музей-заповедник «Царицыно»","estate"),("Царицынские пруды","park")]),
 ("Чертаново Северное", ["sleeper"], ["chertanovskij","caricynskij","akademicheskij"], []),
 ("Чертаново Центральное", ["sleeper"], ["chertanovskij","caricynskij","akademicheskij"], []),
 ("Чертаново Южное", ["sleeper"], ["chertanovskij","caricynskij","cheremushkinskij"], []),
])
add("ЮЗАО", [
 ("Академический", ["sleeper","estate"], ["akademicheskij","gagarinskij","cheremushkinskij"], []),
 ("Гагаринский", ["center","sleeper"], ["gagarinskij","akademicheskij","hamovnicheskij"], []),
 ("Зюзино", ["sleeper"], ["akademicheskij","cheremushkinskij","chertanovskij"], []),
 ("Коньково", ["sleeper","park"], ["cheremushkinskij","akademicheskij","chertanovskij"], []),
 ("Котловка", ["sleeper"], ["gagarinskij","nagatinskij","akademicheskij"], []),
 ("Ломоносовский", ["sleeper"], ["gagarinskij","akademicheskij","vernadskij"], []),
 ("Обручевский", ["estate","park"], ["akademicheskij","cheremushkinskij","gagarinskij"], [("Усадьба Воронцово","estate"),("Воронцовский парк","park")]),
 ("Северное Бутово", ["sleeper"], ["cheremushkinskij","chertanovskij","akademicheskij"], []),
 ("Тёплый Стан", ["sleeper","park"], ["cheremushkinskij","akademicheskij","vernadskij"], []),
 ("Черёмушки", ["sleeper"], ["akademicheskij","gagarinskij","cheremushkinskij"], []),
 ("Южное Бутово", ["sleeper","newm"], ["cheremushkinskij","chertanovskij","akademicheskij"], []),
 ("Ясенево", ["sleeper","park"], ["cheremushkinskij","akademicheskij","chertanovskij"], [("Битцевский лес","park")]),
])
add("ЗАО", [
 ("Внуково", ["newm","park"], ["solncevskij","vernadskij","kuncevskij"], []),
 ("Дорогомилово", ["center","city"], ["kutuzovskij","hamovnicheskij","tverskoj"], [("Парк Победы на Поклонной горе","monument"),("Триумфальные ворота на Кутузовском проспекте","monument"),("Бородинская панорама","monument")]),
 ("Крылатское", ["park","river"], ["kuncevskij","kutuzovskij","vernadskij"], [("Гребной канал","emb"),("Крылатские холмы","park")]),
 ("Кунцево", ["sleeper","park"], ["kuncevskij","kutuzovskij","vernadskij"], []),
 ("Можайский", ["sleeper"], ["kuncevskij","vernadskij","kutuzovskij"], []),
 ("Ново-Переделкино", ["sleeper","park"], ["solncevskij","vernadskij","kuncevskij"], []),
 ("Очаково-Матвеевское", ["sleeper"], ["vernadskij","solncevskij","kuncevskij"], []),
 ("Проспект Вернадского", ["sleeper"], ["vernadskij","gagarinskij","kuncevskij"], []),
 ("Раменки", ["estate","park"], ["vernadskij","gagarinskij","kutuzovskij"], [("Смотровая площадка на Воробьёвых горах","emb"),("Главное здание МГУ","estate")]),
 ("Солнцево", ["sleeper"], ["solncevskij","vernadskij","kuncevskij"], []),
 ("Тропарёво-Никулино", ["park","sleeper"], ["vernadskij","gagarinskij","solncevskij"], [("Тропарёвский парк","park")]),
 ("Филёвский Парк", ["river","park"], ["kutuzovskij","kuncevskij","hamovnicheskij"], [("Парк Фили","park"),("Багратионовский мост","emb")]),
 ("Фили-Давыдково", ["park","estate"], ["kutuzovskij","kuncevskij","vernadskij"], [("Церковь Покрова в Филях","temple")]),
])
add("СЗАО", [
 ("Куркино", ["newm","park"], ["tushinskij","horoshevskij"], []),
 ("Митино", ["sleeper","park"], ["tushinskij","horoshevskij"], [("Митинский ландшафтный парк","park")]),
 ("Покровское-Стрешнево", ["park","estate"], ["tushinskij","horoshevskij","dvorec-4"], [("Парк «Покровское-Стрешнево»","park")]),
 ("Северное Тушино", ["sleeper","park"], ["tushinskij","horoshevskij"], [("Парк «Северное Тушино»","park")]),
 ("Строгино", ["river","park"], ["tushinskij","horoshevskij","kuncevskij"], [("Строгинская пойма","emb")]),
 ("Хорошёво-Мнёвники", ["river","park"], ["horoshevskij","tushinskij","kutuzovskij"], [("Серебряный Бор","park"),("Мнёвниковская пойма","emb")]),
 ("Щукино", ["sleeper"], ["horoshevskij","tushinskij"], []),
 ("Южное Тушино", ["sleeper"], ["tushinskij","horoshevskij"], []),
])
add("ЗелАО", [
 ("Матушкино", ["sleeper","park"], ["zelenogradskij"], []),
 ("Савёлки", ["sleeper","park"], ["zelenogradskij"], []),
 ("Старое Крюково", ["sleeper","park"], ["zelenogradskij"], []),
 ("Крюково", ["sleeper","park"], ["zelenogradskij"], [("Школьное озеро","park")]),
 ("Силино", ["sleeper","park"], ["zelenogradskij"], []),
])
# Новая Москва: (название, вид, env, места)
NAO = [
 ("Московский", "город", ["newm","park"], []),
 ("Щербинка", "город", ["newm","sleeper"], []),
 ("Троицк", "город", ["newm","park"], []),
 ("Сосенское", "поселение", ["newm","park"], []),
 ("Десёновское", "поселение", ["newm","park"], []),
 ("Кокошкино", "поселение", ["newm","park"], []),
 ("Марушкинское", "поселение", ["newm","park"], []),
 ("Вороновское", "поселение", ["newm","park"], []),
]

# ---------------------------------------------------------------- Подмосковье
# (город, [env], zags-адрес или None, [(место, тип)])
PODM = [
 ("Балашиха", ["sleeper","park"], "ул. Некрасова, 5", [("Усадьба Пехра-Яковлевское","estate")]),
 ("Химки", ["river","sleeper"], "Московская ул., 30", [("Химкинское водохранилище","emb")]),
 ("Мытищи", ["sleeper","park"], "Лётная ул., 18, корп. 1", []),
 ("Королёв", ["sleeper","park"], "проспект Королёва, 14", []),
 ("Красногорск", ["river","estate"], None, [("Павшинская пойма","emb"),("Усадьба Ильинское-Усово","estate")]),
 ("Одинцово", ["sleeper","estate"], None, [("Усадьба Захарово","estate"),("Усадьба Большие Вязёмы","estate")]),
 ("Подольск", ["estate","sleeper"], None, [("Усадьба Дубровицы","estate"),("Усадьба Ивановское","estate")]),
 ("Люберцы", ["sleeper"], "Октябрьский проспект, 126", []),
 ("Домодедово", ["sleeper","park"], "Каширское шоссе, 42", []),
 ("Раменское", ["sleeper","park"], None, []),
 ("Жуковский", ["sleeper","park"], "ул. Советская, 6", []),
 ("Пушкино", ["park","sleeper"], None, []),
 ("Щёлково", ["sleeper","park"], None, []),
 ("Долгопрудный", ["sleeper","river"], "ул. Циолковского, 32/12", []),
 ("Железнодорожный", ["sleeper","park"], "ул. Юбилейная, 1а", []),
 ("Лобня", ["sleeper","park"], None, []),
 ("Реутов", ["sleeper"], None, []),
 ("Видное", ["sleeper","estate"], None, [("Музей-усадьба «Горки Ленинские»","estate")]),
 ("Дзержинский", ["sleeper","industrial"], "ул. Томилинская, 14а", []),
 ("Ивантеевка", ["sleeper","park"], "ул. Первомайская, 19", []),
 ("Сергиев Посад", ["estate","temple"], None, [("Троице-Сергиева лавра","temple")]),
 ("Дмитров", ["estate","river"], "ул. Семенюка, 9", [("Дмитровский кремль","estate")]),
 ("Коломна", ["estate","river"], None, [("Коломенский кремль","estate")]),
 ("Клин", ["estate","park"], "ул. М. Балакирева, 6/24", [("Музей-усадьба П. И. Чайковского","estate")]),
 ("Звенигород", ["estate","river"], "ул. Ленина, 13", [("Саввино-Сторожевский монастырь","temple")]),
 ("Истра", ["estate","river"], "ул. 9 Гвардейской Дивизии, 36", [("Новоиерусалимский монастырь","temple")]),
 ("Электросталь", ["sleeper","industrial"], None, []),
 ("Ногинск", ["sleeper","estate"], None, []),
 ("Наро-Фоминск", ["sleeper","park"], None, []),
 ("Солнечногорск", ["river","park"], None, [("Озеро Сенеж","emb")]),
 ("Серпухов", ["estate","river"], None, [("Высоцкий монастырь","temple"),("Серпуховский кремль","estate")]),
 ("Руза", ["river","park"], None, [("Рузское водохранилище","emb")]),
 ("Чехов", ["estate","park"], None, [("Музей-заповедник «Мелихово»","estate")]),
]
