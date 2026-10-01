"""Переходы между стадиями игры по командам игрока."""

import config
from game.actions import (
    action_reason,
    available_targets,
    execute_action,
    skip_action,
    target_reason,
)
from game.events import finish_event, start_turn
from game.state import GameState, Phase, new_game, next_player


def select_action(game: GameState, action_id: str) -> None:
    """Выбор допустимого действия без списания ресурсов."""
    reason = action_reason(game, action_id)
    if reason is not None:
        game["message"] = reason
        return
    if not available_targets(game, action_id):
        game["message"] = "Для этого действия нет допустимых целей."
        return
    game["selected_action"] = action_id
    game["selected_target"] = None
    target_phase: Phase = "target"
    game["phase"] = target_phase
    game["message"] = (
        f"{config.ACTIONS[action_id]['title']}: выберите цель."
    )


def select_target(game: GameState, value: str) -> None:
    """Выбрать цель, проверив формат индекса и доступность клана."""
    try:
        target_index = int(value)
    except ValueError:
        game["message"] = "Некорректный номер цели."
        return
    action_id = game["selected_action"]
    if action_id is None:
        game["message"] = "Сначала выберите действие."
        return
    reason = target_reason(game, action_id, target_index)
    if reason is not None:
        game["message"] = reason
        return
    game["selected_target"] = target_index
    target = game["players"][target_index]
    game["message"] = (
        f"Цель: {target['name']}. Подтвердите действие."
    )


def handle_command(game: GameState, command: str) -> GameState:
    """Обработка допустимой команды (вернуть состояние партии)."""
    phase = game["phase"]
    if phase == "game_over":
        return new_game() if command == "restart" else game

    if command == "start" and phase == "start":
        start_turn(game)
    elif command == "continue" and phase == "event":
        finish_event(game)
    elif command.startswith("action:") and phase in ("action", "target"):
        action_id = command.split(":", maxsplit=1)[1]
        select_action(game, action_id)
    elif command.startswith("target:") and phase == "target":
        value = command.split(":", maxsplit=1)[1]
        select_target(game, value)
    elif command == "back" and phase == "target":
        game["selected_action"] = None
        game["selected_target"] = None
        action_phase: Phase = "action"
        game["phase"] = action_phase
        game["message"] = "Выберите действие."
    elif command == "confirm" and phase == "target":
        action_id = game["selected_action"]
        target_index = game["selected_target"]
        if action_id is None or target_index is None:
            game["message"] = "Выберите действие и цель."
        else:
            execute_action(game, action_id, target_index)
    elif command == "skip" and phase in ("action", "target"):
        skip_action(game)
    elif command == "next" and phase == "result":
        next_player(game)
    return game