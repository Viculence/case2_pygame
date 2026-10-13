"""Readable game dashboard. Presentation only; rules remain in game modules."""
from functools import lru_cache
from pathlib import Path
import pygame
import config
from game.actions import action_reason, available_targets, has_legal_action, target_reason
from game.state import prestige

WIDTH, HEIGHT = 1440, 960
Fonts = tuple
Controls = list[tuple[str, pygame.Rect]]
BG = (231, 238, 214)
PANEL = (251, 249, 232)
INNER = (232, 238, 214)
TEXT = (39, 59, 39)
MUTED = (91, 108, 78)
GREEN = (48, 109, 52)
RED = (171, 61, 43)
GOLD = (139, 96, 30)
CLAN_COLORS = ((148, 84, 29), (48, 104, 106), (65, 112, 49), (118, 79, 119))
LABELS = {'grain': 'Орехи', 'money': 'Шишкоины', 'land': 'Дупла', 'people': 'Белки', 'smuta': 'Паника'}
_report = None
_log_scroll = 0
_pointer = (-1, -1)

def set_pointer(pos):
    global _pointer
    _pointer = pos

@lru_cache(maxsize=32)
def font(size=18, bold=False):
    return pygame.font.SysFont('segoeui,dejavusans,arial', size, bold=bold)

def lines(text, width, size=18, bold=False):
    f = font(size, bold)
    result = []
    for paragraph in str(text).split('\n'):
        line = ''
        for word in paragraph.split():
            trial = (line + ' ' + word).strip()
            if line and f.size(trial)[0] > width:
                result.append(line)
                line = word
            else:
                line = trial
        result.append(line)
    return result

def text(s, value, x, y, width, size=18, color=TEXT, bold=False):
    for line in lines(value, width, size, bold):
        s.blit(font(size, bold).render(line, True, color), (x, y))
        y += size + 5
    return y

@lru_cache(maxsize=1)
def background():
    path = Path(__file__).resolve().parent.parent / 'assets' / 'forest_light.png'
    try:
        return pygame.transform.smoothscale(pygame.image.load(str(path)).convert(), (WIDTH, HEIGHT))
    except (pygame.error, FileNotFoundError):
        surface = pygame.Surface((WIDTH, HEIGHT))
        surface.fill(BG)
        return surface


def box(s, rect, color=PANEL, border=None):
    rect = pygame.Rect(rect)
    layer = pygame.Surface((rect.w + 8, rect.h + 10), pygame.SRCALPHA)
    pygame.draw.rect(layer, (40, 61, 27, 24), (3, 5, rect.w, rect.h), border_radius=16)
    opacity = 240 if color == PANEL else 250
    pygame.draw.rect(layer, (*color, opacity), (0, 0, rect.w, rect.h), border_radius=16)
    pygame.draw.rect(layer, (*(border or (192, 204, 166)), 255), (0, 0, rect.w, rect.h), width=2 if border else 1, border_radius=16)
    s.blit(layer, rect.topleft)


@lru_cache(maxsize=24)
def resource_icon(key, size=24):
    # Supersampled vector pictograms: no dependence on emoji fonts.
    scale = 3
    icon = pygame.Surface((32, 32), pygame.SRCALPHA)
    brown, light, leaf = (132, 77, 34), (211, 156, 72), (72, 112, 46)
    if key == 'grain':
        pygame.draw.ellipse(icon, light, (7, 10, 19, 20))
        pygame.draw.ellipse(icon, brown, (5, 7, 23, 11))
        pygame.draw.line(icon, brown, (16, 9), (19, 2), 3)
        pygame.draw.line(icon, (243, 202, 124), (13, 18), (13, 25), 2)
    elif key == 'money':
        pygame.draw.ellipse(icon, brown, (7, 2, 18, 28))
        for row in range(4):
            for col in range(2):
                x=11+col*9-(row%2)*2; y=7+row*6
                pygame.draw.polygon(icon, light, [(x-4,y),(x,y-3),(x+4,y),(x,y+4)])
    elif key == 'land':
        pygame.draw.rect(icon, brown, (6, 6, 21, 25), border_radius=4)
        pygame.draw.ellipse(icon, (69, 47, 29), (12, 14, 10, 15))
        pygame.draw.ellipse(icon, leaf, (3, 1, 27, 12))
        pygame.draw.line(icon, light, (9,16),(9,27),2)
    elif key == 'people':
        pygame.draw.ellipse(icon, (193, 103, 37), (17, 3, 14, 24))
        pygame.draw.ellipse(icon, (226, 144, 58), (6, 13, 16, 17))
        pygame.draw.circle(icon, (226, 144, 58), (11, 11), 8)
        pygame.draw.polygon(icon, brown, [(5,6),(6,0),(11,5)])
        pygame.draw.polygon(icon, brown, [(13,5),(17,0),(18,8)])
        pygame.draw.circle(icon, TEXT, (8,10),2)
        pygame.draw.ellipse(icon, (248,220,161), (8,20,9,9))
    elif key == 'smuta':
        pygame.draw.polygon(icon, (216,149,43), [(16,1),(31,29),(1,29)])
        pygame.draw.line(icon, (90,59,25), (16,9),(16,19),3)
        pygame.draw.circle(icon, (90,59,25),(16,24),2)
    else:
        pygame.draw.polygon(icon, (194,146,39), [(16,1),(20,11),(31,12),(23,19),(26,30),(16,24),(6,30),(9,19),(1,12),(12,11)])
    return pygame.transform.smoothscale(pygame.transform.scale(icon,(32*scale,32*scale)),(size,size))


def effect(changes):
    return ' / '.join(f'{LABELS[k]} {v:+d}' for k, v in changes.items()) or 'Без изменений'

def observe(before, after, command):
    """Keep actual before/after values, even when the controller clears selection."""
    global _report, _log_scroll
    if command == 'restart' or (command == 'next' and after['phase'] == 'start'):
        _report = None
    if len(after['log']) > len(before['log']):
        _log_scroll = 0
    if command == 'confirm' and len(after['log']) > len(before['log']):
        aid, target = before['selected_action'], before['selected_target']
        if aid is not None and target is not None:
            _report = {'title': config.ACTIONS[aid]['title'], 'rows': []}
            for i in (before['current'], target):
                a, b = before['players'][i], after['players'][i]
                _report['rows'].append((a['name'], a['resources'].copy(), b['resources'].copy(), prestige(a), prestige(b)))
    if command == 'start':
        _report = None

def scroll(amount):
    global _log_scroll
    _log_scroll = max(0, _log_scroll + amount)

def draw(screen, game, targets=None, scores=None, fonts=None):
    global _log_scroll
    screen.blit(background(), (0, 0))
    controls = []
    phase = game['phase']
    actor = game['players'][game['current']]
    accent = CLAN_COLORS[game['current']]
    box(screen, (28, 17, 1384, 59))
    text(screen, 'Академгородок: белки захватили науку', 48, 27, 1344, 29, TEXT, True)
    # Four persistent resource panels.
    for i, p in enumerate(game['players']):
        x, y, w = 28 + i * 350, 94, 334
        col = CLAN_COLORS[i] if p['alive'] else MUTED
        box(screen, (x, y, w, 195), PANEL, col if i == game['current'] else None)
        text(screen, 'Сейчас ходит' if i == game['current'] and p['alive'] else 'Выбыл' if not p['alive'] else '', x+15,y+12,w-30,13,col,True)
        text(screen, p['name'], x+15,y+35,w-30,18,col,True)
        for j,(key,label) in enumerate(LABELS.items()):
            xx = x+15+(j%3)*104
            yy = y+89+(j//3)*46
            text(screen,label,xx,yy,103,12,MUTED)
            val = p['resources'][key]
            screen.blit(resource_icon(key), (xx, yy+17))
            text(screen,str(val),xx+29,yy+15,69,23,RED if key=='smuta' and val>=7 else TEXT,True)
        score = prestige(p)
        text(screen, 'Престиж',x+223,y+135,100,12,MUTED)
        screen.blit(resource_icon('prestige'), (x+223, y+152))
        text(screen,str(score),x+252,y+150,70,22,col,True)
    # Only the current stage is shown, without numbered progress labels.
    names = {'start':'Начало хода','event':'Случайное событие','action':'Выбор действия','target':'Выбор соперника','result':'Результат действия','game_over':'Партия завершена'}
    box(screen, (28, 306, 1384, 64))
    text(screen, names[phase],48,320,660,26,accent,True)
    text(screen, actor['name'],770,326,615,19,MUTED,True)
    # Event remains separate from the action/result.
    box(screen,(28,386,430,482))
    ev = game.get('event')
    text(screen,'СОБЫТИЕ ЭТОГО ХОДА',48,405,390,14,MUTED,True)
    if ev:
        col = GREEN if ev['type']=='Положительное' else RED
        text(screen,ev['type'],48,437,390,15,col,True)
        y = text(screen,ev['title'],48,473,385,25,TEXT,True)
        y = text(screen,ev.get('story',''),48,y+16,383,17,MUTED)
        text(screen,'Фактическое изменение',48,max(y+22,650),383,16,TEXT,True)
        text(screen,effect(ev.get('actual_changes',ev['changes'])),48,max(y+52,680),380,20,col,True)
    else:
        text(screen,'Что принесёт этот ход?',48,465,370,29,TEXT,True)
        text(screen,'Начните ход, чтобы узнать событие. Оно применяется автоматически к вашему клану.',48,555,375,20,MUTED)
    # Right main interaction panel.
    box(screen,(476,386,936,482))
    def button(label, rect, command, enabled=True, selected=False):
        r=pygame.Rect(rect)
        color = accent if selected else (79, 119, 60) if enabled else (220, 226, 204)
        box(screen,r,color,accent if enabled and r.collidepoint(_pointer) else None)
        ls=lines(label,r.w-24,17,True)
        text(screen,label,r.x+12,r.y+(r.h-len(ls)*22)//2,r.w-24,17,(255, 252, 231) if enabled else MUTED,True)
        if enabled: controls.append((command,r))
    if phase in ('action','target'):
        text(screen,'Выберите одно действие',496,402,870,20,TEXT,True)
        for n,(aid,spec) in enumerate(config.ACTIONS.items()):
            x=496+n*179
            enabled=bool(available_targets(game,aid))
            selected=game['selected_action']==aid
            box(screen,(x,441,168,167),INNER,accent if selected else None)
            button(spec['title'],(x+5,446,158,36),'action:'+aid,enabled,selected)
            text(screen,'ВЫ',x+10,489,150,12,MUTED,True)
            text(screen,effect(spec['actor_changes']).replace(' / ', '\n'),x+10,507,148,13,TEXT if enabled else MUTED)
            text(screen,'ЦЕЛЬ: '+effect(spec['target_changes']),x+10,561,148,12,MUTED)
            if not enabled and pygame.Rect(x,441,168,167).collidepoint(_pointer):
                reason=action_reason(game,aid) or 'Нет соперника с нужными ресурсами.'
                text(screen,reason,496,831,870,13,RED)
        aid=game['selected_action']
        if aid:
            text(screen,'Соперник',496,626,870,17,MUTED,True)
            pos=0
            for i,p in enumerate(game['players']):
                if i==game['current']: continue
                x=496+pos*297
                reason=target_reason(game,aid,i)
                button(p['name'],(x,656,283,61),f'target:{i}',reason is None,game['selected_target']==i)
                if reason: text(screen,reason,x+3,720,278,12,RED)
                pos+=1
            button('Подтвердить действие',(1018,774,373,44),'confirm',game['selected_target'] is not None)
            button('Сбросить выбор',(496,774,245,44),'back')
        elif not has_legal_action(game):
            text(screen,'Нет доступных действий: можно передать ход.',496,648,866,20,RED)
            button('Пропустить действие',(496,742,390,49),'skip')
        else:
            text(screen,'Сначала выберите действие, затем соперника.\nРесурсы спишутся только после подтверждения.',496,654,850,21,MUTED)
    elif phase in ('result','game_over'):
        text(screen,('Выполнено: '+_report['title']) if _report else 'Итог',496,405,870,25,GREEN,True)
        if _report:
            for n,(name,old,new,sp,sn) in enumerate(_report['rows']):
                x=496+n*450
                box(screen,(x,449,435,281),INNER)
                text(screen,name,x+16,462,404,18,accent if n==0 else MUTED,True)
                yy=520
                for key in LABELS:
                    delta=new[key]-old[key]
                    if delta:
                        good=delta<0 if key=='smuta' else delta>0
                        text(screen,LABELS[key],x+16,yy,175,17,MUTED)
                        text(screen,f'{old[key]} → {new[key]}  ({delta:+d})',x+180,yy,240,19,GREEN if good else RED,True)
                        yy+=31
                text(screen,f'Престиж: {sp} → {sn}',x+16,yy+9,404,18,GOLD,True)
        else:
            if phase != 'game_over':
                text(screen,game['message'],496,475,858,23,TEXT)
        if phase=='game_over':
            text(screen,game['winner'] or game['message'],496,743 if _report else 495,858,18 if _report else 26,GOLD,True)
            button('Новая игра',(1080,814,310,40),'restart')
        else:
            button('Передать ход',(1050,783,340,56),'next')
    else:
        text(screen,'Ваш ход: '+actor['name'],496,432,860,27,TEXT,True)
        if phase=='start':
            text(screen,'Сначала случайное событие. Затем одно действие с другим кланом.',496,529,790,24,MUTED)
            button('Начать ход',(496,700,380,60),'start')
        else:
            text(screen,'Событие уже применено. Изменения ресурсов показаны слева и на панелях кланов.',496,529,790,24,MUTED)
            button('Перейти к действиям',(496,700,410,60),'continue')
    # Compact log opener; full journal is a scrollable overlay toggled in main.
    button('Журнал событий',(1130,885,282,47),'ui:log')
    if game.get('_show_log'):
        overlay=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        overlay.fill((30,48,25,155)); screen.blit(overlay,(0,0))
        box(screen,(135,80,1170,810),PANEL,accent)
        text(screen,'Журнал партии',165,103,900,29,TEXT,True)
        text(screen,'Новые записи сверху · прокрутка колёсиком',165,149,1000,17,MUTED)
        controls.clear()
        button('Закрыть',(1130,102,145,43),'ui:log')
        viewport=pygame.Rect(165,196,1110,654)
        records=list(reversed(game['log']))
        total=sum(len(lines(e,1060,18))*23+35 for e in records)
        _log_scroll=min(_log_scroll,max(0,total-viewport.h))
        screen.set_clip(viewport)
        yy=viewport.y-_log_scroll
        for entry in records:
            h=len(lines(entry,1060,18))*23+21
            box(screen,(165,yy,1100,h),INNER)
            text(screen,entry,183,yy+10,1060,18,TEXT)
            yy+=h+14
        if not records: text(screen,'Здесь появятся события и результаты действий.',180,215,1000,21,MUTED)
        screen.set_clip(None)
    return controls
