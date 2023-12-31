import pygame
from random import randint
from pygame.locals import *

def init():
    global grid, flags
    grid = [[0]*M for _ in range(N)]
    flags = [[0]*M for _ in range(N)]

def init_mines(n):
    global mines
    mines = []
    available = [(_x, _y) for _x in range(M) for _y in range(N)]
    for _x in range(x-1, x+2):
        for _y in range(y-1, y+2):
            available.remove((_x, _y))
    for _ in range(n):
        mines.append(available.pop(randint(0, len(available)-1)))

def display(bombs=False):
    screen.fill(G)
    for _x in range(M):
        X = _x*20
        for _y in range(N):
            Y = _y*20
            value = grid[_y][_x]
            if value or (game_over and (_x, _y) in mines):
                pygame.draw.line(screen, B, (X, Y), (X+19, Y))
                pygame.draw.line(screen, B, (X, Y), (X, Y+19))
            if bombs and (_x, _y) in mines:
                if (_x, _y) == game_over:
                    pygame.draw.rect(screen, R, Rect(X, Y, 20, 20))
                screen.blit(bomb, (X, Y))
                continue
            if _x == x and _y == y:
                pygame.draw.rect(screen, S, Rect(X+1, Y+1, 19, 19))
            if value > 1:
                text = font.render(str(value-1), 1, colors[value-2])
                screen.blit(text, (X + 10 - text.get_width()//2, Y+4))
            elif not value:
                if flags[_y][_x]: screen.blit(flag, (X, Y))
                pygame.draw.polygon(screen, W, [(X,    Y   ), (X+20, Y   ),
                                                (X+18, Y+2 ), (X+2,  Y+2 ),
                                                (X+2,  Y+18), (X,    Y+20)])
                pygame.draw.polygon(screen, B, [(X+20, Y+20), (X,    Y+20),
                                                (X+2,  Y+18), (X+18, Y+18),
                                                (X+18, Y+2 ), (X+20, Y   )])
    pygame.display.flip()

def count(x, y):
    count = 0
    for _x in range(x-1, x+2):
        for _y in range(y-1, y+2):
            if (_x, _y) in mines: count += 1
    return count

def discover(x, y, stack):
    global game_over
    if flags[y][x]: return

    # clicked on a mine
    if (x, y) in mines:
        game_over = (x, y)
        return

    # mines around
    c = count(x, y)
    grid[y][x] = c+1
    if c: return

    # no mines around: discover more terrain
    for _x in range(x-1, x+2):
        for _y in range(y-1, y+2):
            if 0 <= _x < M and 0 <= _y < N and not grid[_y][_x]:
                if (_x, _y) not in mines and not (_x, _y) in stack:
                    stack.append((_x, _y))

M, N = 20, 20
N_mines = 40
is_init = False
init()
W, S, G, B = (255, 255, 255), (220, 220, 220), (192, 192, 192), (127, 127, 127)
R = (255, 0, 0)
colors = [(0, 0, 255), (0, 127, 0), (255, 0, 0), (0, 0, 127),
          (127, 0, 0), (0, 127, 127), (0, 0, 0), (127, 127, 127)]

pygame.init()
screen = pygame.display.set_mode((20*M, 20*N))
font = pygame.font.SysFont('consolas', 14, 1)
clock = pygame.time.Clock()
flag, bomb = pygame.image.load('flag.png'), pygame.image.load('bomb.png')
pygame.display.set_caption('Minesweeper')
pygame.display.set_icon(bomb)

game_over = None
while True:
    x, y = pygame.mouse.get_pos()
    x, y = int(x/20), int(y/20)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            quit()
        elif not game_over and event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if not is_init:
                    is_init = True
                    init_mines(N_mines)
                stack = [(x, y)]
                i = 0
                while i < len(stack):
                    discover(*stack[i], stack)
                    i += 1
            elif event.button == 3:
                if not grid[y][x]: flags[y][x] = 1-flags[y][x]

    display(game_over)
    clock.tick(60)
