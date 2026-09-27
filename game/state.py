"""Данные партии и проверка условий завершения."""

from typing import Literal, TypedDict

import config


class Player(TypedDict):
    """Состояние одного клана."""

    name: str
    color: config.Color
    resources: dict[str, int]
    alive: bool


class Event(TypedDict):
    """Случайное событие и его эффект."""

    id: str
    title: str
    type: str
    changes: dict[str, int]


Phase = Literal["start", "action", "result", "game_over"]


class GameState(TypedDict):
    """Все изменяемые данные одной партии."""

    players: list[Player]
    current: int
    phase: Phase
    event: Event | None
    selected_target: int | None
    winner: str | None
    message: str
    log: list[str]


def new_game() -> GameState:
    """Создать независимое состояние новой партии."""
    return {
        "players": [
            {
                "name": name,
                "color": color,
                "resources": config.START_RESOURCES.copy(),
                "alive": True,
            }
            for name, color in config.CLANS
        ],
        "current": 0,
        "phase": "start",
        "event": None,
        "selected_target": None,
        "winner": None,
        "message": "Игрок 1: нажмите «Начать ход».",
        "log": [],
    }


def prestige(player: Player) -> int:
    """Расчет престижа по текущим ресурсам клана."""
    resources = player["resources"]
    return (
        resources["land"] * config.LAND_PRESTIGE
        + resources["money"] // config.MONEY_PRESTIGE_DIVISOR
        + resources["people"] // config.PEOPLE_PRESTIGE_DIVISOR
        - resources["smuta"]
    )


def change_resources(
    player: Player, changes: dict[str, int]
) -> dict[str, int]:
    """Применение изменения события и возвращение фактических изменений."""
    actual: dict[str, int] = {}
    for resource, amount in changes.items():
        old_value = player["resources"][resource]
        new_value = max(config.MIN_RESOURCE, old_value + amount)
        player["resources"][resource] = new_value
        actual[resource] = new_value - old_value
    return actual


def add_log(game: GameState, message: str) -> None:
    """Запись сообщения в историю партии."""
    game["log"].append(message)


def check_result(game: GameState) -> bool:
    """Проверка поражения раньше победы после полного эффекта хода."""
    for player in game["players"]:
        resources = player["resources"]
        if player["alive"] and (
            resources["smuta"] >= config.PANIC_DEFEAT
            or resources["people"] <= config.MIN_RESOURCE
        ):
            player["alive"] = False
            add_log(game, f"{player['name']} выбыл!")

    alive = [player for player in game["players"] if player["alive"]]
    if not alive:
        game["winner"] = "Ничья: все кланы выбыли."
    elif len(alive) == 1:
        game["winner"] = f"Победил клан «{alive[0]['name']}»!"
    else:
        candidates = [
            player for player in alive
            if prestige(player) >= config.PRESTIGE_VICTORY
        ]
        if candidates:
            maximum = max(prestige(player) for player in candidates)
            leaders = [
                player for player in candidates
                if prestige(player) == maximum
            ]
            game["winner"] = (
                f"Победил клан «{leaders[0]['name']}»!"
                if len(leaders) == 1
                else "Ничья: лидеры набрали одинаковый престиж."
            )

    if game["winner"] is not None:
        finished_phase: Phase = "game_over"
        game["phase"] = finished_phase
        game["message"] = game["winner"]
        add_log(game, game["winner"])
        return True
    return False


def next_player(game: GameState) -> None:
    """Передача хода следующему действующему клану."""
    for step in range(1, len(game["players"]) + 1):
        index = (game["current"] + step) % len(game["players"])
        if game["players"][index]["alive"]:
            game["current"] = index
            start_phase: Phase = "start"
            game["phase"] = start_phase
            game["event"] = None
            game["selected_target"] = None
            game["message"] = f"Игрок {index + 1}: нажмите «Начать ход»."
            return