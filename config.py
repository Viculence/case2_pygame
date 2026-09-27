"""Настройки правил и интерфейса игры."""

from typing import TypeAlias

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

EVENT_FAMILIES: tuple[tuple[EventSpec, EventSpec], ...] = (
    (
        ("E1", "Репликатор орехов заработал", "Положительное",
         {"grain": 5}),
        ("E2", "Скорлупа достигла критической массы", "Отрицательное",
         {"grain": -3, "land": -1}),
    ),
    (
        ("E3", "Грант на исследование пустой кормушки",
         "Положительное", {"money": 5}),
        ("E4", "Бюджет закопан вместе с отчётом", "Отрицательное",
         {"money": -4, "smuta": 1}),
    ),
)
RESOURCE_NAMES = {
    "grain": "орехи", "money": "шишкоины", "land": "дупла",
    "people": "белки", "smuta": "паника",
}

WIDTH = 1180
HEIGHT = 760
FPS = 30
LEFT_MOUSE_BUTTON = 1
BACKGROUND: Color = (24, 31, 33)
PANEL: Color = (41, 52, 51)
WHITE: Color = (242, 241, 228)
MUTED: Color = (182, 193, 184)
ACCENT: Color = (235, 189, 109)
BUTTON_ACTIVE: Color = (86, 130, 103)
BUTTON_INACTIVE: Color = (68, 75, 73)
TITLE_SIZE = 31
TEXT_SIZE = 22
SMALL_SIZE = 18
PAGE_MARGIN = 28
PANEL_TOP = 104
PANEL_ROW_STEP = 172
PANEL_COLUMN_STEP = 573
PANEL_COLUMNS = 2
PANEL_WIDTH = 550
PANEL_HEIGHT = 154
PANEL_PADDING = 16
PANEL_TEXT_STEP = 30
PANEL_TITLE_OFFSET = 9
PANEL_STATS_TOP = 53
PANEL_BADGE_OFFSET = 430
CORNER_RADIUS = 12
OUTLINE_WIDTH = 3
BUTTON_RADIUS = 9
CURRENT_Y = 465
EVENT_Y = 498
MESSAGE_Y = 526
ACTION_DESCRIPTION_Y = 560
PRIMARY_Y = 565
TARGET_Y = 589
CONFIRM_Y = 641
PRIMARY_WIDTH = 215
TARGET_WIDTH = 210
TARGET_STEP = 222
CONFIRM_WIDTH = 300
BUTTON_HEIGHT = 43
TARGET_BUTTON_HEIGHT = 42
LOG_X = 704
LOG_TITLE_Y = 563
LOG_ENTRY_Y = 595
LOG_STEP = 28
LOG_WIDTH = 445
LOG_VISIBLE = 5
TARGET_NAME_LENGTH = 14
FONT_FAMILIES = "arial,dejavusans,liberationsans"
TITLE_Y = 18
SUBTITLE_Y = 63