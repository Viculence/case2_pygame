"""Данные партии и проверка условий завершения."""

from typing import Literal, TypedDict

import config


class Player(TypedDict):
    """Состояние одного клана."""

    name: str
    color: config.Color
    resources: dict[str, int]
    alive: bool


class EventDetails(TypedDict, total=False):
    """Дополнительные данные для карточки события."""

    story: str
    actual_changes: dict[str, int]


class Event(EventDetails):
    """Случайное событие и его эффект."""

    id: str
    title: str
    type: str
    changes: dict[str, int]


Phase = Literal["start", "event", "action", "target", "result", "game_over"]


class GameState(TypedDict):
    """Все изменяемые данные одной партии."""

    players: list[Player]
    current: int
    phase: Phase
    event: Event | None
    selected_action: str | None
    selected_target: int | None
    winner: str | None
    message: str
    log: list[str]


def new_game() -> GameState:
    """Создание независимого состояния новой партии."""
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
        "selected_action": None,
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
    """Применение изменений и возвращение фактической разницы ресурсов."""
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


def format_changes(changes: dict[str, int]) -> str:
    """Описание фактических изменений ресурсов для сообщения журнала."""
    if not changes:
        return "ресурсы без изменений"
    return ", ".join(
        f"{config.RESOURCE_NAMES[key]}: {amount:+d}"
        for key, amount in changes.items()
    )


def check_result(game: GameState) -> bool:
    """Проверка выбывания каждого клана, определение результата."""
    if game["phase"] == "game_over":
        return True

    for player in game["players"]:
        resources = player["resources"]
        if not player["alive"]:
            continue
        reasons: list[str] = []
        if resources["smuta"] >= config.PANIC_DEFEAT:
            reasons.append(
                f"паника {resources['smuta']} >= {config.PANIC_DEFEAT}"
            )
        if resources["people"] <= config.MIN_RESOURCE:
            reasons.append("не осталось белок")
        if reasons:
            player["alive"] = False
            reason = "; ".join(reasons)
            add_log(game, f"{player['name']} выбыл: {reason}.")

    result: str | None = None
    alive = [player for player in game["players"] if player["alive"]]
    if not alive:
        result = "Ничья: все кланы выбыли."
    elif len(alive) == 1:
        result = (
            f"Победил клан «{alive[0]['name']}»: "
            "остался единственным действующим кланом."
        )
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
            result = (
                f"Победил клан «{leaders[0]['name']}»: "
                f"престиж {maximum} >= {config.PRESTIGE_VICTORY}."
                if len(leaders) == 1
                else (
                    "Ничья: несколько кланов достигли порога победы "
                    f"с одинаковым максимальным престижем {maximum}."
                )
            )

    if result is not None:
        game["winner"] = result
        finished_phase: Phase = "game_over"
        game["phase"] = finished_phase
        game["selected_action"] = None
        game["selected_target"] = None
        game["message"] = result
        add_log(game, result)
        return True
    return False


def next_player(game: GameState) -> None:
    """Передача завершённого хода без запуска события следующего клана."""
    if game["phase"] != "result":
        return
    if check_result(game):
        return
    for step in range(1, len(game["players"]) + 1):
        index = (game["current"] + step) % len(game["players"])
        if game["players"][index]["alive"]:
            game["current"] = index
            start_phase: Phase = "start"
            game["phase"] = start_phase
            game["event"] = None
            game["selected_action"] = None
            game["selected_target"] = None
            game["message"] = f"Игрок {index + 1}: нажмите «Начать ход»."
            return