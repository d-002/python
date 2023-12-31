import math
import time
import random
import pygame
from pygame.locals import *

pygame.init()

def eat():
    sounds[random.randint(0, 2)].play()

pygame.init()
screen = pygame.display.set_mode((200, 200))
pygame.display.set_caption('Eat')
pygame.display.set_icon(pygame.image.load('bread.png'))

bread = pygame.transform.scale(pygame.image.load('bread.png'), (200, 200))
sounds = ['eat1.ogg', 'eat2.ogg', 'eat3.ogg']
sounds = [pygame.mixer.Sound(x) for x in sounds]
burp = pygame.mixer.Sound('burp.ogg')

x = 0
last_eat = 0
was_eating = False

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    if True in pygame.mouse.get_pressed():
        was_eating = True
        if time.time() - last_eat >= 0.2:
            last_eat = time.time()
            eat()
    elif was_eating:
        eat()
        burp.play()
        was_eating = False

    screen.fill((0, 0, 0))
    if True in pygame.mouse.get_pressed():
        y = 50 - abs(math.sin(time.time() * 20) * 50)
        screen.blit(bread, (0, y))
    else:
        screen.blit(bread, (0, 0))

    pygame.display.flip()
