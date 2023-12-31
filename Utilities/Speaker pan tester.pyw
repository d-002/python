import pygame
from pygame.locals import *

pygame.init()

screen = pygame.display.set_mode((500, 300), 0, 32)
pygame.display.set_caption('Speaker tester')
clock = pygame.time.Clock()
font = pygame.font.SysFont('consolas', 20)

c = pygame.mixer.Sound('pan.wav').play()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    mouse_pos = pygame.mouse.get_pos()
    right = mouse_pos[0] / 500
    left = 1 - right
    c.set_volume(left, right)
    
    screen.fill((0, 0, 0))

    pygame.draw.circle(screen, (0, 0, 255), mouse_pos, 20)
    pygame.draw.circle(screen, (0, 0, 200), mouse_pos, 18)
    pygame.draw.circle(screen, (0, 0, 100), mouse_pos, 15)
    pygame.draw.circle(screen, (0, 0, 50), mouse_pos, 10)

    pygame.draw.circle(screen, (200, 200, 255), (30, 150), int(20 * (left + 0.2)))
    pygame.draw.circle(screen, (200, 200, 255), (470, 150), int(20 * (right + 0.2)))
    
    screen.blit(font.render('set_volume(%.3f, %.3f)' % (left, right), 0, (200, 200, 255), True), (20, 20))
    pygame.display.flip()
    
    clock.tick(60)
