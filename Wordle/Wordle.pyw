import pygame
from pygame.locals import *
from math import sin
from random import choice

class Colors:
    background = (34, 34, 34)
    dark = (50, 50, 50)
    grey = (132, 132, 132)
    yellow = (230, 214, 19)
    green = (20, 150, 50)

class Guess:
    def __init__(self):
        self.index = len(guesses_list)
        self.guess = ''

    def update(self, events):
        global message
        if self == guesses_list[-1]:
            # this object is the one getting the user inputs
            for event in events:
                if event.type == KEYDOWN:
                    if event.key == K_BACKSPACE:
                        self.guess = self.guess[:-1]
                    elif event.unicode.isalpha() and len(self.guess) < 5:
                        self.guess += event.unicode.lower()

                    elif event.key == K_RETURN:
                        if len(self.guess) == 5:
                            if self.guess in allowed_words:
                                # do not press Enter on the next guess
                                events.remove(event)
                                guesses_list.append(Guess())
                            else:
                                message = 'The word has not been recognised.'
                        else:
                            message = 'The word is too short.'
        self.draw()

    def fancy_color(self, color):
        r, g, b = color
        add = int(sin(ticks()/500)*20 + 20)
        r += add
        g += add
        b += add
        return r, g, b

    def draw(self):
        last = self.index == len(guesses_list) - 1
        answer_ = list(answer) # used to handle yellow letters

        y = 10 + 100*self.index
        for x in range(len(self.guess)):
            rect = Rect((10 + 100*x, y), (80, 80))

            if last: # self is the last guess
                color = Colors.grey
            else:
                if self.guess[x] == answer[x]:
                    color = Colors.green
                    answer_.remove(self.guess[x])
                elif self.guess[x] in answer_:
                    color = Colors.yellow
                    answer_.remove(self.guess[x])
                else:
                    color = Colors.grey
            pygame.draw.rect(screen, color, rect)
            text = font.render(self.guess[x].upper(), True, Colors.dark)
            w, h = text.get_size()
            screen.blit(text, (rect.x + 40 - w//2, y + 40 - h//2))

        if last and len(self.guess) < 5: # blinking cursor
            rect = Rect((10 + 100*len(self.guess), y), (80, 80))
            pygame.draw.rect(screen, self.fancy_color(Colors.dark), rect)

def draw_empty_board():
    screen.fill(Colors.background)

    for x in range(5):
        for y in range(6):
            pygame.draw.rect(screen, Colors.dark, Rect((10 + 100*x, 10 + 100*y), (80, 80)))

def show_message():
    screen.blit(black, (0, 0))
    text = message_font.render(message, True, Colors.grey)
    w, h = text.get_size()
    pygame.draw.rect(screen, Colors.dark, Rect((WIDTH//2 - w//2 - 20, HEIGHT//2 - 50), (w + 40, 100)))
    screen.blit(text, (WIDTH//2 - w//2, HEIGHT//2 - h//2))

pygame.init()
pygame.display.set_caption('Wordle Copy')
WIDTH, HEIGHT = (500, 600)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.SysFont('calibri', 50, True)
message_font = pygame.font.SysFont('calibri', 30, True)
clock = pygame.time.Clock()
ticks = pygame.time.get_ticks

# overlay
black = pygame.Surface((WIDTH, HEIGHT), SRCALPHA)
black.fill((0, 0, 0, 100))

with open('allowed guesses.txt', encoding='utf-8') as f:
    allowed_words = f.read().split('\n')
answer = choice(allowed_words)
guesses_list = []
guesses_list.append(Guess())
message = '' # optional popup

game_over = False
while True:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            exit()
        elif event.type == KEYDOWN and event.key == K_RETURN:
            # close any opened popup
            if message:
                if game_over:
                    pygame.quit()
                    exit()
                    # close the game after the game is over
                else:
                    message = ''
                    events.remove(event) # do not trigger the popup again

    draw_empty_board()
    if message:
        for guess in guesses_list:
            guess.draw() # do not update them until you close the message box
        show_message()
    else:
        for guess in guesses_list:
            guess.update(events)
    if len(guesses_list) > 1 and guesses_list[-2].guess == answer: # -2 because need to press Enter
        message = 'Found it! Congrats!'
        game_over = True
    if len(guesses_list) == 7:
        message = 'Game over - the word was %s' %answer
        game_over = True

    pygame.display.flip()
    clock.tick(60) # limit the framerate to avoid using the computer resources
