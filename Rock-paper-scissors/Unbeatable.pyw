import pygame, random, time
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('Rock-paper-scissors')
font = pygame.font.SysFont('helevtica', 20)
win_font = pygame.font.SysFont('helevtica', 50)

def player():
    if played is None:
        image = none_image
    elif played == 'rock':
        image = rock_image
    elif played == 'paper':
        image = paper_image
    elif played == 'scissors':
        image = scissors_image
    
    x, y = player_pos
    w, h = image.get_size()
    screen.blit(image, (int(x - w / 2), int(y - h / 2)))
    
    if win() == 'player':
        text = win_font.render('WIN!', 0, (0, 0, 0))
        w = text.get_width()
        screen.blit(text, (int(x - w / 2), int(y + h / 2 + 5)))
    
def computer():
    if computered is None:
        image = none_image
    elif computered == 'rock':
        image = rock_image
    elif computered == 'paper':
        image = paper_image
    elif computered == 'scissors':
        image = scissors_image
    
    x, y = computer_pos
    w, h = image.get_size()
    screen.blit(image, (int(x - w / 2), int(y - h / 2)))
    
    if win() == 'computer':
        text = win_font.render('WIN!', 0, (0, 0, 0))
        w = text.get_width()
        screen.blit(text, (int(x - w / 2), int(y + h / 2 + 5)))

def win():
    if played == 'rock':
        if computered == 'paper':
            return 'computer'
        elif computered == 'scissors':
            return 'player'
    elif played == 'paper':
        if computered == 'rock':
            return 'player'
        elif computered == 'scissors':
            return 'computer'
    elif played == 'scissors':
        if computered == 'paper':
            return 'player'
        elif computered == 'rock':
            return 'computer'
    return 'draw'

def display_scores():
    # mask the scores with a white rect
    pygame.draw.rect(screen, (255, 255, 255), Rect((0, 400), (640, 80)))
    
    text = win_font.render(str(player_score), 0, (0, 127, 0))
    w = text.get_width()
    screen.blit(text, (int(player_pos[0] - w / 2), 400))
    
    text = win_font.render(str(draws), 0, (200, 127, 0))
    w = text.get_width()
    screen.blit(text, (int(320 - w / 2), 400))
    
    text = win_font.render(str(computer_score), 0, (127, 0, 0))
    w = text.get_width()
    screen.blit(text, (int(computer_pos[0] - w / 2), 400))

def play():
    global played, computered, player_score, computer_score, draws, last_winner
    played = None
    computered = None
    player()
    computer()
    display_scores()
    pygame.display.flip()
    while played is None:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == MOUSEBUTTONDOWN:
                if rock_rect.collidepoint(event.pos):
                    played = 'rock'
                elif paper_rect.collidepoint(event.pos):
                    played = 'paper'
                elif scissors_rect.collidepoint(event.pos):
                    played = 'scissors'
        
        button('Rock', rock_rect)
        button('Paper', paper_rect)
        button('Scissors', scissors_rect)

    AI()

    plays.append(played)
    if win() == 'player':
        player_score += 1
        last_winner = 'player'
    elif win() == 'computer':
        computer_score += 1
        last_winner = 'computer'
    else:
        draws += 1
        last_winner = 'draw'

    display_scores()
    
    start = time.time()
    while time.time() - start < 1:
        player()
        computer()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.exit()
                quit()

def AI():
    global computered
    if played == 'rock':
        computered = 'paper'
    elif played == 'paper':
        computered = 'scissors'
    elif played == 'scissors':
        computered = 'rock'

def button(text, rect):
    size = (rect.width, rect.height)
    pos = (rect.x, rect.y)
    surface = pygame.Surface(size)
    surface.fill((200, 200, 200))
    text = font.render(text, 0, (255, 255, 255))
    w, h = text.get_size()
    surface.blit(text, (int((rect.width - w) / 2), int((rect.height - h) / 2)))
    screen.blit(surface, pos)
    pygame.display.flip()

player_score = 0
draws = 0
computer_score = 0
last_winner = None
plays = []

none_image = pygame.image.load('files\\none.png')
rock_image = pygame.image.load('files\\rock.png')
paper_image = pygame.image.load('files\\paper.png')
scissors_image = pygame.image.load('files\\scissors.png')

player_pos = (200, 240)
computer_pos = (440, 240)

rock_rect = Rect((20, 20), (100, 40))
paper_rect = Rect((20, 70), (100, 40))
scissors_rect = Rect((20, 120), (100, 40))

while True:
    screen.fill((255, 255, 255))
    play()
