"""Выбор, применение и показ одного случайного события за ход."""

import random

import config
from game.state import (
    Event,
    GameState,
    Phase,
    add_log,
    change_resources,
    check_result,
    format_changes,
    next_player,
)


def choose_event() -> Event:
    """Выбор равновероятного семейства, затем исхода с вероятностью 50%."""
    family = random.choice(config.EVENT_FAMILIES)
    spec = (
        family[0]
        if random.random() < config.POSITIVE_EVENT_PROBABILITY
        else family[1]
    )
    event_id, title, event_type, changes = spec
    return {
        "id": event_id,
        "title": title,
        "type": event_type,
        "changes": changes.copy(),
        "story": config.EVENT_STORIES[event_id],
        "actual_changes": {},
    }


def start_turn(game: GameState) -> None:
    """Применение события текущего клана 1 раз и проверка результата."""
    if game["phase"] != "start":
        return
    if check_result(game):
        return
    player = game["players"][game["current"]]
    if not player["alive"]:
        result_phase: Phase = "result"
        game["phase"] = result_phase
        next_player(game)
        return

    event = choose_event()
    event_phase: Phase = "event"
    game["phase"] = event_phase
    game["selected_action"] = None
    game["selected_target"] = None
    actual = change_resources(player, event["changes"])
    event["actual_changes"] = actual
    game["event"] = event
    game["message"] = format_changes(actual)
    add_log(
        game,
        f"{player['name']}: {event['title']} "
        f"({event['type']}; {format_changes(actual)}).",
    )

    if check_result(game):
        return
    if not player["alive"]:
        result_phase: Phase = "result"
        game["phase"] = result_phase
        next_player(game)


def finish_event(game: GameState) -> None:
    """Закрытие показа события без повторного применения его эффектов."""
    if game["phase"] != "event":
        return
    if check_result(game):
        return
    action_phase: Phase = "action"
    game["phase"] = action_phase
    game["message"] = "Выберите действие."