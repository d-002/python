import time
import pygame
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((500, 650), 0, 32)
font = pygame.font.SysFont('consolas', 15)

class Ball:
    def __init__(self, pattern, decay):
        self.pattern = pattern
        self.start = time.time() + decay
        self.image = pygame.image.load('ball.png').convert_alpha()

        self.left = (150, 600)
        self.right = (350, 600)

        if self.pattern[0][0] == 1:
            self.x, self.y = self.left
        else:
            self.x, self.y = self.right
        self.moveX = 0
        self.moveY = 0
        self.index = 0
        
    def _move(self, goal):
        if goal[0] < 0 and (self.x < self.left[0] or self.y > self.left[1]):
            global prevLeft
            prevLeft = time.time()
            self.x, self.y = self.left
            self.index += 1
            self.moveX = 0
            self.moveY = 0
        elif self.x > self.right[0] or self.y > self.right[1]:
            global prevRight
            prevRight = time.time()
            self.x, self.y = self.right
            self.index += 1
            self.moveX = 0
            self.moveY = 0
        else:
            if not self.moveY and self.y >= self.left[1]:
                self.moveY = goal[1] * -5
            try:
                self.moveX = goal[0] * 4 / goal[1]
            except:
                self.moveX = 0
            self.moveY += 0.2
    
    def move(self):
        if time.time() - self.start >= 0:
            self.x += self.moveX
            self.y += self.moveY
            self._move(self.pattern[(self.index + 1) % len(self.pattern)])
            self.render()

    def render(self):
        screen.blit(self.image,
                    (int(self.x - self.image.get_width() / 2),
                     int(self.y - self.image.get_height() / 2)))


def reset():
    global start, number, SPEED, balls
    start = time.time()
    number = patterns[PATTERN][0]
    SPEED = 100
    balls = [Ball(patterns[PATTERN][x + 1], x * SPEED / 100 / number) for x in range(number)]

left = pygame.image.load('hand.png').convert_alpha()
right = pygame.transform.flip(left, 1, 0)
left_ = pygame.image.load('hand_.png').convert_alpha()
right_ = pygame.transform.flip(left_, 1, 0)

prevLeft = 0
prevRight = 0

patterns = [[2, [(1, 2), (-1, 1)]],
            [3, [(1, 2), (-1, 1)]],
            [4, [(1, 2), (-1, 1)]],
            [5, [(1, 2), (-1, 1)]],
            [2, [(1, 1), (-1, 1), (1, 3), (-1, 1)], [(-1, 3), (1, 1), (-1, 1), (1, 1)]],
            [2, [(1, 3), (-1, 1), (1, 2), (-1, 1)], [(-1, 2), (1, 1), (-1, 3), (1, 1)]],
            [2, [(1, 3), (-1, 2), (1, 1), (-1, 3), (1, 2), (-1, 1)]],
            [3, [(1, 3), (-1, 2), (1, 1), (-1, 3), (1, 2), (-1, 1)]],
            [4, [(1, 2), (-1, 1)], [(-1, 2), (1, 1)]],
            [6, [(1, 2), (-1, 1)], [(-1, 2), (1, 1)]],
            [4, [(1, 3), (-1, 1), (1, 2), (-1, 1)], [(1, 2), (-1, 1), (1, 3), (-1, 1)], [(-1, 3), (1, 1), (-1, 2), (1, 1)], [(-1, 2), (1, 1), (-1, 3), (1, 1)]],
            [8, [(1, 3), (-1, 1), (1, 2), (-1, 1)], [(1, 2), (-1, 1), (1, 3), (-1, 1)], [(-1, 3), (1, 1), (-1, 2), (1, 1)], [(-1, 2), (1, 1), (-1, 3), (1, 1)]]]

PATTERN = 0
for p in range(len(patterns)):
    if len(patterns[p]) - 1 != patterns[p][0]:
        LEN = -len(patterns[p]) + 1
        for x in range(patterns[p][0] - len(patterns[p]) + 1):
            patterns[p].append(patterns[p][LEN])

reset()

while True:
    prev = time.time()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            PATTERN += 1
            PATTERN = PATTERN % len(patterns)
            reset()
            
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[K_RIGHT]:
        if SPEED < 200:
            SPEED += 1
    elif pressed_keys[K_LEFT]:
        if SPEED > 1:
            SPEED -= 1

    screen.fill((255, 255, 255))

    if time.time() - prevLeft < 0.5 / patterns[PATTERN][0]:
        screen.blit(left_, (int(150 - left.get_width() / 2), int(600 - left.get_width() / 2)))
    else:
        screen.blit(left, (int(150 - left.get_width() / 2), int(600 - left.get_width() / 2)))
    if time.time() - prevRight < 0.5 / patterns[PATTERN][0]:
        screen.blit(right_, (int(350 - right.get_width() / 2), int(600 - right.get_width() / 2)))
    else:
        screen.blit(right, (int(350 - right.get_width() / 2), int(600 - right.get_width() / 2)))
        
    pygame.draw.rect(screen, (230, 230, 230), Rect((50, 50), (400, 20)))
    pygame.draw.rect(screen, (150, 200, 150), Rect((50, 50), (2 * SPEED, 20)))
    pygame.draw.line(screen, (0, 0, 0), (49 + 2 * SPEED, 30), (49 + 2 * SPEED, 69))
    text = font.render('Speed: %d%%' %SPEED, 0, (0, 0, 0))
    screen.blit(text, (int(45 + 2 * SPEED - text.get_width()), int(45 - text.get_height())))
    text = font.render('Pattern %d of %d' %(PATTERN + 1, len(patterns)), 0, (0, 0, 0))
    screen.blit(text, (int(250 - text.get_width() / 2), 100))
    text = font.render('Hit arrows to change speed and click to switch pattern', 0, (0, 0, 0))
    screen.blit(text, (int(250 - text.get_width() / 2), int(595 - text.get_height())))
    
    for ball in balls:
        ball.move()
    pygame.display.flip()
    try:
        time.sleep(0.5 / SPEED - time.time() + prev)
    except:
        pass
