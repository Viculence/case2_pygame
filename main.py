"""Resizable Pygame window. Game rules are delegated to the existing controller."""
from copy import deepcopy
import pygame
import config
from game.controller import handle_command
from game.state import new_game
from game import ui


def main():
    pygame.init()
    info=pygame.display.Info()
    scale=min(1.0, info.current_w/ui.WIDTH*0.92, info.current_h/ui.HEIGHT*0.88)
    screen=pygame.display.set_mode((int(ui.WIDTH*scale),int(ui.HEIGHT*scale)),pygame.RESIZABLE)
    pygame.display.set_caption('Академгородок: белки захватили науку')
    canvas=pygame.Surface((ui.WIDTH,ui.HEIGHT))
    clock=pygame.time.Clock()
    game=new_game()
    running=True
    while running:
        w,h=screen.get_size()
        factor=min(w/ui.WIDTH,h/ui.HEIGHT)
        size=(max(1,int(ui.WIDTH*factor)),max(1,int(ui.HEIGHT*factor)))
        offset=((w-size[0])//2,(h-size[1])//2)
        mouse=pygame.mouse.get_pos()
        ui.set_pointer(((mouse[0]-offset[0])/factor,(mouse[1]-offset[1])/factor))
        controls=ui.draw(canvas,game)
        window_background = pygame.transform.smoothscale(
            ui.background(), (w, h)
        )
        screen.blit(window_background, (0, 0))
        screen.blit(pygame.transform.smoothscale(canvas, size), offset)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            elif event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
                game['_show_log']=False
            elif event.type==pygame.MOUSEWHEEL and game.get('_show_log'):
                ui.scroll(-event.y*65)
            elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                pos=((event.pos[0]-offset[0])/factor,(event.pos[1]-offset[1])/factor)
                for command,rect in controls:
                    if rect.collidepoint(pos):
                        if command=='ui:log':
                            game['_show_log']=not game.get('_show_log',False)
                        else:
                            before=deepcopy(game)
                            game=handle_command(game,command)
                            ui.observe(before,game,command)
                        # Do not let a second queued click use stale hitboxes.
                        controls=[]
                        break
        clock.tick(config.FPS)
    pygame.quit()


if __name__=='__main__':
    main()
