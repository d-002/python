import time
import pygame
from random import randint
from pygame.locals import *

SCREENSIZE = (477, 477)

class Snake:
    def __init__(self):
        self.pos = [(4 - x, int(size[1] / 2)) for x in range(5)]
        self.direction = 'right'
        self.speed = 2
        self.game_over = False
        self.head = pygame.image.load('files\\head.png').convert_alpha()
        self.head = [pygame.transform.rotate(self.head, 90 * x) for x in range(4)]
        self.body = pygame.image.load('files\\body.png').convert_alpha()
        self.tail = pygame.image.load('files\\tail.png').convert_alpha()
        self.tail = [pygame.transform.rotate(self.tail, 90 * x) for x in range(4)]
        
    def add(self):
        self.speed += 0.5
        self.pos.append(self.pos[-1])

    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_RIGHT] and self.direction != 'left':
            self.direction = 'right'
        if pressed_keys[K_LEFT] and self.direction != 'right':
            self.direction = 'left'
        if pressed_keys[K_UP] and self.direction != 'down':
            self.direction = 'up'
        if pressed_keys[K_DOWN] and self.direction != 'up':
            self.direction = 'down'

    def update(self):
        for pos in range(len(self.pos) - 1, 0, -1):
            self.pos[pos] = self.pos[pos - 1]

        self.move()
        
        if self.direction == 'right':
            self.pos[0] = (self.pos[0][0] + 1, self.pos[0][1])
        if self.direction == 'left':
            self.pos[0] = (self.pos[0][0] - 1, self.pos[0][1])
        if self.direction == 'up':
            self.pos[0] = (self.pos[0][0], self.pos[0][1] - 1)
        if self.direction == 'down':
            self.pos[0] = (self.pos[0][0], self.pos[0][1] + 1)

        if self.pos[0][0] < 0:
            self.pos[0] = (0, self.pos[0][1])
        if self.pos[0][0] >= size[0]:
            self.pos[0] = (size[0] - 1, self.pos[0][1])

        if self.pos[0][0] < 0:
            self.pos[0] = (0, self.pos[0][1])
            self.game_over = True
        if self.pos[0][0] >= size[0]:
            self.pos[0] = (size[1] - 1, self.pos[0][1])
            self.game_over = True
        if self.pos[0][1] < 0:
            self.pos[0] = (self.pos[0][0], 0)
            self.game_over = True
        if self.pos[0][1] >= size[1]:
            self.pos[0] = (self.pos[0][0], size[1] - 1)
            self.game_over = True
        if self.pos[0] in self.pos[1:-1]:
            self.game_over = True
        self.render()

    def render(self):
        if self.direction == 'left':
            index = 0
        elif self.direction == 'down':
            index = 1
        elif self.direction == 'right':
            index = 2
        elif self.direction == 'up':
            index = 3
        screen.blit(self.head[index], (5 + self.pos[0][0] * 26, 5 + self.pos[0][1] * 26))
        for pos in self.pos[1:-1]:
            screen.blit(self.body, (5 + pos[0] * 26, 5 + pos[1] * 26))
        if self.pos[-1][0] - self.pos[-2][0] > 0:
            index = 0
        elif self.pos[-1][0] - self.pos[-2][0] < 0:
            index = 2
        elif self.pos[-1][1] - self.pos[-2][1] > 0:
            index = 3
        elif self.pos[-1][1] - self.pos[-2][1] < 0:
            index = 1
        screen.blit(self.tail[index], (5 + self.pos[-1][0] * 26, 5 + self.pos[-1][1] * 26))

class Apple:
    def __init__(self):
        self.new_pos()
        self.image = pygame.image.load('files\\apple.png').convert_alpha()

    def new_pos(self):
        self.pos = (randint(3, size[0] - 2), randint(3, size[1]) - 2)

    def update(self):
        for pos in snake.pos:
            if pos == self.pos:
                snake.add()
                self.new_pos()
                return
        self.render()

    def render(self):
        screen.blit(self.image, (5 + self.pos[0] * 26, 5 + self.pos[1] * 26))

class Grid:
    def __init__(self):
        global size
        size = (int((SCREENSIZE[0] - 9) / 26), int((SCREENSIZE[1] - 9) / 26))

    def update(self):
        screen.fill((0, 0, 255))
        pygame.draw.rect(screen, (120, 120, 120), Rect((3, 3), (SCREENSIZE[0] - 6, SCREENSIZE[1] - 6)))
        pygame.draw.rect(screen, (0, 0, 0), Rect((5, 5), (SCREENSIZE[0] - 10, SCREENSIZE[1] - 10)))

class Menu:
    def __init__(self):
        self.score = self.get_score()

    def get_score(self):
        try:
            with open('files\\score') as f:
                return f.read
        except:
            self.set_score(0)

    def set_score(self, score):
        with open('files\\score', 'w') as f:
            f.write(score)
        self.score = score


pygame.init()

screen = pygame.display.set_mode(SCREENSIZE, 0, 32)

grid = Grid()
snake = Snake()
apple = Apple()

running = True
index = 0

while running:
    prev = time.time()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    grid.update()
    apple.update()
    
    if snake.game_over:
        snake.render()
    else:
        if index % 10:
            snake.move()
            snake.render()
        else:
            snake.update()

    pygame.display.flip()

    try:
        time.sleep(0.1 / snake.speed + prev - time.time())
    except:
         pass

    index += 1
