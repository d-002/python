import time
import pygame
from pygame.locals import *
from random import randint, seed
from threading import Thread

class Colors:
    background = (11, 5, 61)
    text = (215, 215, 215)
    back = (26, 31, 47)
    border = (200, 200, 200)
    grey = (139, 139, 139)
    pieces = [(47, 249, 113),
              (138, 27, 175),
              (51, 210, 244),
              (242, 153, 152),
              (74, 170, 221),
              (254, 142, 41),
              (213, 83, 116),
              (139, 139, 139),
              grey] # the last one is used when a line is completed

    def draw(self, surf, color, pos):
        x, y = pos
        r, g, b = color
        lighten = (min(r+50, 255), min(g+50, 255), min(b+50, 255))
        darken = (max(r-50, 0), max(g-50, 0), max(b-50, 0))
        pygame.draw.rect(surf, color, Rect(pos, (20, 20)))
        pygame.draw.polygon(surf, darken, [(x+19, y+19), (x+19, y), (x+17, y+1), (x+17, y+17), (x+1, y+17), (x, y+19)])
        pygame.draw.polygon(surf, lighten, [(x, y), (x+19, y), (x+17, y+1), (x+1, y+1), (x+1, y+17), (x, y+19)])

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
                board.new_piece()
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
        self.pieces = [['0010', '0010', '0010', '0010'],
                       ['0000', '0010', '0111', '0000'],
                       ['0000', '0010', '1110', '0000'],
                       ['0000', '0100', '0111', '0000'],
                       ['0000', '0011', '0110', '0000'],
                       ['0000', '1100', '0110', '0000'],
                       ['0000', '0110', '0110', '0000']]

        self.background = pygame.Surface((240, 440))
        self.background.fill(colors.back)
        for x in range(12):
            colors.draw(self.background, colors.grey, (20*x, 0))
            colors.draw(self.background, colors.grey, (20*x, 420))
        for y in range(22):
            colors.draw(self.background, colors.grey, (0, 20*y))
            colors.draw(self.background, colors.grey, (220, 20*y))

        self.points_per_line = [0, 40, 100, 250, 1000]
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

    def append_piece(self):
        for x in range(4):
            for y in range(4):
                abs_x, abs_y = x+self.piece.pos[0], y+self.piece.pos[1]
                if 0 <= abs_x <= 9 and abs_y <= 19:
                    if self.piece.pattern[y][x]:
                        self.board[abs_y][abs_x] = self.piece.pattern[y][x]

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

    def update(self):
        global lines, score

        completed_lines = []
        for y in range(20):
            if not 0 in self.board[y]: # completed line
                completed_lines.append(y)

        last_level = level()
        score += self.points_per_line[len(completed_lines)]
        lines += len(completed_lines)
        if len(completed_lines):
            for y in completed_lines:
                self.board[y] = [8]*10

            start = ticks()
            while ticks()-start < 500: # animation
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
                    screen.fill(colors.background)
                    self.draw()

                gui.draw()

                pygame.display.flip()
                clock.tick(60)

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

class Ai:
    def __init__(self):
        self.goto = 0 # x value where the piece needs to go
        self.rotation = 0 # how many times the piece needs to rotate
        self.switch = False # if needs to switch to hold
        self.prev_piece = None
        self.rotation_count = 0
        self.cooldown = 0
        self.forbidden = []
        self.globals = [] # board.board, board.piece, score, lines, rotation_count, holes_before, piece_height_diff, next, hold
        self.queue = [] # for threads to launch one after another
        self.thread_index = 0

        # functions used as bonuses and penalties depending on their respective multiplier
        self.parameters = [self.low_piece, self.tetris_hole, self.lines,
                           self.next_piece_possible, self.holes, self.height_diff, self.long_holes]
        self.good = [True, True, True, True, False, False, False]
        self.multipliers = [0.8, 1, 10, 0.5, -2, -1, -2]

    def low_piece(self):
        if self.globals[5]:
            return self.globals[1].pos[1]*3 - 50
        return self.globals[1].pos[1] - 10

    def lines(self):
        if self.globals[5]:
            return self.globals[3]*5
        return self.globals[3]//4*4

    def holes(self):
        has_piece = [0]*10
        holes = 0
        for y in range(20):
            for x in range(10):
                if self.globals[0][y][x]:
                    has_piece[x] += 1
                elif has_piece[x]:
                    holes += has_piece[x]**0.3
        return holes

    def long_holes(self):
        top = []
        for x in range(8): # do not count the last one
            top.append(0)
            while top[-1] < 20 and not self.globals[0][top[-1]][x]:
                top[-1] += 1
        holes = 0
        for x in range(7):
            if abs(top[x]-top[x+1]) >= 3:
                holes += 1
        return holes

    def tetris_hole(self):
        height1 = height2 = 0
        while height1 < 20 and not self.globals[0][height1][8]:
            height1 += 1
        while height2 < 20 and not self.globals[0][height2][9]:
            height2 += 1

        if self.globals[5]: # if hole, change the algorithm to mine to them
            return min(height1-height2, 0)
        return min(height2-height1-3, 1)

    def height_diff(self):
        top = []
        for x in range(9):
            top.append(0)
            while top[-1] < 20 and not self.globals[0][top[-1]][x]:
                top[-1] += 1
        mean = sum(top)/10
        variance = sum([(x-mean)**2 for x in top])/10
        return variance**0.5

    def next_piece_possible(self):
        if not self.globals[5]:
            return 0
        top = []
        for x in range(9):
            top.append(0)
            while top[-1] < 20 and not self.globals[0][top[-1]][x]:
                top[-1] += 1
        differences = [top[x+1]-top[x] for x in range(8)]
        bonus = 0
        for rotation in self.globals[6]:
            for x in range(5):
                if differences[x:x+3] == rotation:
                    bonus += 1
        return bonus


    def rotate_piece(self, rotation, piece_=None, count=None):
        def add_to_count(add):
            self.rotation_count += add
        def add_to_globals(add):
            self.globals[4] += add

        # returns False if did not succeed

        if piece_ is None:
            piece_ = board.piece
            collide = piece_.collide
        else: # use ai collide function
            collide = self.piece_collide
        if count is None:
            get_count = self.rotation_count
            count = add_to_count # adds to self.rotation_count
        else:
            get_count = self.globals[4]
            count = add_to_globals # adds to self.globals[4]

        if get_count%4 != rotation:
            if (rotation-get_count) % 4 == 1: # turn right
                piece_.rotate()
                count(1)
                if collide():
                    for _ in range(3):
                        piece_.rotate()
                    count(-1)
                    return False
            else: # turn left
                for _ in range(3):
                    piece_.rotate()
                count(-1)
                if collide():
                    piece_.rotate()
                    count(1)
                    return False
        return True

    def update_board_fast(self):
        completed_lines = []
        for y in range(20):
            if not 0 in self.globals[0][y]: # completed line
                completed_lines.append(y)

        if len(completed_lines):
            self.globals[2] += board.points_per_line[len(completed_lines)]
            self.globals[3] += len(completed_lines)
            for y in completed_lines:
                for y_ in range(y-1, -1, -1):
                    self.globals[0][y_+1] = self.globals[0][y_]
                self.globals[0][0] = [0]*10

    def piece_collide(self):
        piece_ = self.globals[1]
        px, py = piece_.pos
        for x in range(px, px+4):
            for y in range(py, py+4):
                if piece_.pattern[y-py][x-px]:
                    if not 0 <= x <= 9 or not 0 <= y <= 19 or self.globals[0][y][x]:
                        return True
        return False

    def move_piece_fast(self):
        pos = self.globals[1].pos
        pos[1] += 1

        if self.piece_collide():
            pos[1] -= 1
            self.append_piece_to_board()
            pos[1] += 1

    def append_piece_to_board(self):
        piece_ = self.globals[1]
        px, py = piece_.pos
        for x in range(px, px+4):
            for y in range(py, py+4):
                if 0 <= x <= 9 and y <= 19:
                    value = piece_.pattern[y-py][x-px]
                    if value:
                        self.globals[0][y][x] = value

    def switch_pieces(self):
        if self.globals[8]:
            self.globals[1], self.globals[7] = self.globals[8], self.globals[1]
        else:
            self.globals[8] = self.globals[1]
            self.new_piece()

        self.has_switch = True

    def from_pattern(self, pattern, pos=[3, 0]):
        piece = Piece(0)
        piece.pattern = pattern
        piece.pos = pos
        return piece

    def calculate(self, *args):
        b_copy, pos, pat, next_pat, hold_pat = args
        index = self.thread_index
        self.thread_index += 1
        self.queue.append(index)
        while self.queue[0] != index:
            time.sleep(0.01)

        # make saves of global variables
        scores = [[], []]
        for x in range(10):
            scores[0].append([0]*4)
            scores[1].append([0]*4)

        # create local pieces
        next_piece = self.from_pattern(next_pat)
        hold_piece = self.from_pattern(hold_pat)

        # get the height difference for every piece rotation
        piece_height_diff = []
        temp_piece = self.from_pattern(next_piece.pattern)
        for rotation in range(4):
            temp_pat = [line[:] for line in temp_piece.pattern]
            while temp_pat[0] == [0, 0, 0, 0]:
                temp_pat.pop(0)

            piece_height_diff.append([])
            for x in range(3):
                max_y0 = max_y1 = 0
                for y in range(len(temp_pat)):
                    if temp_pat[y][x]:
                        max_y0 = y+1
                    if temp_pat[y][x+1]:
                        max_y1 = y+1
                piece_height_diff[-1].append(max_y1-max_y0)
            temp_piece.rotate()
        del temp_piece, temp_pat

        for index, current_pat in [(0, pat), (1, hold_pat)]:
            for x in range(-2, 8):
                for rotation in range(4):
                    # reset variables
                    board_ = copy(b_copy)
                    piece_ = self.from_pattern(current_pat)
                    piece_.pos = [x, pos]
                    self.globals = [board_, piece_, 0, 0, 0, None, piece_height_diff, self.from_pattern(next_piece.pattern, [x, pos]), self.from_pattern(hold_piece.pattern, [x, pos])]
                    if index:
                        self.switch_pieces()
                    self.globals[5] = self.holes()
                    while not self.piece_collide() or self.globals[4]%4 != rotation:
                        if not self.rotate_piece(rotation, piece_, self.globals): # do not cancel certain paths only available after rotating
                            if piece_.pos[0] < 0:
                                piece_.pos[0] += 2
                            elif piece_.pos[0] > 5:
                                piece_.pos[0] -= 2
                            else:
                                self.globals[4] = rotation # end the loop

                        self.update_board_fast()
                        self.move_piece_fast()
                    self.update_board_fast() # check if any completed line
                    piece_.pos[1] -= 1
                    if piece_.pos[1] <= 0 or piece_.pos[0] != x or (x, rotation) in self.forbidden: # the piece spawns out of bounds
                        scores[index][x+2][rotation] = -1000000
                    else:
                        scores[index][x+2][rotation] = sum([self.parameters[p]()*self.multipliers[p] for p in range(len(self.parameters))])

        bests = [[max(x) for x in scores[0]], [max(x) for x in scores[1]]]
        best_piece = int(bests[1] > bests[0])
        goto = bests[best_piece].index(max(bests[best_piece]))-2
        rotation = scores[best_piece][goto+2].index(max(scores[best_piece][goto+2]))

        self.goto, self.rotation, self.switch = goto, rotation, best_piece
        self.queue.pop(0)

    def process(self):
        global falling_delay

        if self.prev_piece != board.piece:
            if board.hold:
                hold = board.hold
            else:
                hold = board.next
            args = (copy(board.board), board.piece.pos[1], [y[:] for y in board.piece.pattern], [y[:] for y in board.next.pattern], [y[:] for y in hold.pattern])
            Thread(target=lambda: self.calculate(*args)).start()
            self.prev_piece = board.piece

        if self.switch:
            board.switch()
            self.switch = False

        if not self.cooldown:
            self.cooldown = 3
            if board.piece.pos[0] > self.goto:
                if not board.piece.left(): # did not succeed: needs to go around sth?
                    self.forbidden.append((self.goto, self.rotation))
                    # retry, but forbid this position and rotation
                    self.prev_piece = None
            elif board.piece.pos[0] < self.goto:
                if not board.piece.right():
                    self.forbidden.append((self.goto, self.rotation))
                    self.prev_piece = None
            else:
                falling_delay = 3

            self.rotate_piece(self.rotation)
        self.cooldown -= 1

def falling_delay_alg(): # in frames per cell
    if level() < 9:
        return 48 - 5*level()
    if level() == 9:
        return 6
    if 10 <= level() <= 12:
        return 5
    if 13 <= level() <= 15:
        return 4
    if 16 <= level() <= 18:
        return 3
    if 19 <= level() <= 28:
        return 2
    return 1

def copy(b): # copy a 2D list
    board = []
    for y in range(20):
        board.append(b[y][:])
    return board

seed(0)

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

AI = True
if AI:
    ai = Ai()

icon = pygame.Surface((20, 20))
colors.draw(icon, colors.grey, (0, 0))
pygame.display.set_icon(icon)
del icon

score = 0
lines = 0
start_level = 0
level = lambda: start_level + lines//10
enable_down = False

while not board.gameover:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            exit()

    falling_delay = falling_delay_alg()
    if AI:
        ai.process()
    else:
        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_q:
                    board.piece.left()
                elif event.key == K_d:
                    board.piece.right()
                elif event.key == K_RIGHT:
                    board.piece.rotate()
                    if board.piece.collide():
                        for x in range(3):
                            board.piece.rotate()
                elif event.key == K_LEFT:
                    for x in range(3):
                        board.piece.rotate()
                    if board.piece.collide():
                        board.piece.rotate()
                elif event.key == K_SPACE:
                    board.switch()

        pressed = pygame.key.get_pressed()
        if pressed[K_s]:
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
    clock.tick(120)

# game over animation
time.sleep(0.5)
for y in range(20):
    board.board[y] = [8]*10
    board.draw()
    pygame.display.flip()
    time.sleep(0.05)

time.sleep(0.5)
text = font.render('Game Over', True, colors.text)
pygame.draw.rect(screen, colors.background, Rect((30, 230), (240, 40)))
screen.blit(text, (150 - text.get_width()//2, 235))
pygame.display.flip()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
