import time
import pygame
from pygame.locals import *
from math import sqrt
from random import randint, choice

pygame.init()

class Background:
    def __init__(self):
        self.bg = pygame.image.load('files\\background.png')
        self.size = (3000, 2000)
        self.rect = Rect((self.size[0] / 2, self.size[1] / 2), SIZE)

        self.border = pygame.Surface(SIZE, SRCALPHA)
        self.border.fill((0, 0, 0, 127))

    def update(self):
        self.render()

    def render(self):
        w, h = self.bg.get_size()
        screen.blit(self.bg, (int(-self.rect.x)%w, int(-self.rect.y)%h))         # centre
        screen.blit(self.bg, (int(-self.rect.x)%w - w, int(-self.rect.y)%h))     # left
        screen.blit(self.bg, (int(-self.rect.x)%w, int(-self.rect.y)%h - h))     # up
        screen.blit(self.bg, (int(-self.rect.x)%w - w, int(-self.rect.y)%h - h)) # up left
        screen.blit(self.bg, (int(-self.rect.x)%w + w, int(-self.rect.y)%h - h)) # up right
        screen.blit(self.bg, (int(-self.rect.x)%w - w, int(-self.rect.y)%h + h)) # down left
        screen.blit(self.bg, (int(-self.rect.x)%w + w, int(-self.rect.y)%h))     # right
        screen.blit(self.bg, (int(-self.rect.x)%w, int(-self.rect.y)%h + h))     # down
        screen.blit(self.bg, (int(-self.rect.x)%w + w, int(-self.rect.y)%h + h)) # down right

        if self.rect.x < 0:
            screen.blit(self.border, (int(-self.rect.x - SIZE[0]), 0))
        elif self.rect.x > self.size[0] - SIZE[0]:
            screen.blit(self.border, (int(self.size[0] - self.rect.x), 0))
        if self.rect.y < 0:
            if self.rect.x > self.size[0] - SIZE[0]:
                pos = (int(self.size[0] - self.rect.x - SIZE[0]), int(-self.rect.y - SIZE[1]))
                screen.blit(self.border, pos)
                screen.blit(self.border, (pos[0] - SIZE[0], pos[1]))
            elif self.rect.x < 0:
                pos = (int(-self.rect.x), int(-self.rect.y - SIZE[1]))
                screen.blit(self.border, pos)
                screen.blit(self.border, (pos[0] + SIZE[0], pos[1]))
            else:
                screen.blit(self.border, (0, int(-self.rect.y - SIZE[1])))
        elif self.rect.y > self.size[1] - SIZE[1]:
            if self.rect.x > self.size[0] - SIZE[0]:
                pos = (int(self.size[0] - self.rect.x - SIZE[0]), int(self.size[1] - self.rect.y))
                screen.blit(self.border, pos)
                screen.blit(self.border, (pos[0] - SIZE[0], pos[1]))
            elif self.rect.x < 0:
                pos = (int(-self.rect.x), int(self.size[1] - self.rect.y))
                screen.blit(self.border, pos)
                screen.blit(self.border, (pos[0] + SIZE[0], pos[1]))
            else:
                screen.blit(self.border, (0, int(self.size[1] - self.rect.y)))

class Snake:
    def __init__(self, automatic):
        self.automatic = automatic
        self.score = 0
        self.prev_candy = 0
        
        self.image = pygame.image.load('files\\skins\\%d.png' % randint(0, 3))
        self.base_w, self.base_h = self.w, self.h = self.image.get_size() # initial sze of the image
        self.rect = self.image.get_rect()

        self.prev_direction = 0 # do not turn too quickly

        if automatic:
            self.rect.x = randint(10, bg.size[0] - 50)
            self.rect.y = randint(10, bg.size[1] - 50)
        else:
            self.rect.x = bg.size[0] / 2 + SIZE[0] / 2 #
            self.rect.y = bg.size[1] / 2 + SIZE[1] / 2 # center of the map
        self.x = self.rect.x
        self.y = self.rect.y
        
        self.balls = [(self.rect.x, self.rect.y) for x in range(5)] # 5 balls to start

    def update(self):
        self.sprint = False
        
        self.w = self.base_w + self.score / 10
        self.h = self.base_h + self.score / 10
        
        # check if collide another snake
        for snake in snakes:
            if snake != self:
                for ball in snake.balls:
                    distance = sqrt((ball[0] - self.rect.x)**2 + (ball[1] - self.rect.y)**2)
                    if distance < (self.w + snake.w) / 2:
                        return self.die()
        
        # add or remove balls
        number = max(5, int(self.score / 5) + 4)
        to_add = number - len(self.balls)
        
        if to_add: # not the right number
            self.w, self.h = self.image.get_size()
            if to_add > 0:
                self.balls.append(self.balls[-1]) # add maximum one ball per frame
            else:
                self.balls.pop() # remove one ball per frame (enough)
        
        for b in range(len(self.balls)):
            if b:
                ball = self.balls[b]
                ball_ = self.balls[b-1]
                vec = pygame.math.Vector2((ball[0] - ball_[0], ball[1] - ball_[1]))
                if vec.length() > 20: # if a ball is too far from an other ball move it
                    vec = vec.normalize()
                    x = ball_[0] + vec[0] * 20
                    y = ball_[1] + vec[1] * 20
                    self.balls[b] = (x, y)

        # get the direction
        if self.automatic:
            move = self.opponent()
        else:
            move = self.player()

        if self.sprint:
            if time.time() - self.prev_candy >= 0.2:
                image = pygame.transform.scale(self.image, (20, 20))
                candies.append(Candy(self.balls[-1], image)) # leave a candy behind
                self.prev_candy = time.time()
                self.score -= 1
            speed = 400 # speed up
        else:
            speed = 200 # normal speed

        self.x += move[0] * speed * time_passed # need float values
        self.y += move[1] * speed * time_passed #
        self.rect.x = self.x # move according to the FPS
        self.rect.y = self.y #

        # do not go over the border (die)
        if self.rect.x < self.w / 2 or self.rect.x > bg.size[0] - self.w / 2:
            return self.die()
        if self.rect.y < self.h / 2 or self.rect.y > bg.size[1] - self.h / 2:
            return self.die()

        self.balls[0] = (self.rect.x, self.rect.y)

        self.render()
        
        self.prev_direction = move

    def player(self):
        bg.rect.x = self.rect.x - SIZE[0] / 2 # scroll the background to be in the center of the screen
        bg.rect.y = self.rect.y - SIZE[1] / 2 #

        if pygame.mouse.get_pressed()[0] and self.score: # sprint
            self.sprint = True
        else:
            self.sprint = False

        return head(self) # movement: follow the mouse cursor

    def opponent(self):
        nearest = [None, -1] # nearest candy found and distance to it
        for candy in candies:
            dist = sqrt((candy.rect.x - self.rect.x)**2 + (candy.rect.y - self.rect.y)**2)
            if dist < nearest[1] or nearest[1] < 0:
                nearest = [candy, dist]

        pos = (nearest[0].rect.x, nearest[0].rect.y)

        for snake in snakes: # check if there is a snake near
            if snake != self:
                for ball in snake.balls:
                    distance = sqrt((ball[0] - self.rect.x)**2 + (ball[1] - self.rect.y)**2)
                    if distance < 100:
                        return head(self, (self.rect.x - snake.rect.x, self.rect.y - snake.rect.y))
        
        return head(self, pos) # movement: to the nearest candy

    def die(self):
        image = pygame.transform.scale(self.image, (int(self.w / 1.5), int(self.h / 1.5)))
        
        for ball in range(0, len(self.balls), 2): # leave balls here
            candies.append(Candy(self.balls[ball], image, 5))
        
        if self.automatic:
            self.__init__(self.automatic)
        else:
            self.__init__(0)

    def render(self):
        image = pygame.transform.scale(self.image, (int(self.base_w + self.score / 10), int(self.base_h + self.score / 10)))
        balls = [self.balls[len(self.balls) - x - 1] for x in range(len(self.balls))] # reversed self.balls (draw the first ball in the foreground)
        for ball in balls:
            if bg.rect.colliderect(Rect(ball, image.get_size())): # visible in the screen
                screen.blit(image, (int(ball[0] - bg.rect.x - self.w / 2), int(ball[1] - bg.rect.y - self.h / 2)))

class Candy:
    def __init__(self, pos=None, image=None, worth=1):
        if image is None:
            self.image = choice(candy_images) # random color
        else:
            self.image = image
        
        self.worth = worth
        self.w, self.h = self.image.get_size()
        self.rect = self.image.get_rect()
        
        if pos is None:
            self.rect.x = randint(10, bg.size[0] - 10) # random position in the map
            self.rect.y = randint(10, bg.size[1] - 10) #
        else:
            self.rect.x, self.rect.y = pos

    def update(self):
        for snake in snakes:
            # move if a snake is near
            dist = sqrt((snake.rect.x - self.rect.x)**2 + (snake.rect.y - self.rect.y)**2)
            if 0 < dist < 50:
                speed = 5000 / dist * time_passed
                direction = head(self, (snake.rect.x, snake.rect.y))
                self.rect.x += direction[0] * speed
                self.rect.y += direction[1] * speed

            if dist < snake.h / 2: # get eaten
                candies.remove(self)
                if len(candies) < num_candies: # avoid making too many candies due to the snakes acceleration
                    candies.append(Candy())
                snake.score += self.worth
                return

        screen.blit(self.image, (int(self.rect.x - bg.rect.x - self.w / 2), int(self.rect.y - bg.rect.y - self.h / 2))) # render

def head(self, pos=None):
    if pos is None: # player control
        x, y = pygame.mouse.get_pos()
        vec = pygame.math.Vector2(x - SIZE[0] / 2, y - SIZE[1] / 2)
    else: # head to the specified position
        x, y = pos
        vec = pygame.math.Vector2(x - self.rect.x, y - self.rect.y)

    try:
        n = vec.normalize()
    except:
        n = (0, 0)

    return n # vector to point normalised

fullscreen = False

SIZE = (800, 450)
if fullscreen:
    screen = pygame.display.set_mode(SIZE, FULLSCREEN|SCALED)
else:
    screen = pygame.display.set_mode(SIZE)

screen_rect = Rect((0, 0), SIZE)

font = pygame.font.SysFont('consolas', 30)
title = pygame.font.SysFont('consolas', 100)
clock = pygame.time.Clock()

num_snakes = 10

candy_images = [pygame.image.load('files\\candies\\%s.png' %x) for x in range(5)]

bg = Background()
snakes = ([Snake(x) for x in range(num_snakes)])
candies = [Candy() for x in range(int(bg.size[0] * bg.size[1] / 100000))] # number of candies in function to the map size
num_candies = len(candies)

time_passed = 0

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    bg.update()
    for candy in candies:
        candy.update()
    for snake in snakes:
        snake.update()

    # render the score
    text = font.render('Score:', 0, (127, 127, 127))
    w = text.get_width() + 10
    screen.blit(text, (20, 50))
    text = title.render(str(snakes[0].score), 0, (100, 100, 100))
    screen.blit(text, (20 + w, 20))
    
    pygame.display.flip()
    time_passed = clock.tick(100) / 1000 # get the FPS
