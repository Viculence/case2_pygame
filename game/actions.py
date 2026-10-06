"""Проверка доступности и выполнение пяти действий между кланами."""

import config
from game.state import (
    GameState,
    Phase,
    Player,
    add_log,
    change_resources,
    check_result,
    format_changes,
    next_player,
)


def resource_reason(
    player: Player, requirements: dict[str, int]
) -> str | None:
    """Вернуть причину нехватки ресурсов или None, если их достаточно."""
    missing = [
        f"{config.RESOURCE_NAMES[key]}: нужно {minimum}, "
        f"есть {player['resources'][key]}"
        for key, minimum in requirements.items()
        if player["resources"][key] < minimum
    ]
    return "; ".join(missing) if missing else None


def action_reason(game: GameState, action_id: str) -> str | None:
    """Проверить стадию, действие и ресурсы инициатора."""
    if game["phase"] == "game_over":
        return "Партия завершена."
    if game["phase"] not in ("action", "target"):
        return "Сейчас нельзя выполнять действие."
    if action_id not in config.ACTIONS:
        return "Неизвестное действие."
    actor = game["players"][game["current"]]
    if not actor["alive"]:
        return "Ваш клан выбыл."
    requirements = config.ACTIONS[action_id]["actor_requirements"]
    reason = resource_reason(actor, requirements)
    return f"Недостаточно ресурсов: {reason}." if reason else None


def target_reason(
    game: GameState, action_id: str, target_index: int
) -> str | None:
    """Проверить действие и цель; вернуть объяснение запрета."""
    reason = action_reason(game, action_id)
    if reason is not None:
        return reason
    if not 0 <= target_index < len(game["players"]):
        return "Такого клана нет."
    if target_index == game["current"]:
        return "Нельзя выбрать свой клан."
    target = game["players"][target_index]
    if not target["alive"]:
        return "Этот клан выбыл."
    requirements = config.ACTIONS[action_id]["target_requirements"]
    reason = resource_reason(target, requirements)
    return f"У цели недостаточно ресурсов: {reason}." if reason else None


def available_targets(
    game: GameState, action_id: str | None = None
) -> list[int]:
    """Вернуть индексы допустимых целей выбранного действия."""
    selected = action_id or game["selected_action"] or "A1"
    return [
        index for index in range(len(game["players"]))
        if target_reason(game, selected, index) is None
    ]


def available_actions(game: GameState) -> list[str]:
    """Вернуть действия, для которых есть хотя бы одна допустимая цель."""
    return [
        action_id for action_id in config.ACTIONS
        if available_targets(game, action_id)
    ]


def has_legal_action(game: GameState) -> bool:
    """Проверить наличие любой допустимой пары: действие + цель."""
    return bool(available_actions(game))


def execute_action(
    game: GameState, action_id: str, target_index: int
) -> bool:
    """Применить все эффекты один раз, записать их и проверить результат."""
    if game["phase"] == "game_over":
        return False
    reason = target_reason(game, action_id, target_index)
    if reason is not None:
        game["message"] = reason
        return False

    spec = config.ACTIONS[action_id]
    actor = game["players"][game["current"]]
    target = game["players"][target_index]
    actor_changes = change_resources(actor, spec["actor_changes"])
    target_changes = change_resources(target, spec["target_changes"])
    record = (
        f"{spec['title']}: {actor['name']} → {target['name']}. "
        f"Инициатор: {format_changes(actor_changes)}. "
        f"Цель: {format_changes(target_changes)}."
    )
    add_log(game, record)
    game["message"] = record
    game["selected_action"] = None
    game["selected_target"] = None
    if not check_result(game):
        result_phase: Phase = "result"
        game["phase"] = result_phase
    return True


def skip_action(game: GameState) -> bool:
    """Пропустить действие только при отсутствии всех допустимых пар."""
    if game["phase"] not in ("action", "target"):
        return False
    if has_legal_action(game):
        game["message"] = "Пропуск недоступен: есть допустимое действие."
        return False
    actor = game["players"][game["current"]]
    if not actor["alive"]:
        return False
    message = (
        f"{actor['name']}: вынужденный пропуск — "
        "нет допустимой пары «действие + цель»."
    )
    game["message"] = message
    add_log(game, message)
    result_phase: Phase = "result"
    game["phase"] = result_phase
    next_player(game)
    return True


def trade(game: GameState, target_index: int) -> bool:
    """Передать цели шишкоины в обмен на её орехи."""
    return execute_action(game, "A1", target_index)


def bribe(game: GameState, target_index: int) -> bool:
    """Снизить панику цели, потратив деньги и повысив свою панику."""
    return execute_action(game, "A2", target_index)


def raid(game: GameState, target_index: int) -> bool:
    """Забрать орехи цели, потеряв белок и повысив свою панику."""
    return execute_action(game, "A3", target_index)


def alliance(game: GameState, target_index: int) -> bool:
    """Потратить орехи на снижение паники обоих кланов."""
    return execute_action(game, "A4", target_index)


def propaganda(game: GameState, target_index: int) -> bool:
    """Потратить деньги, снизить свою панику и повысить панику цели."""
    return execute_action(game, "A5", target_index)