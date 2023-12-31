import time
import pygame
from pygame.locals import *
from random import randint, seed
from threading import Thread

from ai import *

class Colors:
    background = (11, 5, 61)
    text = (215, 215, 215)
    back = (26, 31, 47)
    border = (200, 200, 200)
    grey = (139, 139, 139)
    pieces = [(15, 155, 215),
              (33, 65, 198),
              (227, 91, 2),
              (227, 159, 2),
              (89, 177, 1),
              (175, 41, 138),
              (215, 15, 55),
              grey] # the last one is used when a line is completed

    def draw(self, surf, color, pos):
        x, y = pos
        r, g, b = color
        lighten = (min(r+50, 255), min(g+50, 255), min(b+50, 255))
        darken = (max(r-50, 0), max(g-50, 0), max(b-50, 0))
        pygame.draw.rect(surf, color, Rect(pos, (20, 20)))
        pygame.draw.polygon(surf, darken, [(x+19, y+19), (x+19, y), (x+16, y+3), (x+16, y+16), (x+3, y+16), (x, y+19)])
        pygame.draw.polygon(surf, lighten, [(x, y), (x+19, y), (x+16, y+3), (x+3, y+3), (x+3, y+16), (x, y+19)])

class Sounds:
    def __init__(self):
        self.drop = pygame.mixer.Sound('files/drop.mp3')
        self.line = pygame.mixer.Sound('files/line clear.mp3')
        self.tetris = pygame.mixer.Sound('files/tetris.mp3')
        self.next_level = pygame.mixer.Sound('files/next level.mp3')
        self.game_over = pygame.mixer.Sound('files/game over.mp3')

        self.files = {'A': 'files/A music.mp3',
                      'B': 'files/B music.mp3',
                      'C': 'files/C music.mp3',
                      'title': 'files/title.mp3',
                      'game over': 'files/game over music.mp3'}
        pygame.mixer.music.set_volume(0.5)

    def play_music(self, name):
        pygame.mixer.music.unload()
        pygame.mixer.music.load(self.files[name])
        pygame.mixer.music.play(-1)

class Piece:
    def __init__(self, index):
        self.pos = [3, 0]
        self.pattern = []
        for line in board.pieces[index]:
            self.pattern.append([])
            for cell in line:
                if cell == '1':
                    self.pattern[-1].append(index+1)
                else:
                    self.pattern[-1].append(0)

        self.ticks_since_drop = 0

    def left(self):
        self.pos[0] -= 1
        if self.collide():
            self.pos[0] += 1
            return False # did not succeed
        return True

    def right(self):
        self.pos[0] += 1
        if self.collide():
            self.pos[0] -= 1
            return False
        return True

    def hard_drop(self):
        while not self.collide():
            self.pos[1] += 1
        self.pos[1] -= 1
        board.append_piece(True)

    def rotate(self): # right
        pattern = []
        for y in range(4):
            pattern.append([0]*4)

        for y in range(4):
            for x in range(4):
                pattern[x][y] = self.pattern[3-y][x]
        self.pattern = pattern

    def collide(self):
        for x in range(4):
            for y in range(4):
                if self.pattern[y][x]:
                    abs_x, abs_y = x+self.pos[0], y+self.pos[1]
                    if not 0 <= abs_x <= 9 or not 0 <= abs_y <= 19 or board.board[abs_y][abs_x]:
                        return True
        return False

    def move(self):
        self.ticks_since_drop += 1

        if self.ticks_since_drop >= falling_delay:
            self.ticks_since_drop = 0
            self.pos[1] += 1

            if self.collide():
                self.pos[1] -= 1
                board.append_piece()
                if AI:
                    ai.rotation_count = 0
                    ai.forbidden = [] # reset the forbidden positions and rotations

    def draw(self):
        for y in range(4):
            for x in range(4):
                if self.pattern[y][x]:
                    pos = (50 + 20 * (self.pos[0]+x), 50 + 20 * (self.pos[1]+y))
                    colors.draw(screen, colors.pieces[self.pattern[y][x]-1], pos)

class Board:
    def __init__(self):
        self.board = []
        for y in range(20):
            self.board.append([0]*10)
        self.pieces = [['0000', '0000', '1111', '0000'],
                       ['0000', '1000', '1110', '0000'],
                       ['0000', '0010', '1110', '0000'],
                       ['0000', '0110', '0110', '0000'],
                       ['0000', '0110', '1100', '0000'],
                       ['0000', '0100', '1110', '0000'],
                       ['0000', '1100', '0110', '0000']]

        self.background = pygame.Surface((240, 440))
        self.background.fill(colors.back)
        for x in range(12):
            colors.draw(self.background, colors.grey, (20*x, 0))
            colors.draw(self.background, colors.grey, (20*x, 420))
        for y in range(22):
            colors.draw(self.background, colors.grey, (0, 20*y))
            colors.draw(self.background, colors.grey, (220, 20*y))

        self.points_per_line = [0, 100, 300, 500, 800]
        self.piece = None
        self.next = None
        self.hold = None
        self.has_switch = False
        self.gameover = False

    def switch(self):
        if not self.has_switch: # can only switch once per piece
            if self.hold:
                self.piece, self.hold = self.hold, self.piece
            else:
                self.hold = self.piece
                self.new_piece()

            self.has_switch = True
            self.hold.pos = [3, 0]

    def append_piece(self, hard_drop=False):
        global score

        for x in range(4):
            for y in range(4):
                abs_x, abs_y = x+self.piece.pos[0], y+self.piece.pos[1]
                if 0 <= abs_x <= 9 and abs_y <= 19:
                    if self.piece.pattern[y][x]:
                        self.board[abs_y][abs_x] = self.piece.pattern[y][x]
        sounds.drop.play()
        if hard_drop:
            score += 2
        else:
            score += 1
        self.new_piece()

    def new_piece(self):
        global enable_down

        self.piece = self.next
        if self.piece is not None and self.piece.collide():
            self.gameover = True

        n = randint(0, 7)
        if n == 7:
            self.next = Piece(randint(0, 6))
        else:
            self.next = Piece(n)

        enable_down = False
        self.has_switch = False

    def generate_noise(self, level):
        for y in range(19, max(19 - 2*level, -1), -1):
            for x in range(10):
                if not randint(0, 2):
                    self.board[y][x] = randint(1, 7)

    def update(self):
        global lines, score

        completed_lines = []
        for y in range(20):
            if not 0 in self.board[y]: # completed line
                completed_lines.append(y)

        last_level = level()
        score += self.points_per_line[len(completed_lines)]*level()
        lines += len(completed_lines)
        if len(completed_lines):
            if len(completed_lines) == 4:
                sounds.tetris.play()
            else:
                sounds.line.play()

            for y in completed_lines:
                self.board[y] = [8]*10

            start = ticks()
            while ticks()-start < 500: # animation
                screen.fill(colors.background)
                if (ticks()-start) // 100 % 2:
                    if last_level != level():
                        screen.fill(colors.grey)

                    self.draw()
                    for x in range(12):
                        colors.draw(screen, colors.back, (30 + 20*x, 30))
                        colors.draw(screen, colors.back, (30 + 20*x, 450))
                    for y in range(22):
                        colors.draw(screen, colors.back, (30, 30 + 20*y))
                        colors.draw(screen, colors.back, (250, 30 + 20*y))
                else:
                    self.draw()

                gui.draw()

                pygame.display.flip()
                clock.tick(60)

            if last_level != level():
                sounds.next_level.play()

            for y in completed_lines:
                for y_ in range(y-1, -1, -1):
                    self.board[y_+1] = self.board[y_]
                self.board[0] = [0]*10

    def draw(self):
        screen.blit(self.background, (30, 30)) # the actual main area begins at (50, 50)
        self.piece.draw()

        for y in range(20):
            for x in range(10):
                if self.board[y][x]:
                    pos = (50 + 20*x, 50 + 20*y)
                    colors.draw(screen, colors.pieces[self.board[y][x]-1], pos)

class Gui:
    def __init__(self):
        self.box = pygame.Surface((120, 120))
        self.box.fill(colors.back)
        for x in range(6):
            colors.draw(self.box, colors.grey, (20*x, 0))
            colors.draw(self.box, colors.grey, (20*x, 100))
        for y in range(6):
            colors.draw(self.box, colors.grey, (0, 20*y))
            colors.draw(self.box, colors.grey, (100, 20*y))

        n_cells = 2 + int(9*number_font_w/20 + 0.95)
        self.boxes = pygame.Surface((20 * n_cells, 100))

        for x in range(n_cells):
            for y in [0, 2, 4]:
                colors.draw(self.boxes, colors.grey, (20*x, 20*y))
        for y in range(5):
            colors.draw(self.boxes, colors.grey, (0, 20*y))
            colors.draw(self.boxes, colors.grey, (20 * (n_cells-1), 20*y))

    def draw(self):
        screen.blit(self.box, (310, 100))
        screen.blit(self.box, (460, 100))
        for x in range(4):
            for y in range(4):
                pos = [330 + 20*x, 120 + 20*y]
                if board.next.pattern[y][x]:
                    colors.draw(screen, colors.pieces[board.next.pattern[y][x]-1], pos)
                if board.hold is not None and board.hold.pattern[y][x]:
                    pos[0] += 150
                    colors.draw(screen, colors.pieces[board.hold.pattern[y][x]-1], pos)

        text = title.render('TETRIS', True, colors.text)
        w, h = text.get_size()
        screen.blit(text, (435 - w//2, 50 - h//2))

        text = font.render('Next', True, colors.text)
        screen.blit(text, (370 - text.get_width()//2, 230))
        text = font.render('Hold', True, colors.text)
        screen.blit(text, (520 - text.get_width()//2, 230))

        screen.blit(self.boxes, (440, 300))
        text = number_font.render('0' * (9-len(str(score))) + str(score), True, colors.text)
        screen.blit(text, (460, 320))
        text = number_font.render('0' * (9-len(str(lines))) + str(lines), True, colors.text)
        screen.blit(text, (460, 360))

        text = font.render('Score:', True, colors.text)
        w, h = text.get_size()
        screen.blit(text, (420-w, 330 - h//2))
        text = font.render('Lines:', True, colors.text)
        w, h = text.get_size()
        screen.blit(text, (420-w, 370 - h//2))

def falling_delay_alg(): # in frames per cell
    return 120//level()
    if level()-1 < 9:
        return 48 - 5*level()
    if level()-1 == 9:
        return 6
    if 10 <= level()-1 <= 12:
        return 5
    if 13 <= level()-1 <= 15:
        return 4
    if 16 <= level()-1 <= 18:
        return 3
    if 19 <= level()-1 <= 28:
        return 2
    return 1

def copy(b): # copy a board-like list
    board = []
    for y in range(20):
        board.append(b[y][:])
    return board

def move_from_event(key):
    if key == K_q: # move left
        board.piece.left()
    elif key == K_d: # move right
        board.piece.right()
    elif key == K_s: # hard drop
        board.piece.hard_drop()
    elif key == K_RIGHT: # rotate clockwise
        board.piece.rotate()
        if board.piece.collide():
            for x in range(3):
                board.piece.rotate()
    elif key == K_LEFT: # rotate counterclockwise
        for x in range(3):
            board.piece.rotate()
        if board.piece.collide():
            board.piece.rotate()
    elif key == K_DOWN: # rotate 180°
        for x in range(2):
            board.piece.rotate()
        if board.piece.collide():
            for x in range(2):
                board.piece.rotate()
    elif key == K_SPACE: # switch
        board.switch()

#seed(0)

pygame.init()
pygame.mouse.set_visible(0)
screen = pygame.display.set_mode((620, 500))
pygame.display.set_caption('Tetris')
font = pygame.font.SysFont('Consolas', 30)
number_font = pygame.font.SysFont('Consolas', 20) # must be fixed-width
number_font_w = number_font.render('0', 0, (0, 0, 0)).get_width()
title = pygame.font.SysFont('Consolas', 50)
clock = pygame.time.Clock()
ticks = pygame.time.get_ticks

colors = Colors()
board = Board()
board.new_piece() # fill next
board.new_piece()
gui = Gui()
sounds = Sounds()
sounds.play_music('B')

score = 0
lines = 0
start_level = 1
level = lambda: start_level + lines//10
enable_down = False

AI = False
if AI:
    # send global variables to the ai file
    send_globals(board, Piece, copy, level)
    ai = Ai(False)
board.generate_noise(0) # game B type

icon = pygame.Surface((20, 20))
colors.draw(icon, colors.grey, (0, 0))
pygame.display.set_icon(icon)
del icon

while not board.gameover:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            exit()

    falling_delay = falling_delay_alg()
    if AI:
        pressed = ai.play()
        for key in pressed:
            move_from_event(key)

        if K_a in pressed: # soft drop
            if enable_down:
                falling_delay = 1
        else:
            enable_down = True
    else:
        for event in events:
            if event.type == KEYDOWN:
                move_from_event(event.key)

        pressed = pygame.key.get_pressed()
        if pressed[K_a]: # soft drop
            if enable_down:
                falling_delay = 1
        else:
            enable_down = True

    board.update()

    screen.fill(colors.background)

    board.piece.move()
    board.draw()
    gui.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.mixer.music.stop()
sounds.game_over.play().set_volume(0.3)
# game over animation
time.sleep(0.5)
for y in range(20):
    board.board[y] = [8]*10
    board.draw()
    pygame.display.flip()
    time.sleep(0.05)

time.sleep(0.5)
sounds.play_music('game over')
text = font.render('Game Over', True, colors.text)
pygame.draw.rect(screen, colors.background, Rect((30, 230), (240, 40)))
screen.blit(text, (150 - text.get_width()//2, 235))
pygame.display.flip()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
