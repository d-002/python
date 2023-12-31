import pygame
from pygame.locals import *
from random import randint

pygame.init()

screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
font = pygame.font.SysFont('consolas', 18)

time_passed = 0
bg_color = (255, 255, 0)
num_colors = 15

x = 320
y = 240

moveX = randint(20, 230)
moveY = 250 - moveX
if randint(0, 1):
    moveX = -moveX
if randint(0, 1):
    moveY = -moveY

def move_circle():
    global x, y, moveX, moveY
    
    x += moveX * time_passed
    y += moveY * time_passed

    if x < 50:
        moveX = abs(moveX)
    elif x > 590:
        moveX = -abs(moveX)
    if y < 50:
        moveY = abs(moveY)
    elif y > 430:
        moveY = -abs(moveY)
    
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == MOUSEWHEEL:
            num_colors += event.y
            num_colors = max(min(255, num_colors), 1)
    
    screen.fill(bg_color)

    move_circle()
    
    c = bg_color[0] - 255 / num_colors
    circle_color = (int(c), 255, 0)
    pygame.draw.circle(screen, circle_color, (int(x), int(y)), 50)

    text = font.render('You can see %d colors if you can see the circle' %(num_colors**3*8), 1, True)
    screen.blit(text, (20, 20))
    
    if num_colors == 255:
        comment = 'Stronger than the computer!'
    elif num_colors > 200:
        comment = 'Ur a mutant!'
    elif num_colors > 100:
        comment = 'NOICE!!!'
    elif num_colors > 50:
        comment = 'Nice!'
    elif num_colors < 10:
        comment = 'Come on!'
    else:
        comment = ''
    
    comment = font.render(comment, 0, True)
    screen.blit(comment, (20, 42))
    
    pygame.display.flip()
    time_passed = clock.tick() / 1000
