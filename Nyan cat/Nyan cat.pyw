import time
import pygame
from pygame.locals import *
from math import sin, sqrt
from random import randint, choice

class Cat:
    def __init__(self):
        self.x = 400
        self.y = 240
        self.moveX = 0
        self.moveY = 0
        
        self.hyperspeed = [0, 0] # start, stop
        self.prev_hyperspeed = False
        
        self.scroll = 0
        self.colors = [(255, 0, 0),
                       (255, 155, 0),
                       (255, 255, 0),
                       (50, 255, 0),
                       (0, 155, 255),
                       (105, 55, 255)]
        
        self.image = pygame.transform.scale(pygame.image.load('cat.png'), (128, 80))
        self.w, self.h = self.image.get_size()

    def check_hyperspeed(self):
        if True in pygame.mouse.get_pressed(): # any mouse button pressed
            if self.prev_hyperspeed: # hyperspeed before
                self.hyperspeed[1] = time.time()
            else: # set the start
                self.hyperspeed[0] = time.time()
            self.prev_hyperspeed = True
            self.effects()
        else:
            self.prev_hyperspeed = False

    def effects(self):
        w, h = screen.get_size()
        if not False in pygame.mouse.get_pressed():
            number = 1000
        else:
            number = 20000
        for x in range(int(w * h / number)):
            pygame.draw.circle(screen, choice(self.colors), (randint(0, w), randint(0, h)), randint(1, 10))

    def get_image(self):
        if 0 <= time.time() - self.hyperspeed[0] <= 0.5: # bigger the first half of second
            time_ = 2 * (0.5 + time.time() - self.hyperspeed[0])
            image = pygame.transform.scale(self.image, (int(128 * time_), int(80 * time_)))
            self.w, self.h = image.get_size()
            return image
        
        elif 0 <= time.time() - self.hyperspeed[1] <= 0.5: # tinier the last half of second
            time_ = 2 * (1 + self.hyperspeed[1] - time.time())
            image = pygame.transform.scale(self.image, (int(128 * time_), int(80 * time_)))
            self.w, self.h = image.get_size()
            return image
        
        elif self.prev_hyperspeed: # in hyperspeed
            image = pygame.transform.scale(self.image, (256, 160))
            self.w, self.h = image.get_size()
            return image
        
        self.w, self.h = self.image.get_size()
        return self.image

    def run(self):
        # follow the mouse pointer
        x, y = pygame.mouse.get_pos()
        vect = (x - self.x, y - self.y)
        # move quicker if hyperspeed
        if vect[0] > 0:
            self.moveX += 3000 * time_passed * (1 + self.prev_hyperspeed * 5)
        elif vect[0] < 0:
            self.moveX -= 3000 * time_passed * (1 + self.prev_hyperspeed * 5)
        if vect[1] > 0:
            self.moveY += 3000 * time_passed * (1 + self.prev_hyperspeed * 5)
        elif vect[1] < 0:
            self.moveY -= 3000 * time_passed * (1 + self.prev_hyperspeed * 5)
        
        self.moveX *= 0.95**(100 * time_passed)
        self.moveY *= 0.95**(100 * time_passed)
        
        self.x += self.moveX * time_passed
        self.y += self.moveY * time_passed
        
        for x in range(0, int(self.x - 10), 50):
            y = self.y - 30 + int(sin((x - self.scroll) / 10) * 5)
            for color in self.colors:
                pygame.draw.rect(screen, color, Rect((x, y), (50, 8)))
                y += 8
        
        self.check_hyperspeed()
        
        screen.blit(self.get_image(), (int(self.x - self.w / 2), int(self.y - self.h / 2)))
        
        hyperspeed = 1 + self.prev_hyperspeed
        self.scroll += 200 * time_passed * hyperspeed # quicker if hyperspeed

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_icon(pygame.image.load('icon.png'))
pygame.display.set_caption('Nyan cat')
clock = pygame.time.Clock()

background = pygame.image.load('background.png')
music = pygame.mixer.Sound('music.mp3')
music.play(-1)
cat = Cat()

time_passed = 0
scroll = 0
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    hyperspeed = 1 + cat.prev_hyperspeed * 5
    scroll += 500 * time_passed * hyperspeed # quicker if hyperspeed
    screen.blit(background, (int(-(scroll % 640)), 0))
    screen.blit(background, (int(640 - (scroll % 640)), 0))
    
    cat.run()
    
    pygame.display.flip()
    time_passed = clock.tick(100) / 1000
