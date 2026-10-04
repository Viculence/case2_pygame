"""Отрисовка только игрового экрана и интерактивных областей."""

import pygame

import config
from game.state import GameState

Controls = list[tuple[str, pygame.Rect]]
Fonts = tuple[pygame.font.Font, pygame.font.Font, pygame.font.Font]


def write(
    screen: pygame.Surface,
    font: pygame.font.Font,
    value: str,
    x: int,
    y: int,
    color: config.Color = config.WHITE,
    max_width: int | None = None,
) -> None:
    """Нарисовать текст, обрезав длинную строку по ширине."""
    if (
        max_width is not None
        and font.render(value, True, color).get_width() > max_width
    ):
        while (
            value
            and font.render(f"{value}…", True, color).get_width() > max_width
        ):
            value = value[:-1]
        value += "…"
    screen.blit(font.render(value, True, color), (x, y))


def button(
    screen: pygame.Surface,
    font: pygame.font.Font,
    label: str,
    rect: pygame.Rect,
    enabled: bool = True,
    selected: bool = False,
) -> pygame.Rect:
    """Нарисовать кнопку и вернуть её область клика."""
    color = (
        config.ACCENT if selected
        else config.BUTTON_ACTIVE if enabled
        else config.BUTTON_INACTIVE
    )
    pygame.draw.rect(screen, color, rect, border_radius=config.BUTTON_RADIUS)
    text_color = (
        config.BACKGROUND if selected
        else config.WHITE if enabled
        else config.MUTED
    )
    text_surface = font.render(label, True, text_color)
    screen.blit(text_surface, text_surface.get_rect(center=rect.center))
    return rect


def draw_players(
    screen: pygame.Surface, game: GameState, scores: list[int], fonts: Fonts
) -> None:
    """Нарисовать панели всех кланов."""
    _, text_font, small_font = fonts
    for index, player in enumerate(game["players"]):
        x = config.PAGE_MARGIN + (index % config.PANEL_COLUMNS) * (
            config.PANEL_COLUMN_STEP
        )
        y = config.PANEL_TOP + (index // config.PANEL_COLUMNS) * (
            config.PANEL_ROW_STEP
        )
        rect = pygame.Rect(x, y, config.PANEL_WIDTH, config.PANEL_HEIGHT)
        pygame.draw.rect(screen, config.PANEL, rect,
                         border_radius=config.CORNER_RADIUS)
        outline = (
            config.ACCENT if index == game["current"] else player["color"]
        )
        outline_width = 4 if index == game["current"] else config.OUTLINE_WIDTH
        pygame.draw.rect(screen, outline, rect,
                         width=outline_width,
                         border_radius=config.CORNER_RADIUS)

        name_color = player["color"] if player["alive"] else config.MUTED
        write(screen, text_font, f"{index + 1}. {player['name']}",
              x + config.PANEL_PADDING, y + config.PANEL_TITLE_OFFSET,
              name_color)

        if not player["alive"]:
            write(screen, small_font, "ВЫБЫЛ",
                  x + config.PANEL_BADGE_OFFSET,
                  y + config.PANEL_TITLE_OFFSET, config.ACCENT)

        res = player["resources"]
        icons = ("🌰", "🌲", "🕳️", "🐿️", "❗", "🏆")
        labels = ("Орехи", "Шишки", "Дуппа", "Белки", "Паника", "Престиж")
        values = (
            res["grain"], res["money"], res["land"],
            res["people"], res["smuta"], scores[index],
        )

        icon_font = pygame.font.SysFont("segoeuiemoji", 22)
        cell_width = (config.PANEL_WIDTH - config.PANEL_PADDING * 2) // 6

        for i, (icon, label, value) in enumerate(zip(icons, labels, values)):
            cx = x + config.PANEL_PADDING + i * cell_width + cell_width // 2
            icon_surface = icon_font.render(icon, True, config.WHITE)
            screen.blit(icon_surface,
                        icon_surface.get_rect(center=(cx, y + 78)))
            value_surface = small_font.render(str(value), True, config.WHITE)
            screen.blit(value_surface,
                        value_surface.get_rect(center=(cx, y + 105)))
            label_surface = small_font.render(label, True, config.MUTED)
            screen.blit(label_surface,
                        label_surface.get_rect(center=(cx, y + 128)))


def draw_controls(
    screen: pygame.Surface,
    game: GameState,
    targets: list[int],
    fonts: Fonts,
) -> Controls:
    """Нарисовать элементы управления и вернуть их области клика."""
    _, text_font, small_font = fonts
    controls: Controls = []
    phase = game["phase"]
    if phase == "start":
        controls.append((
            "start",
            button(screen, text_font, "Начать ход", pygame.Rect(
                config.PAGE_MARGIN, config.PRIMARY_Y,
                config.PRIMARY_WIDTH, config.BUTTON_HEIGHT,
            )),
        ))
    elif phase == "event":
        controls.append((
            "continue",
            button(screen, text_font, "К действиям", pygame.Rect(
                config.PAGE_MARGIN, config.PRIMARY_Y,
                config.PRIMARY_WIDTH, config.BUTTON_HEIGHT,
            )),
        ))
    elif phase == "action":
        write(screen, small_font,
              "Выберите действие:",
              config.PAGE_MARGIN, config.ACTION_DESCRIPTION_Y)
        position = 0
        action_step = 130
        action_width = 122
        for action_id, action in config.ACTIONS.items():
            rect = pygame.Rect(
                config.PAGE_MARGIN + position * action_step,
                config.TARGET_Y,
                action_width,
                config.TARGET_BUTTON_HEIGHT,
            )
            controls.append((
                f"action:{action_id}",
                button(screen, small_font, action["title"], rect),
            ))
            position += 1
    elif phase == "target":
        action_id = game["selected_action"]
        if action_id:
            action_title = config.ACTIONS[action_id]["title"]
            write(screen, small_font,
                  f"{action_title}: выберите цель.",
                  config.PAGE_MARGIN, config.ACTION_DESCRIPTION_Y)
        position = 0
        for index, player in enumerate(game["players"]):
            if index == game["current"]:
                continue
            rect = pygame.Rect(
                config.PAGE_MARGIN + position * config.TARGET_STEP,
                config.TARGET_Y,
                config.TARGET_WIDTH,
                config.TARGET_BUTTON_HEIGHT,
            )
            short_name = player["name"][:config.TARGET_NAME_LENGTH]
            label = f"{index + 1}. {short_name}"
            controls.append((
                f"target:{index}",
                button(screen, small_font, label, rect,
                       player["alive"],
                       game["selected_target"] == index),
            ))
            position += 1
        controls.append((
            "back",
            button(screen, small_font, "Назад",
                   pygame.Rect(config.PAGE_MARGIN, config.CONFIRM_Y,
                               config.CONFIRM_WIDTH // 2 - 5,
                               config.TARGET_BUTTON_HEIGHT)),
        ))
        controls.append((
            "confirm",
            button(screen, small_font, "Подтвердить",
                   pygame.Rect(
                       config.PAGE_MARGIN + config.CONFIRM_WIDTH // 2 + 5,
                       config.CONFIRM_Y,
                       config.CONFIRM_WIDTH // 2 - 5,
                       config.TARGET_BUTTON_HEIGHT),
                   game["selected_target"] is not None),
        ))
    elif phase == "result":
        controls.append((
            "next",
            button(screen, text_font, "Передать ход", pygame.Rect(
                config.PAGE_MARGIN, config.PRIMARY_Y,
                config.PRIMARY_WIDTH, config.BUTTON_HEIGHT,
            )),
        ))
    else:
        controls.append((
            "restart",
            button(screen, text_font, "Новая игра", pygame.Rect(
                config.PAGE_MARGIN, config.PRIMARY_Y,
                config.PRIMARY_WIDTH, config.BUTTON_HEIGHT,
            )),
        ))
    return controls


def draw(
    screen: pygame.Surface,
    game: GameState,
    targets: list[int],
    scores: list[int],
    fonts: Fonts,
) -> Controls:
    """Нарисовать кадр, где игровое состояние не изменяется."""
    title_font, text_font, small_font = fonts
    screen.fill(config.BACKGROUND)
    write(screen, title_font, "Академгородок: белки захватили науку",
          config.PAGE_MARGIN, config.TITLE_Y)
    write(screen, small_font,
          "Прототип: событие → торговля → следующий клан",
          config.PAGE_MARGIN, config.SUBTITLE_Y, config.MUTED)
    draw_players(screen, game, scores, fonts)
    phase_names = {
        "start": "Начало хода",
        "event": "Событие",
        "action": "Выбор цели",
        "target": "Выбор цели",
        "result": "Итог хода",
        "game_over": "Конец партии",
    }
    write(screen, text_font,
          f"Игрок {game['current'] + 1} · {phase_names[game['phase']]}",
          config.PAGE_MARGIN, config.CURRENT_Y)
    if game["event"] is not None:
        event = game["event"]
        write(screen, small_font,
              f"Событие: {event['title']}",
              config.PAGE_MARGIN, config.EVENT_Y)
    write(screen, small_font, game["message"],
          config.PAGE_MARGIN, config.MESSAGE_Y, config.ACCENT,
          config.WIDTH - config.PAGE_MARGIN * config.PANEL_COLUMNS)

    controls = draw_controls(screen, game, targets, fonts)
    write(screen, small_font, "ЖУРНАЛ (последние пять записей)",
          config.LOG_X, config.LOG_TITLE_Y, config.MUTED)
    for row, entry in enumerate(game["log"][-config.LOG_VISIBLE:]):
        y = config.LOG_ENTRY_Y + row * config.LOG_STEP
        marker_color = config.MUTED
        clan_names = [clan[0] for clan in config.CLANS]
        for i, clan_name in enumerate(clan_names):
            if clan_name in entry:
                marker_color = config.CLANS[i][1]
                break
        pygame.draw.circle(screen, marker_color, (config.LOG_X - 14, y + 9), 5)
        write(screen, small_font, entry,
              config.LOG_X, y,
              max_width=config.LOG_WIDTH)
    pygame.display.flip()
    return controls