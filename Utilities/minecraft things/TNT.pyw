import time
import random
import pygame
from pygame.locals import *

def explode():
    explosions[random.randint(0, 2)].play()

pygame.init()
screen = pygame.display.set_mode((200, 200))
pygame.display.set_caption('TNT')
pygame.display.set_icon(pygame.image.load('tnt.png'))

tnt = pygame.transform.scale(pygame.image.load('tnt.png'), (200, 200))
fizz = pygame.mixer.Sound('fuse.ogg')
explosions = ['explode1.ogg', 'explode2.ogg', 'explode3.ogg', 'explode4.ogg']
explosions = [pygame.mixer.Sound(x) for x in explosions]

start = 0

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        elif event.type == MOUSEBUTTONDOWN:
            fizz.play()
            start = time.time() - 0.4
        elif event.type == MOUSEBUTTONUP:
            explode()

    if True in pygame.mouse.get_pressed() and int((time.time() - start) * 4) % 2:
        screen.fill((255, 255, 255))
    else:
        screen.blit(tnt, (0, 0))

    pygame.display.flip()
