"""Доступность и применение торговли между кланами."""

import config
from game.state import GameState, Phase, add_log, check_result


def available_targets(game: GameState) -> list[int]:
    """Возвращение номеров кланов, с которыми можно торговать."""
    if game["phase"] != "action":
        return []

    actor = game["players"][game["current"]]
    if actor["resources"]["money"] < config.TRADE_MONEY:
        return []

    return [
        index for index, player in enumerate(game["players"])
        if index != game["current"]
        and player["alive"]
        and player["resources"]["grain"] >= config.TRADE_GRAIN
    ]


def trade(game: GameState, target_index: int) -> bool:
    """Передача шишкоинов цели в обмен на её орехи."""
    if target_index not in available_targets(game):
        game["message"] = "Торговля недоступна: проверьте ресурсы цели."
        return False

    actor = game["players"][game["current"]]
    target = game["players"][target_index]
    actor["resources"]["money"] -= config.TRADE_MONEY
    target["resources"]["money"] += config.TRADE_MONEY
    target["resources"]["grain"] -= config.TRADE_GRAIN
    actor["resources"]["grain"] += config.TRADE_GRAIN

    game["message"] = (
        f"Торговля: {actor['name']} получил "
        f"{config.TRADE_GRAIN} ореха от «{target['name']}»."
    )
    add_log(game, game["message"])
    if not check_result(game):
        result_phase: Phase = "result"
        game["phase"] = result_phase
    return True