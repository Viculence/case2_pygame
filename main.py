import pygame

import config
from game.actions import available_targets
from game.controller import handle_command
from game.state import new_game, prestige
from game.ui import Fonts, draw


def main() -> None:
    """Запуск окна и направление кликов в игровой контроллер."""
    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Академгородок: белки захватили науку")
    font_path = pygame.font.match_font(config.FONT_FAMILIES)
    fonts: Fonts = (
        pygame.font.Font(font_path, config.TITLE_SIZE),
        pygame.font.Font(font_path, config.TEXT_SIZE),
        pygame.font.Font(font_path, config.SMALL_SIZE),
    )
    clock = pygame.time.Clock()
    game = new_game()
    running = True

    while running:
        controls = draw(
            screen, game, available_targets(game),
            [prestige(player) for player in game["players"]], fonts
        )
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == config.LEFT_MOUSE_BUTTON
            ):
                for command, rect in controls:
                    if rect.collidepoint(event.pos):
                        game = handle_command(game, command)
                        break
        clock.tick(config.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()