import time
import pygame

from math import cos
from random import randint
from pygame.mixer import *
from pygame.locals import *

fullscreen = 0

class Paddle:
    def __init__(self):
        self.images = [pygame.image.load(r'files\paddle-normal-little.png'),\
                       pygame.image.load(r'files\paddle-normal.png'),\
                       pygame.image.load(r'files\paddle-normal-tall.png'),\
                       pygame.image.load(r'files\paddle-zap-little.png'),\
                       pygame.image.load(r'files\paddle-zap.png'),\
                       pygame.image.load(r'files\paddle-zap-tall.png')]
        self.dead = pygame.image.load(r'files\explosion.png')
        self.image = self.images[0]
        self.stateBase = [1, 0]
        self.state = [1, 0]
        self.x = 250
        self.y = 425
        self.moveX = 0

    def move(self):
        if self.image != self.dead:
            self.image = self.images[self.state[0] + 3 * self.state[1]]

        pressed_keys = pygame.key.get_pressed() # get user actions
        
        self.joystick = joystick

        if self.joystick is None:
            if pressed_keys[K_LEFT]:
                    self.moveX -= 2
            if pressed_keys[K_RIGHT]:
                self.moveX += 2

        else:
            if self.joystick.get_numaxes() and abs(self.joystick.get_axis(0)) > 0.2:
                self.moveX += self.joystick.get_axis(0) * 2
            
        if self.x - self.image.get_width() / 2 < 100:
            self.x = 100 + self.image.get_width() / 2
                 
        if self.x + self.image.get_width() / 2 > 400:
            self.x = 400 - self.image.get_width() / 2
                
        self.moveX = self.moveX * 0.8
        self.x += self.moveX
        self.render()

    def render(self):
        if self.image != self.dead:
            self.image = self.images[self.state[0] + 3 * self.state[1]]
        blit(self.image, self.x - self.image.get_width() / 2, self.y - self.image.get_height() / 2)

class Opponent:
    def __init__(self, pos):
        global free
        self.pos = pos
        self.images = [pygame.image.load(r'files\paddle-normal-little.png'),\
                       pygame.image.load(r'files\paddle-normal.png'),\
                       pygame.image.load(r'files\paddle-normal-tall.png'),\
                       pygame.image.load(r'files\paddle-zap-little.png'),\
                       pygame.image.load(r'files\paddle-zap.png'),\
                       pygame.image.load(r'files\paddle-zap-tall.png')]
        self.dead = pygame.image.load(r'files\explosion.png')
        self.image = self.images[0]
        self.stateBase = [1, 0]
        self.state = [1, 0]
        free[self.pos] = False
        for image in range(len(self.images)):
            if self.pos == 'top': # set position
                self.images[image] = pygame.transform.rotate(self.images[image], 180)
                self.x = 250
                self.y = 75
            elif self.pos == 'right':
                self.images[image] = pygame.transform.rotate(self.images[image], 90)
                self.x = 425
                self.y = 250
            elif self.pos == 'left':
                self.images[image] = pygame.transform.rotate(self.images[image], 270)
                self.x = 75
                self.y = 250

    def move(self):
        if self.pos == 'top': # set position
            speedX = abs(ball.x - self.x)
            if speedX > ball.speedBase / 3:
                if self.x > ball.x:
                    self.x += -ball.speedBase / 2
                else:
                    self.x += ball.speedBase / 2
            else:
                self.x += ball.x - self.x
        else:
            speedY = abs(ball.y - self.y)
            if speedY > ball.speedBase / 2:
                if self.y > ball.y:
                    self.y += -ball.speedBase / 2
                else:
                    self.y += ball.speedBase / 2
            else:
                self.y += ball.y - self.y
            
        if self.pos == 'top': # correct position
            if self.x - self.image.get_width() / 2 < 100:
                self.x = 100 + self.image.get_width() / 2
            if self.x + self.image.get_width() / 2 > 400:
                self.x = 400 - self.image.get_width() / 2
        else:
            if self.y - self.image.get_height() / 2 < 100:
                self.y = 100 + self.image.get_height() / 2
            if self.y + self.image.get_height() / 2 > 400:
                self.y = 400 - self.image.get_height() / 2
        self.render()

    def render(self):
        if self.image != self.dead:
            self.image = self.images[self.state[0] + 3 * self.state[1]]
        blit(self.image, self.x - self.image.get_width() / 2, self.y - self.image.get_height() / 2)
        
    def delete(self):
        try:
            opponents.remove(self)
            free[self.pos] = True
        except:
            pass
        

class Ball:
    def __init__(self, speed=5, clone=False):
        self.gr = 0
        self.lastTouch = 'bottom'
        self.speedBase = speed
        self.speed = speed
        self.images = [r'files\ball\1.png',
                       r'files\ball\2.png',
                       r'files\ball\3.png',
                       r'files\ball\4.png',
                       r'files\ball\alpha 1.png',
                       r'files\ball\alpha 2.png',
                       r'files\ball\alpha 3.png',
                       r'files\ball\alpha 4.png']
        self.images = [pygame.image.load(x).convert_alpha() for x in self.images]
        self.image = self.images[0]
        self.sound_paddle = pygame.mixer.Sound(r'files\paddle.wav')
        self.sound_edge = pygame.mixer.Sound(r'files\edge.wav')
        self.sound_goal = pygame.mixer.Sound(r'files\goal.wav')
        self.sound_corner = pygame.mixer.Sound(r'files\corner.wav')
        self.sound_zap = pygame.mixer.Sound(r'files\zap.wav')
        if clone:
            self.x = ball.x
            self.y = ball.y
            self.moveX = speed / 2
            self.moveY = speed / 2
        else:
            self.reset(False)

    def move(self):
        self.bounce()
        self.collided()
        if self.gr:
            self.gravity()
        elif abs(abs(self.moveX) + abs(self.moveY) - self.speed) > 0:
            try:
                factor = self.speed / (abs(self.moveX) + abs(self.moveY))
            except:
                factor = 10
            self.moveX *= factor # reset speed when the effects are stopping
            self.moveY *= factor
        self.x += self.moveX
        self.y += self.moveY
        self.render()

    def bounce(self):
        global ball
        p = None
        if self.x < 50:
            if self.x < 30:
                self.sound_goal.play()
                p = find('left')
            elif free['left'] or self.y < 100 or self.y > 400:
                self.moveX = -self.moveX
                self.x = 50
                self.sound_edge.play()
        elif self.x > 450:
            if self.x > 470:
                self.sound_goal.play()
                p = find('right')
            elif free['right'] or self.y < 100 or self.y > 400:
                self.moveX = -self.moveX
                self.x = 450
                self.sound_edge.play()
        if self.y < 50:
            if self.y < 30:
                self.sound_goal.play()
                p = find('top')
            elif free['top'] or self.x < 100 or self.x > 400:
                self.moveY = -self.moveY
                self.y = 50
                self.sound_edge.play()
        elif self.y > 450:
            if self.y > 470:
                self.sound_goal.play()
                p = paddle
            elif self.x < 100 or self.x > 400:
                self.moveY = -self.moveY
                self.y = 450
                self.sound_edge.play()
        if p is not None:
            if self == ball and len(balls) < 2:
                for x in range(10):
                    if x % 2:
                        p.image = p.dead
                    else:
                        p.image = p.images[p.state[0] + 3 * p.state[1]]
                    blit(p.image, p.x - p.image.get_width() / 2, p.y - p.image.get_height() / 2)
                    blit(edge, 0, 0)
                    pygame.display.update()
                    time.sleep(0.05)
                    if p != paddle:
                        p.delete()
                p.state = p.stateBase
                p.image = p.images[p.stateBase[0] + 3 * p.stateBase[1]]
                self.reset()
            elif self == ball:
                balls.remove(self)
                ball = balls[0]
            else:
                try:
                    balls.remove(self)
                except:
                    self.reset()
        self.corners()

    def move10times(self): # after touching a corner
        for x in range(10):
            self.x += self.moveX
            self.y += self.moveY
            self.render()
            blit(background, 0, 0)
            paddle.move()
            for opponent in opponents:
                opponent.render()
            power.update()
            self.move()
            blit(edge, 0, 0)
            update_screen()
            pygame.display.update()
            
    def corners(self):
        if self.x + self.y < 150:
            self.x = 75
            self.y = 75
            self.moveX = self.speed / 2
            self.moveY = self.speed / 2
            self.sound_corner.play()
            self.move10times()
            number = randint(-10, 10) / 10
            self.moveX = self.speed / 2 - number
            self.moveY = self.speed / 2 + number

        elif 500 - self.x + self.y < 150:
            self.x = 425
            self.y = 75
            self.moveX = -self.speed / 2
            self.moveY = self.speed / 2
            self.sound_corner.play()
            self.move10times()
            number = randint(-10, 10) / 10
            self.moveX = -self.speed / 2 + number
            self.moveY = self.speed / 2 + number

        elif self.x + 500 - self.y < 150:
            self.x = 75
            self.y = 425
            self.moveX = self.speed / 2
            self.moveY = -self.speed / 2
            self.sound_corner.play()
            self.move10times()
            number = randint(-10, 10) / 10
            self.moveX = self.speed / 2 + number
            self.moveY = -self.speed / 2 + number

        elif self.x + self.y > 850:
            self.x = 425
            self.y = 425
            self.moveX = -self.speed / 2
            self.moveY = -self.speed / 2
            self.sound_corner.play()
            self.move10times()
            number = randint(-10, 10) / 10
            self.moveX = -self.speed / 2 + number
            self.moveY = -self.speed / 2 - number

    def collided(self):
        global free
        if self.x + self.image.get_width() / 2 > paddle.x - paddle.image.get_width() / 2:
            if self.x - self.image.get_width() / 2 < paddle.x + paddle.image.get_width() / 2:
                if self.y + self.image.get_height() / 2 > paddle.y - paddle.image.get_height() / 3:
                    if self.y - self.image.get_height() / 2 < paddle.y + paddle.image.get_height() / 2:
                        self.sound_paddle.play()
                        self.moveX += (self.x - paddle.x) / 5 + 0.5 # touch a paddle
                        if abs(self.moveX) > self.speed:
                            self.moveX = self.moveX / abs(self.moveX) * self.speed - 1
                        self.moveY = -abs(self.moveY)
                        if abs(self.moveY) < 1:
                            try:
                                self.moveY = self.moveY / abs(self.moveY) * 2
                            except:
                                self.moveY = 2
                        if self.gr == 3:
                            self.moveY = self.speed * -1.5
                        if paddle.state[1]:
                            self.sound_zap.play()
                            self.speed = 2 * self.speedBase
                        else:
                            self.speed = self.speedBase
                        self.lastTouch = 'bottom'
        if not free['top']:
            opponent = find('top')
            if self.x + self.image.get_width() / 2 > opponent.x - opponent.image.get_width() / 2:
                if self.x - self.image.get_width() / 2 < opponent.x + opponent.image.get_width() / 2:
                    if self.y + self.image.get_height() / 2 > opponent.y - opponent.image.get_height() / 2:
                        if self.y - self.image.get_height() / 2 < opponent.y + opponent.image.get_height() / 3:
                            self.sound_paddle.play()
                            self.moveX += (self.x - opponent.x) / 5 - 0.1 # touch a paddle
                            if abs(self.moveX) > self.speed:
                                self.moveX = self.moveX / abs(self.moveX) * self.speed - 1
                            self.moveY = abs(self.moveY)
                            if abs(self.moveY) < 1:
                                try:
                                    self.moveY = self.moveY / abs(self.moveY) * 2
                                except:
                                    self.moveY = 2
                            if self.gr:
                                self.moveY = self.speed * 1.5
                            if find('top').state[1]:
                                self.sound_zap.play()
                                self.speed = 2 * self.speedBase
                            else:
                                self.speed = self.speedBase
                            self.lastTouch = 'top'
        if not free['right']:
            opponent = find('right')
            if self.x + self.image.get_width() / 2 > opponent.x - opponent.image.get_width() / 2:
                if self.x - self.image.get_width() / 2 < opponent.x + opponent.image.get_width() / 3:
                    if self.y + self.image.get_height() / 2 > opponent.y - opponent.image.get_height() / 2:
                        if self.y - self.image.get_height() / 2 < opponent.y + opponent.image.get_height() / 2:
                            self.sound_paddle.play()
                            self.moveY += (self.y - opponent.y) / 5 - 0.1 # touch a paddle
                            if abs(self.moveY) > self.speed:
                                self.moveY = self.moveY / abs(self.moveY) * self.speed - 1
                            self.moveX = -abs(self.moveX)
                            if abs(self.moveX) < 1:
                                try:
                                    self.moveX = self.moveX / abs(self.moveX) * 2
                                except:
                                    self.moveX = -2
                            if self.gr == 2:
                                self.moveX = self.speed * -1.5
                            if find('right').state[1]:
                                self.sound_zap.play()
                                self.speed = 2 * self.speedBase
                            else:
                                self.speed = self.speedBase
                            self.lastTouch = 'right'
        if not free['left']:
            opponent = find('left')
            if self.x + self.image.get_width() / 2 > opponent.x - opponent.image.get_width() / 3:
                if self.x - self.image.get_width() / 2 < opponent.x + opponent.image.get_width() / 2:
                    if self.y + self.image.get_height() / 2 > opponent.y - opponent.image.get_height() / 2:
                        if self.y - self.image.get_height() / 2 < opponent.y + opponent.image.get_height() / 2:
                            self.sound_paddle.play()
                            self.moveY += (self.y - opponent.y) / 5 - 0.1 # touch a paddle
                            if abs(self.moveY) > self.speed:
                                self.moveY = self.moveY / abs(self.moveY) * self.speed - 1
                            self.moveX = abs(self.moveX)
                            if abs(self.moveX) < 1:
                                try:
                                    self.moveX = self.moveX / abs(self.moveX) * 2
                                except:
                                    self.moveX = 2
                            if self.gr == 4:
                                self.moveX = self.speed * 1.5
                            if find('left').state[1]:
                                self.sound_zap.play()
                                self.speed = 2 * self.speedBase
                            else:
                                self.speed = self.speedBase
                            self.lastTouch = 'left'
                            
    def gravity(self):
        if self.gr == 1: # gravity to up
            self.moveY -= 0.25
        elif self.gr == 2: # gravity to right
            self.moveX += 0.25
        elif self.gr == 3: # gravity to Down
            self.moveY += 0.25
        else: # gravity to left
            self.moveX -= 0.25

    def render(self):
        blit(self.image, self.x - self.image.get_width() / 2, self.y - self.image.get_height() / 2 - 1)
        
    def reset(self, sleep=True):
        self.x = 250
        self.y = 250
        self.moveX = 1
        self.moveY = 1
        self.speed = self.speedBase

        blit(background, 0, 0)
        paddle.render()
        for opponent in opponents:
            opponent.render()
        blit(edge, 0, 0)
        pygame.display.update()
        
        if sleep:
            global running
            prev = time.time()
            while time.time() - prev < 1: # update the paddle while a few moments
                for event in pygame.event.get():
                    if event.type == QUIT:
                        running = False
                blit(background, 0, 0)
                paddle.move()
                for opponent in opponents:
                    opponent.move()
                power.update()
                blit(edge, 0, 0)
                pygame.display.update()
                time.sleep(0.015)
        self.x = 60 + 380 * randint(0, 1)
        self.y = 60

class Powerups:
    def __init__(self, *args):
        self.imageGravity = pygame.image.load(r'files\powerups\gravity.png')
        self.imageWave = pygame.image.load(r'files\powerups\wave.png')
        self.imageWaveDirection = pygame.image.load(r'files\powerups\wave direction.png')
        self.imageTall = pygame.image.load(r'files\powerups\tall.png')
        self.imageLittle = pygame.image.load(r'files\powerups\little.png')
        self.imageZap = pygame.image.load(r'files\powerups\zap.png')
        self.imageMultiball = pygame.image.load(r'files\powerups\multiball.png')
        self.sound_powerup = pygame.mixer.Sound(r'files\powerups\powerup.wav')
        self.sound_gravity = pygame.mixer.Sound(r'files\powerups\gravity.wav')
        self.sound_wave = pygame.mixer.Sound(r'files\powerups\wave.wav')
        self.sound_wave_direction = pygame.mixer.Sound(r'files\powerups\wave direction.wav')
        self.sound_tall = pygame.mixer.Sound(r'files\powerups\tall.wav')
        self.sound_little = pygame.mixer.Sound(r'files\powerups\little.wav')
        self.sound_zap = pygame.mixer.Sound(r'files\powerups\zap.wav')
        self.sound_multiball = pygame.mixer.Sound(r'files\powerups\multiball.wav')
        self.sound_new_direction = pygame.mixer.Sound(r'files\powerups\new direction.wav')
        self.powerups = []
        self.pos = []
        self.times = []
        self.touched = []
        self.infoTouch = []
        self.duration = 10
        self.start = time.time()
        for x in range(len(args)):
            if x % 2:
                self.powerups.append(args[x])
            else:
                self.times.append(args[x])
            self.touched.append(False)
            self.infoTouch.append(['', 0])
        self.set_pos()
        self.reset()

    def touch(self):
        for powerup in range(len(self.powerups)):
            if ball.x + ball.image.get_width() / 2 > self.pos[powerup][0] and ball.x - ball.image.get_width() / 2 < self.pos[powerup][0] + 35:
                if ball.y + ball.image.get_height() / 2 > self.pos[powerup][1] and ball.y - ball.image.get_height() / 2 < self.pos[powerup][1] + 35: # if the ball touchs the powerup
                    if self.times[powerup] < time.time() - self.start < self.times[powerup] + self.duration: # if the powerup is active
                        if not self.touched[powerup]:
                            self.sound_powerup.play()
                            self.touched[powerup] = True # active the effect
                            self.infoTouch[powerup][1] = time.time()
                            self.infoTouch[powerup][0] = find(ball.lastTouch)
                            if self.powerups[powerup] == 'gravity':
                                self.sound_gravity.play()
                                self.gravity_()
                            elif self.powerups[powerup] == 'wave':
                                self.sound_wave.play()
                                self.wave()
                            elif self.powerups[powerup] == 'wave_direction':
                                self.sound_wave_direction.play()
                                self.wave_direction()
                            elif self.powerups[powerup] == 'tall':
                                self.sound_tall.play()
                                self.tall()
                                self.infoTouch[powerup][0].state[0] = 2
                            elif self.powerups[powerup] == 'little':
                                self.sound_little.play()
                                self.little()
                                self.infoTouch[powerup][0].state[0] = 0
                            elif self.powerups[powerup] == 'zap':
                                self.sound_zap.play()
                                self.zap()
                            elif self.powerups[powerup] == 'multiball':
                                self.sound_multiball.play()
                                balls.append(Ball(speed, True))

    def set_pos(self):
        self.pos = []
        for powerup in range(len(self.powerups)):
            self.pos.append((randint(140, 340), randint(140, 340))) # init new positions for the powerups
            
    def update(self):
        for powerup in range(len(self.powerups)):
            if self.times[powerup] < time.time() - self.start < self.times[powerup] + self.duration:
                self.render(powerup) # render all the powerups which are active
                self.touch()
                if self.touched[powerup]:
                    if self.powerups[powerup] == 'wave':
                        self.wave()
                    elif self.powerups[powerup] == 'wave_direction':
                        self.wave_direction()
            elif time.time() - self.infoTouch[powerup][1] > self.duration + 0.5 and self.infoTouch[powerup][1]: # desactivate effects
                self.touched[powerup] = False
                self.infoTouch[powerup][1] = 0
                if self.powerups[powerup] == 'gravity':
                    ball.gr = 0
                elif self.powerups[powerup] == 'wave':
                    ball.speed = ball.speedBase
                elif self.powerups[powerup] == 'wave_direction':
                    ball.speed = ball.speedBase
                elif self.powerups[powerup] == 'tall':
                    if self.infoTouch[powerup][0].state[0] == 2:
                        self.infoTouch[powerup][0].state[0] = self.infoTouch[powerup][0].stateBase[0]
                elif self.powerups[powerup] == 'little':
                    if self.infoTouch[powerup][0].state[0] == 0:
                        self.infoTouch[powerup][0].state[0] = self.infoTouch[powerup][0].stateBase[0]
                elif self.powerups[powerup] == 'zap':
                    self.infoTouch[powerup][0].state[1] = self.infoTouch[powerup][0].stateBase[1]
        if time.time() - self.start > self.times[-1] + self.duration:
            self.reset()

    def render(self, powerup):
        if not self.touched[powerup]:
            if self.powerups[powerup] == 'gravity':
                image = self.imageGravity
            elif self.powerups[powerup] == 'wave':
                image = self.imageWave
            elif self.powerups[powerup] == 'wave_direction':
                image = self.imageWaveDirection
            elif self.powerups[powerup] == 'tall':
                image = self.imageTall
            elif self.powerups[powerup] == 'little':
                image = self.imageLittle
            elif self.powerups[powerup] == 'zap':
                image = self.imageZap
            elif self.powerups[powerup] == 'multiball':
                image = self.imageMultiball
            else:
                raise BaseException('%s powerup is not known' % powerup)
            blit(image, self.pos[powerup][0], self.pos[powerup][1])

    def reset(self):
        self.start = time.time()
        self.set_pos()

    def gravity_(self): # effect gravity to the last paddle which touchs the ball
        if ball.lastTouch == 'top':
            ball.gr = 1
        elif ball.lastTouch == 'right':
            ball.gr = 2
        elif ball.lastTouch == 'bottom':
            ball.gr = 3
        else:
            ball.gr = 4

    def wave(self):
        ball.speed = ball.speedBase + 3 * cos(4 * time.time())

    def wave_direction(self):
        if int(time.time() * 20) % 30 == 0:
            ball.moveX = randint(-int(ball.speedBase), int(ball.speedBase)) / 2
            ball.moveY = (randint(0, 1) - 0.5) * 2 * (10 - abs(ball.moveX)) / 2
            self.sound_new_direction.play()

    def tall(self):
        find(ball.lastTouch).state[0] = 1

    def little(self):
        find(ball.lastTouch).state[0] = -1

    def zap(self):
        find(ball.lastTouch).state[1] = 1

def find(pos):
    for opponent in opponents:
        if opponent.pos == pos:
            return opponent
    return paddle

def blit(sprite, x, y):
    try:
        screen.blit(sprite, (int(x), int(y)))
    except:
        pass

def update_screen():
    global prev
    pygame.display.flip()
    
    try:
        time.sleep(0.015 - time.time() + prev)
    except:
        pass
    prev = time.time()

def create_screen():
    global screen
    if fullscreen:
        screen = pygame.display.set_mode((500, 500), FULLSCREEN|SCALED)
        pygame.mouse.set_visible(0)
    else:
        screen = pygame.display.set_mode((500, 500))
        pygame.mouse.set_visible(1)
    pygame.display.update()
    try:
        if power.start:
            time.sleep(2)
            blit(background, 0, 0)
            paddle.move()
            for opponent in opponents:
                opponent.move()
            power.update()
            ball.move()
            blit(edge, 0, 0)
            update_screen()
            if not pause:
                sound_pause.play().wait_done()
    except:
        pass


pygame.init()

pygame.mixer.music.load(r'files\music.mp3')
pygame.mixer.music.play(loops=-1)
sound_pause = pygame.mixer.Sound(r'files\pause.wav')
font = pygame.font.SysFont('comicsansms', 50)

create_screen()
pygame.display.set_caption('Pong')
background = pygame.image.load(r'files\background.png').convert()
edge = pygame.image.load(r'files\edge.png').convert_alpha()
image_pause = pygame.image.load(r'files\pause.png').convert_alpha()

joystick = None

if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

free = {'top': True, 'right': True, 'left': True}
opponents = []
youwin = False
running = True
x = 0
speed = 5
pause = 0
prev = time.time()

paddle = Paddle()
balls = [Ball(speed)]
ball = balls[0]
power = Powerups(5, 'gravity', 10, 'wave_direction', 15, 'wave', 20, 'tall', 25, 'little', 30, 'zap', 35, 'multiball')
opponents.append(Opponent('top'))
opponents.append(Opponent('right'))
opponents.append(Opponent('left'))

blit(background, 0, 0)
paddle.move()
for opponent in opponents:
    opponent.move()
blit(edge, 0, 0)
pygame.display.update()
time.sleep(1)

while running: # mainloop

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == JOYBUTTONDOWN:
            if event.button == 6:
                fullscreen = 1 - fullscreen
                create_screen()
            elif event.button == 7:
                pause = 1 - pause
                if not pause:
                    blit(background, 0, 0)
                    paddle.move()
                    for opponent in opponents:
                        opponent.move()
                    power.update()
                    ball.move()
                    blit(edge, 0, 0)
                    update_screen()
                    sound_pause.play().wait_done()
                    
    pressed_keys = pygame.key.get_pressed()

    if pressed_keys[K_ESCAPE]:
        pause = 1 - pause
        if pause:
            blit(image_pause, 0, 0)
            update_screen()
        else:
            blit(background, 0, 0)
            paddle.move()
            for opponent in opponents:
                opponent.move()
            power.update()
            ball.move()
            blit(edge, 0, 0)
            update_screen()
            sound_pause.play().wait_done()
        time.sleep(0.5)
    elif pressed_keys[K_F11]:
        fullscreen = 1 - fullscreen
        create_screen()

    if joystick is None:
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
    elif pygame.joystick.get_count() < 1:
        joystick = None

    if pause:
        blit(image_pause, 0, 0)
    else:
        blit(background, 0, 0)
        paddle.move()
        for opponent in opponents:
            opponent.move()
        power.update()
        for b in balls:
            b.move()
        blit(edge, 0, 0)

    if not len(opponents):
        youwin = True
    if youwin:
        text = font.render('You win!', 0, (127, 127, 127))
        w, h = text.get_size()
        blit(text, 252 - w / 2, 202 - h / 2)
        text = font.render('You win!', 0, (255, 255, 255))
        w, h = text.get_size()
        blit(text, 250 - w / 2, 200 - h / 2)

    update_screen()

pygame.quit()
exit()
