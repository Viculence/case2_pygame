from game.state import (
    new_game,
    prestige,
    change_resources,
    next_player,
    check_result,
)

from game.actions import (
    available_targets,
    action_reason,
    target_reason,
    execute_action,
    skip_action,
    trade,
)

from game.events import (
    choose_event,
    start_turn,
    finish_event,
)


# T1 — Начальное состояние

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


# T2 — Престиж

def test_prestige():
    game = new_game()
    player = game["players"][0]

    assert prestige(player) == 14


# T3 — Поражение по панике

def test_panic_defeat_boundary():
    for smuta, should_be_alive in [
        (9, True),
        (10, False),
        (11, False),
    ]:
        game = new_game()
        player = game["players"][0]

        player["resources"]["smuta"] = smuta

        check_result(game)

        assert player["alive"] is should_be_alive


# T4 — Поражение при отсутствии белок

def test_people_defeat_boundary():
    for people, should_be_alive in [
        (1, True),
        (0, False),
    ]:
        game = new_game()
        player = game["players"][0]

        player["resources"]["people"] = people

        check_result(game)

        assert player["alive"] is should_be_alive


# T5 — Ресурсы не могут стать отрицательными

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


# T6 — Стоимость действия и проверка ресурсов

def test_action_requirements():
    game = new_game()

    game["phase"] = "action"
    game["current"] = 0

    # Достаточно ресурсов для торговли
    assert action_reason(game, "A1") is None

    # Недостаточно денег у инициатора
    game["players"][0]["resources"]["money"] = 2

    assert action_reason(game, "A1") is not None

    # Возвращаем деньги
    game["players"][0]["resources"]["money"] = 10

    # У цели недостаточно зерна
    game["players"][1]["resources"]["grain"] = 3

    assert target_reason(game, "A1", 1) is not None

    # При недостатке денег ничего частично не списывается
    game["players"][0]["resources"]["money"] = 2
    money_before = game["players"][0]["resources"]["money"]

    assert action_reason(game, "A1") is not None
    assert game["players"][0]["resources"]["money"] == money_before

# T7 — Случайное событие

def test_event_is_applied_to_current_player(monkeypatch):
    game = new_game()

    # Положительный результат первого семейства событий
    monkeypatch.setattr(
        "game.events.random.choice",
        lambda families: families[0],
    )
    monkeypatch.setattr(
        "game.events.random.random",
        lambda: 0.1,
    )

    start_turn(game)

    assert game["phase"] == "event"
    assert game["event"] is not None
    assert game["players"][0]["resources"]["grain"] == 15

    # Отрицательный результат
    game = new_game()

    monkeypatch.setattr(
        "game.events.random.choice",
        lambda families: families[0],
    )
    monkeypatch.setattr(
        "game.events.random.random",
        lambda: 0.9,
    )

    start_turn(game)

    assert game["event"] is not None
    assert game["players"][0]["resources"]["grain"] == 7


# T8 — Вероятности случайных событий

def test_event_probability_distribution():
    total = 8000

    family_counts = {i: 0 for i in range(8)}
    positive_count = 0
    event_ids = set()

    for _ in range(total):
        event = choose_event()

        event_id = int(event["id"][1:])
        event_ids.add(event["id"])

        family = (event_id - 1) // 2
        family_counts[family] += 1

        if event_id % 2 == 1:
            positive_count += 1

    # Должны встречаться все 16 конкретных исходов
    assert len(event_ids) == 16

    # Все 8 семейств встречаются примерно одинаково часто
    for count in family_counts.values():
        assert 800 <= count <= 1200

    # Положительные и отрицательные исходы примерно 50/50
    positive_share = positive_count / total

    assert 0.45 <= positive_share <= 0.55


# T9 — Действия игроков

def test_trade():
    game = new_game()

    game["phase"] = "action"
    game["current"] = 0

    trade(game, 1)

    assert game["players"][0]["resources"]["money"] == 7
    assert game["players"][0]["resources"]["grain"] == 14

    assert game["players"][1]["resources"]["money"] == 13
    assert game["players"][1]["resources"]["grain"] == 6


# T9 — Остальные действия игроков

def test_bribe():
    game = new_game()

    game["phase"] = "action"
    game["current"] = 0

    game["players"][0]["resources"]["money"] = 10
    game["players"][1]["resources"]["smuta"] = 3

    execute_action(game, "A2", 1)

    assert game["players"][0]["resources"]["money"] == 5
    assert game["players"][0]["resources"]["smuta"] == 1

    assert game["players"][1]["resources"]["smuta"] == 1


def test_raid():
    game = new_game()

    game["phase"] = "action"
    game["current"] = 0

    execute_action(game, "A3", 1)

    assert game["players"][0]["resources"]["people"] == 8
    assert game["players"][0]["resources"]["grain"] == 13
    assert game["players"][0]["resources"]["smuta"] == 1

    assert game["players"][1]["resources"]["grain"] == 7


def test_alliance():
    game = new_game()

    game["phase"] = "action"
    game["current"] = 0

    execute_action(game, "A4", 1)

    assert game["players"][0]["resources"]["grain"] == 8
    assert game["players"][0]["resources"]["smuta"] == 0

    assert game["players"][1]["resources"]["smuta"] == 0


def test_propaganda():
    game = new_game()

    game["phase"] = "action"
    game["current"] = 0

    game["players"][0]["resources"]["smuta"] = 2

    execute_action(game, "A5", 1)

    assert game["players"][0]["resources"]["money"] == 7
    assert game["players"][0]["resources"]["smuta"] == 0

    assert game["players"][1]["resources"]["smuta"] == 2

# T10 — Выбор цели

def test_target_selection():
    game = new_game()

    game["phase"] = "action"
    game["current"] = 0

    # Самого себя выбрать нельзя
    assert target_reason(game, "A1", 0) is not None

    # Живого соперника выбрать можно
    assert target_reason(game, "A1", 1) is None

    # Выбывшего игрока выбрать нельзя
    game["players"][1]["alive"] = False

    assert target_reason(game, "A1", 1) is not None


# T11 — Порядок ходов

def test_next_player():
    game = new_game()

    game["current"] = 0
    game["phase"] = "result"

    next_player(game)

    assert game["current"] == 1
    assert game["phase"] == "start"


def test_turn_order_full_cycle():
    game = new_game()

    game["phase"] = "result"
    game["current"] = 0

    expected_order = [1, 2, 3, 0]

    for expected_player in expected_order:
        next_player(game)

        assert game["current"] == expected_player

        game["phase"] = "result"


# T12 — Выбывание игрока

def test_eliminated_player_cannot_act_or_receive_turn():
    game = new_game()

    game["players"][1]["alive"] = False

    game["phase"] = "action"
    game["current"] = 0

    # Выбывший игрок не может быть целью
    assert target_reason(game, "trade", 1) is not None

    # Если текущим оказался выбывший игрок,
    # событие для него не запускается
    game["current"] = 1
    game["phase"] = "start"

    start_turn(game)

    assert game["event"] is None
    assert game["current"] == 2


# T13 — Победа по престижу

def test_prestige_victory_boundary():
    cases = [
        (13, 15, 2, 0, False),
        (13, 20, 2, 0, True),
        (14, 20, 2, 0, True),
    ]

    for land, money, people, smuta, should_win in cases:
        game = new_game()
        player = game["players"][0]

        player["resources"]["land"] = land
        player["resources"]["money"] = money
        player["resources"]["people"] = people
        player["resources"]["smuta"] = smuta

        assert (
            prestige(player)
            == land * 2
            + money // 5
            + people // 5
            - smuta
        )

        check_result(game)

        assert (game["winner"] is not None) is should_win


# T14 — Победа последнего активного клана

def test_last_active_clan_wins():
    game = new_game()

    for index in [1, 2, 3]:
        game["players"][index]["alive"] = False

    check_result(game)

    assert game["winner"] is not None
    assert game["phase"] == "game_over"


# T15 — Ничья

def test_draw_when_all_players_are_eliminated():
    game = new_game()

    for player in game["players"]:
        player["alive"] = False

    check_result(game)

    assert game["winner"] is not None
    assert "Ничья" in game["winner"]
    assert game["phase"] == "game_over"


# T16 — Приоритет поражения над победой

def test_defeat_has_priority_over_prestige_victory():
    game = new_game()

    player = game["players"][0]

    player["resources"]["land"] = 19
    player["resources"]["money"] = 10
    player["resources"]["people"] = 10
    player["resources"]["smuta"] = 10

    check_result(game)

    assert player["alive"] is False
    assert game["winner"] is None


# T17 — Принудительный пропуск хода

def test_forced_skip_when_no_legal_action():
    game = new_game()

    game["phase"] = "action"
    game["current"] = 0

    player = game["players"][0]

    # Игрок жив, но не может выполнить ни одного действия
    player["resources"]["money"] = 0
    player["resources"]["grain"] = 0
    player["resources"]["people"] = 1
    player["resources"]["smuta"] = 0

    skip_action(game)

    assert player["alive"] is True
    assert game["current"] == 1
    assert game["phase"] == "start"
    assert len(game["log"]) >= 1


# T18 — Одно событие + одно действие за ход

def test_one_event_and_one_action_per_turn(monkeypatch):
    game = new_game()

    # Фиксируем положительное событие E1: +5 зерна
    monkeypatch.setattr(
        "game.events.random.choice",
        lambda families: families[0],
    )
    monkeypatch.setattr(
        "game.events.random.random",
        lambda: 0.1,
    )

    # Начало хода — происходит одно событие
    start_turn(game)

    assert game["event"] is not None
    assert game["phase"] == "event"

    grain_after_event = game["players"][0]["resources"]["grain"]

    # Завершаем событие
    finish_event(game)

    assert game["phase"] == "action"

    # Выполняем одно действие A1 — торговля
    execute_action(game, "A1", 1)

    # После одного действия ход переходит в результат
    assert game["phase"] == "result"

    # Торговля добавляет инициатору 4 зерна
    assert game["players"][0]["resources"]["grain"] == (
        grain_after_event + 4
    )


# T19 — Лог игры

def test_game_log_records_events_actions_and_reset(monkeypatch):
    game = new_game()

    # Фиксируем событие E1: +5 зерна
    monkeypatch.setattr(
        "game.events.random.choice",
        lambda families: families[0],
    )
    monkeypatch.setattr(
        "game.events.random.random",
        lambda: 0.1,
    )

    # Запускаем ход — событие должно попасть в лог
    start_turn(game)

    assert len(game["log"]) == 1
    assert game["log"][0] != ""

    log_before_action = len(game["log"])

    # Завершаем событие
    finish_event(game)

    assert game["phase"] == "action"

    # Выполняем действие A1 — торговля
    execute_action(game, "A1", 1)

    # Действие добавило новую запись
    assert len(game["log"]) == log_before_action + 1
    assert "Торговля" in game["log"][-1]

    # Новая игра начинается с пустым логом
    new_game_state = new_game()

    assert new_game_state["log"] == []

    # Выбытие игрока записывается в лог
    game = new_game()

    game["players"][0]["resources"]["smuta"] = 10

    check_result(game)

    assert any(
        "выбыл" in message
        for message in game["log"]
    )