import pygame
from pygame.locals import *

from math import pi, sin

pygame.init()
screen = pygame.display.set_mode((500, 200))
font = pygame.font.SysFont('consolas', 20)
ticks = pygame.time.get_ticks

x = start = goal = 250
start_time = 0
speed = 0.5

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        elif event.type == MOUSEWHEEL:
            start_time = ticks()
            start = x
            goal -= event.y*20
            goal = min(max(goal, 0), 500)

    progress = (ticks()-start_time) * speed / 1000 # from 0 to 1
    if progress < 1:
        # fast at the start
        x = start + (goal-start) * (0.4 + 0.6 * sin(pi * (progress - 2/7) / 1.4))

        # full sine
        #x = start + (goal-start) * (sin(pi * (progress-0.5)) + 1) / 2
    else:
        x = start = goal

    screen.fill(0)

    screen.blit(font.render('Position: %d' %x, 1, (255, 255, 255)), (2, 2))
    screen.blit(font.render('Start: %d' %start, 1, (255, 0, 0)), (2, 22))
    screen.blit(font.render('Goal: %d' %goal, 1, (0, 255, 0)), (2, 42))
    screen.blit(font.render('Progress: %.2f' %progress, 1, (127, 127, 127)), (202, 2))
    pygame.draw.rect(screen, (255, 255, 255), Rect((0, 100), (x, 100)))
    pygame.draw.line(screen, (255, 0, 0), (start, 100), (start, 200))
    pygame.draw.line(screen, (0, 255, 0), (goal, 100), (goal, 200))

    pygame.display.flip()
