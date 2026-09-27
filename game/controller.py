"""Реакции игры на команды игрока."""

from game.actions import available_targets, trade
from game.events import start_turn
from game.state import GameState, Phase, new_game, next_player


def handle_command(game: GameState, command: str) -> GameState:
    """Применение команды и возвращение состояния партии."""
    phase = game["phase"]
    if command == "start" and phase == "start":
        start_turn(game)
    elif command.startswith("target:") and phase == "action":
        target = int(command.split(":", maxsplit=1)[1])
        if target in available_targets(game):
            game["selected_target"] = target
    elif command == "confirm" and phase == "action":
        target = game["selected_target"]
        if target is not None:
            trade(game, target)
    elif command == "skip" and phase == "action":
        if not available_targets(game):
            result_phase: Phase = "result"
            game["phase"] = result_phase
            game["message"] = "Доступных целей нет, действие пропущено."
    elif command == "next" and phase == "result":
        next_player(game)
    elif command == "restart" and phase == "game_over":
        return new_game()
    return game