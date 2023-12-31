import pygame, time
from pygame.locals import *

screen = pygame.display.set_mode((300, 200))

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        elif event.type == KEYDOWN:
            print(event.key)
