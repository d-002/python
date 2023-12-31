from urllib.request import urlopen
import pygame
from pygame.locals import *

def screen():
    image = pygame.Surface((8, 8))
    image.blit(pygame.image.load('skin.png'), (-8, -8))
    image.blit(pygame.image.load('skin.png'), (-40, -8))
    w, h = image.get_size()
    image = pygame.transform.scale(image, (200, 200))
    w, h = image.get_size()
    screen = pygame.display.set_mode((w, h))
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()

        screen.blit(image, (0, 0))
        pygame.display.flip()

pygame.init()

name = input('Type your username: ')
file = urlopen('https://minecraft.tools/download-skin/%s' %name).read()
with open('skin.png', 'wb') as f:
    f.write(file)

screen()
