import pygame
from pygame.locals import *

def update_tiles():
    for x in range(len(grid[0])):
        for y in range(len(grid)):
            total = 0
            for x_ in range(-1, 2):
                for y_ in range(-1, 2): # for each tile, check each of its neighbours
                    if (x_, y_) != (0, 0): # do not count itself
                        if 0 <= x + x_ < len(grid[0]):
                            if 0 <= y + y_ < len(grid):
                                total += grid[y + y_][x + x_]
            
            if total < 2 or total > 3: # die
                next_grid[y][x] = False
            if total == 3: # live
                next_grid[y][x] = True

def draw_tiles():
    for x in range(int(SIZE / size)):
        for y in range(int(SIZE / size)):
            c = grid[y][x] * 255
            pygame.draw.rect(screen, (c, c, c), Rect((x * (size + 1) + 1, y * (size + 1) + 1), (size, size)))

def draw_background():
    for x in range(0, SIZE, size + 1):
        pygame.draw.line(screen, (100, 100, 100), (x, 0), (x, SIZE))
    for y in range(0, SIZE, size + 1):
        pygame.draw.line(screen, (100, 100, 100), (0, y), (SIZE, y))

def get(src): # used to copy lists without links
    dest = []
    for line in src:
        dest.append(list(line))
    return dest

pygame.init()

SIZE = 500
screen = pygame.display.set_mode((SIZE, SIZE))
clock = pygame.time.Clock()
pygame.display.set_caption("Conway's Game of Life")

size = 10
delay = 0.01
grid = []
for y in range(int(SIZE / size)):
    grid.append([])
    for x in range(int(SIZE / size)):
        grid[-1].append(False)

next_grid = []
grid_creative = []
next_grid = get(grid)

play = False

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        elif event.type == MOUSEBUTTONDOWN and event.button == 1 and not play:
            pos = list(pygame.mouse.get_pos())
            x = int(pos[0] / (size + 1))
            y = int(pos[1] / (size + 1))
            
            grid[y][x] = not grid[y][x]
        elif event.type == KEYDOWN and event.key == K_SPACE:
            if play: # to creative
                play = False
                grid = get(grid_creative)
            else: # simulate
                play = True
                grid_creative = get(grid)

    draw_background()
    if play:
        next_grid = get(grid)
        update_tiles()
        grid = get(next_grid) # update the tiles all at once
        clock.tick(1 / delay)
    draw_tiles()
    
    pygame.display.flip()
