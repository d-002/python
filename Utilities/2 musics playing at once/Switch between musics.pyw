import pygame
from pygame.locals import *

pygame.init()

screen = pygame.display.set_mode((640, 300))

music1 = pygame.mixer.Sound('music1.ogg')
music2 = pygame.mixer.Sound('music2.ogg')
music1.play(1)
music2.play(-1)

x = 0

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    if pygame.mouse.get_pressed()[0]:
        x = pygame.mouse.get_pos()[0]

    music1.set_volume(1 - x/640)
    music2.set_volume(x / 640)

    screen.fill((0, 0, 0))
    for color, x1, x2 in [[(60, 50, 220), 0, x-3], [(220, 30, 240), x+3, 640]]:
        for y in range(300):
            r, g, b = color
            r += (0 - r) * y/300
            g += (0 - g) * y/300
            b += (0 - b) * y/300
            pygame.draw.line(screen, (int(r), int(g), int(b)), (x1, y), (x2, y))
    pygame.display.flip()
