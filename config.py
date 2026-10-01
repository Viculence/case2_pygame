"""Настройки правил и интерфейса игры."""

from typing import TypeAlias, TypedDict

Color: TypeAlias = tuple[int, int, int]
EventSpec: TypeAlias = tuple[str, str, str, dict[str, int]]

CLANS: tuple[tuple[str, Color], ...] = (
    ("Ядерный орех", (241, 153, 67)),
    ("Институт прикладного дупла", (100, 166, 238)),
    ("Кедровый консорциум", (115, 205, 147)),
    ("Лаборатория спорных запасов", (192, 143, 227)),
)
START_RESOURCES = {
    "grain": 10,
    "money": 10,
    "land": 5,
    "people": 10,
    "smuta": 0,
}
MIN_RESOURCE = 0
PANIC_DEFEAT = 10
PRESTIGE_VICTORY = 30
LAND_PRESTIGE = 2
MONEY_PRESTIGE_DIVISOR = 5
PEOPLE_PRESTIGE_DIVISOR = 5
TRADE_MONEY = 3
TRADE_GRAIN = 4
POSITIVE_EVENT_PROBABILITY = 0.5

# Семейства случайных событий.
EVENT_FAMILIES: tuple[tuple[EventSpec, EventSpec], ...] = (
    (
        (
            "E1",
            "Репликатор орехов заработал",
            "Положительное",
            {'grain': 5},
        ),
        (
            "E2",
            "Скорлупа достигла критической массы",
            "Отрицательное",
            {'grain': -3, 'land': -1},
        ),
    ),
    (
        (
            "E3",
            "Грант на исследование пустой кормушки",
            "Положительное",
            {'money': 5},
        ),
        (
            "E4",
            "Бюджет закопан вместе с отчётом",
            "Отрицательное",
            {'money': -4, 'smuta': 1},
        ),
    ),
    (
        (
            "E5",
            "Дупло с заначкой",
            "Положительное",
            {'money': 3, 'land': 1},
        ),
        (
            "E6",
            "Люди установили фотоловушку",
            "Отрицательное",
            {'money': -3, 'land': -1},
        ),
    ),
    (
        (
            "E7",
            "Набор в беличью аспирантуру",
            "Положительное",
            {'people': 3},
        ),
        (
            "E8",
            "Экспедиция ушла не в тот лес",
            "Отрицательное",
            {'people': -2, 'smuta': 1},
        ),
    ),
    (
        (
            "E9",
            "Доклад о пользе хруста",
            "Положительное",
            {'money': 3, 'smuta': -1},
        ),
        (
            "E10",
            "Рецензент потребовал переделать лес",
            "Отрицательное",
            {'money': -2, 'smuta': 2},
        ),
    ),
    (
        (
            "E11",
            "Тайник предыдущего завлаба",
            "Положительное",
            {'grain': 5},
        ),
        (
            "E12",
            "Сибирский мороз",
            "Отрицательное",
            {'grain': -4, 'smuta': 1},
        ),
    ),
    (
        (
            "E13",
            "Теория великого дупла признана",
            "Положительное",
            {'land': 1, 'smuta': -2},
        ),
        (
            "E14",
            "Раскол по вопросу формы ореха",
            "Отрицательное",
            {'land': -1, 'smuta': 2},
        ),
    ),
    (
        (
            "E15",
            "Открытая кормушка",
            "Положительное",
            {'grain': 4, 'people': 1},
        ),
        (
            "E16",
            "Встреча со студентами ФЕН",
            "Отрицательное",
            {'people': -3, 'smuta': 2},
        ),
    ),
)

# Тексты карточек, отделенные от числовых эффектов.
EVENT_STORIES: dict[str, str] = {
    "E1": (
        "Впервые за семестр эксперимент дал съедобный результат."
    ),
    "E2": (
        "Просили расколоть орех. Раскололи дупло."
    ),
    "E3": (
        "Актуальность доказана: кормушка действительно пуста."
    ),
    "E4": (
        "Координаты были в отчёте. Отчёт был в бюджете."
    ),
    "E5": (
        "Обнаружены рабочее место, шишкоины и отсутствие прежнего "
        "хозяина."
    ),
    "E6": (
        "Секретный институт больше не секретный. Пришлось срочно "
        "съезжать."
    ),
    "E7": (
        "Трое поступили ради науки. Или ради бесплатных орехов."
    ),
    "E8": (
        "На карте было написано: вы почти у цели."
    ),
    "E9": (
        "После фуршета научное сообщество единогласно поддержало клан."
    ),
    "E10": (
        "Замечание первое: тема раскрыта недостаточно широко."
    ),
    "E11": (
        "Наследие оказалось богаче списка публикаций."
    ),
    "E12": (
        "Склад замёрз. Ответственная белка тоже не отвечает."
    ),
    "E13": (
        "Совет выделил новое дупло и временно прекратил споры."
    ),
    "E14": (
        "Круглые и овальные больше не могут работать вместе."
    ),
    "E15": (
        "Запасов хватило даже на нового сотрудника."
    ),
    "E16": (
        "Научный интерес оказался гастрономическим. Три белки не "
        "вернулись, остальные срочно сменили маршрут."
    ),
}

RESOURCE_NAMES = {
    "grain": "орехи", "money": "шишкоины", "land": "дупла",
    "people": "белки", "smuta": "паника",
}

# Размер окна, частота кадров, мышь.
WIDTH = 1180
HEIGHT = 760
FPS = 30
LEFT_MOUSE_BUTTON = 1
# Цвета интерфейса.
BACKGROUND: Color = (24, 31, 33)
PANEL: Color = (41, 52, 51)
WHITE: Color = (242, 241, 228)
MUTED: Color = (182, 193, 184)
ACCENT: Color = (235, 189, 109)
BUTTON_ACTIVE: Color = (86, 130, 103)
BUTTON_INACTIVE: Color = (68, 75, 73)
# Шрифты.
TITLE_SIZE = 31
TEXT_SIZE = 22
SMALL_SIZE = 18
# Расположение карточек кланов.
PAGE_MARGIN = 28
PANEL_TOP = 104
PANEL_ROW_STEP = 172
PANEL_COLUMN_STEP = 573
PANEL_COLUMNS = 2
# Размеры и содержимое карточек.
PANEL_WIDTH = 550
PANEL_HEIGHT = 154
PANEL_PADDING = 16
PANEL_TEXT_STEP = 30
PANEL_TITLE_OFFSET = 9
PANEL_STATS_TOP = 53
PANEL_BADGE_OFFSET = 430
# Скругления краев, рамки.
CORNER_RADIUS = 12
OUTLINE_WIDTH = 3
BUTTON_RADIUS = 9
# Положение текста и кнопок под карточками.
CURRENT_Y = 465
EVENT_Y = 498
MESSAGE_Y = 526
ACTION_DESCRIPTION_Y = 560
# Размеры кнопок.
PRIMARY_Y = 565
TARGET_Y = 589
CONFIRM_Y = 641
PRIMARY_WIDTH = 215
TARGET_WIDTH = 210
TARGET_STEP = 222
CONFIRM_WIDTH = 300
BUTTON_HEIGHT = 43
TARGET_BUTTON_HEIGHT = 42
# Журнал событий.
LOG_X = 704
LOG_TITLE_Y = 563
LOG_ENTRY_Y = 595
LOG_STEP = 28
LOG_WIDTH = 445
LOG_VISIBLE = 5
# Ограничение названий, положение заголовков.
TARGET_NAME_LENGTH = 14
FONT_FAMILIES = "arial,dejavusans,liberationsans"
TITLE_Y = 18
SUBTITLE_Y = 63


class ActionSpec(TypedDict):
    """Стоимость, условия и полные изменения одного действия."""

    title: str
    subtitle: str
    actor_requirements: dict[str, int]
    target_requirements: dict[str, int]
    actor_changes: dict[str, int]
    target_changes: dict[str, int]


ACTIONS: dict[str, ActionSpec] = {
    "A1": {
        "title": "Торговля",
        "subtitle": "Сделка у кормушки",
        "actor_requirements": {"money": TRADE_MONEY},
        "target_requirements": {"grain": TRADE_GRAIN},
        "actor_changes": {"money": -TRADE_MONEY, "grain": TRADE_GRAIN},
        "target_changes": {"money": TRADE_MONEY, "grain": -TRADE_GRAIN},
    },
    "A2": {
        "title": "Подкуп",
        "subtitle": "Спонсорство чужого научсовета",
        "actor_requirements": {"money": 5},
        "target_requirements": {},
        "actor_changes": {"money": -5, "smuta": 1},
        "target_changes": {"smuta": -2},
    },
    "A3": {
        "title": "Набег",
        "subtitle": "Несогласованный отбор образцов",
        "actor_requirements": {"people": 2},
        "target_requirements": {"grain": 3},
        "actor_changes": {"people": -2, "grain": 3, "smuta": 1},
        "target_changes": {"grain": -3},
    },
    "A4": {
        "title": "Союз",
        "subtitle": "Совместный научный фуршет",
        "actor_requirements": {"grain": 2},
        "target_requirements": {},
        "actor_changes": {"grain": -2, "smuta": -1},
        "target_changes": {"smuta": -1},
    },
    "A5": {
        "title": "Пропаганда",
        "subtitle": "Анонимная рецензия",
        "actor_requirements": {"money": 3, "smuta": 2},
        "target_requirements": {},
        "actor_changes": {"money": -3, "smuta": -2},
        "target_changes": {"smuta": 2},
    },
}