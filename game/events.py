"""Выбор и применение случайного события."""

import random

import config
from game.state import (
    Event,
    GameState,
    add_log,
    Phase,
    change_resources,
    check_result,
)


def start_turn(game: GameState) -> None:
    """Ровно один раз разыграть событие текущего хода."""
    if game["phase"] != "start":
        return

    family = random.choice(config.EVENT_FAMILIES)
    spec = (
        family[0]
        if random.random() < config.POSITIVE_EVENT_PROBABILITY
        else family[1]
    )
    event: Event = {
        "id": spec[0],
        "title": spec[1],
        "type": spec[2],
        "changes": spec[3],
    }
    player = game["players"][game["current"]]
    actual = change_resources(player, event["changes"])
    effects = ", ".join(
        f"{config.RESOURCE_NAMES[key]}: {amount:+d}"
        for key, amount in actual.items()
    )
    game["event"] = event
    game["message"] = f"{event['title']} ({effects})"
    add_log(game, f"{player['name']}: {game['message']}")
    if not check_result(game):
        if player["alive"]:
            next_phase: Phase = "action"
        else:
            next_phase: Phase = "result"
            game["message"] = "Ваш клад выбыл. Передайте ход."

        game["phase"] = next_phase