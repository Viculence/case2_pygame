from game.state import (
    new_game,
    prestige,
    change_resources,
    next_player,
)

from game.actions import (
    available_targets,
    trade,
)


def test_new_game_initial_state():
    game = new_game()

    assert len(game["players"]) == 4
    assert game["current"] == 0
    assert game["phase"] == "start"
    assert game["event"] is None
    assert game["selected_target"] is None
    assert game["winner"] is None


def test_new_game_initial_resources():
    game = new_game()

    for player in game["players"]:
        assert player["resources"]["grain"] == 10
        assert player["resources"]["money"] == 10
        assert player["resources"]["land"] == 5
        assert player["resources"]["people"] == 10
        assert player["resources"]["smuta"] == 0


def test_prestige():
    game = new_game()
    player = game["players"][0]

    assert prestige(player) == 14


def test_resources_cannot_go_below_zero():
    game = new_game()
    player = game["players"][0]

    change_resources(
        player,
        {
            "grain": -100,
            "money": -100,
            "land": -100,
            "people": -100,
            "smuta": -100,
        },
    )

    assert player["resources"]["grain"] == 0
    assert player["resources"]["money"] == 0
    assert player["resources"]["land"] == 0
    assert player["resources"]["people"] == 0
    assert player["resources"]["smuta"] == 0


def test_next_player():
    game = new_game()

    game["current"] = 0
    game["phase"] = "result"

    next_player(game)

    assert game["current"] == 1
    assert game["phase"] == "start"


def test_trade():
    game = new_game()

    game["phase"] = "action"
    game["current"] = 0

    trade(game, 1)

    assert game["players"][0]["resources"]["money"] == 7
    assert game["players"][0]["resources"]["grain"] == 14

    assert game["players"][1]["resources"]["money"] == 13
    assert game["players"][1]["resources"]["grain"] == 6


def test_trade_unavailable_without_money():
    game = new_game()

    game["phase"] = "action"
    game["current"] = 0

    game["players"][0]["resources"]["money"] = 2

    targets = available_targets(game)

    assert targets == []


def test_trade_unavailable_without_target_grain():
    game = new_game()

    game["phase"] = "action"
    game["current"] = 0

    game["players"][1]["resources"]["grain"] = 3

    targets = available_targets(game)

    assert 1 not in targets