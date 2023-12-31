import pygame
from pygame.locals import *

pygame.init()
font = pygame.font.SysFont('consolas', 100)

surf = pygame.Surface((900, 900), SRCALPHA)
for x in range(900):
    for y in range(900):
        dist = ((x-450)**2 + (y-450)**2)**0.5
        surf.set_at((x, y), (255, 41, 11, min(max(dist-250, 0)//1.5, 255)))
surf = pygame.transform.smoothscale(surf, (900, 500))

pygame.image.save(surf, ('low_overlay.png'))

###

surf.fill((0, 0, 0, 150))
text = font.render('u die :)', 1, (255, 255, 255))
w, h = text.get_size()
surf.blit(text, ((900-w)//2, (500-h)//2))

pygame.image.save(surf, 'death_overlay.png')
