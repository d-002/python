import time
import pygame
from pygame.locals import *
from random import randint

class Piece:
    def __init__(self, index, glob):
        self.pos = [3, 0]
        self.pattern = []
        for line in glob[0].pieces[index]:
            self.pattern.append([])
            for cell in line:
                if cell == '1':
                    self.pattern[-1].append(index+1)
                else:
                    self.pattern[-1].append(0)

        self.ticks_since_drop = 0

    def left(self, glob):
        self.pos[0] -= 1
        if self.collide(glob):
            self.pos[0] += 1
            return False # did not succeed
        return True

    def right(self, glob):
        self.pos[0] += 1
        if self.collide(glob):
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

    def collide(self, glob):
        for x in range(4):
            for y in range(4):
                if self.pattern[y][x]:
                    abs_x, abs_y = x+self.pos[0], y+self.pos[1]
                    if not 0 <= abs_x <= 9 or not 0 <= abs_y <= 19 or glob[0].board[abs_y][abs_x]:
                        return True
        return False

    def move(self, glob, fast=False):
        self.ticks_since_drop += 1
        if self.ticks_since_drop >= glob[4] or fast:
            self.ticks_since_drop = 0
            self.pos[1] += 1

            if self.collide(glob):
                self.pos[1] -= 1
                glob[0].append_piece()
                if fast:
                    self.pos[1] += 1
                else:
                    glob[0].new_piece(glob)

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

        self.piece = None
        self.next = None
        self.hold = None
        self.has_switch = False
        self.gameover = False

    def switch(self, glob):
        if not self.has_switch: # can only switch once per piece
            if self.hold:
                self.piece, self.hold = self.hold, self.piece
            else:
                self.hold = self.piece
                self.new_piece(glob)

            self.has_switch = True
            self.hold.pos = [3, 0]

    def append_piece(self):
        for x in range(4):
            for y in range(4):
                abs_x, abs_y = x+self.piece.pos[0], y+self.piece.pos[1]
                if self.piece.pattern[y][x]:
                    self.board[abs_y][abs_x] = self.piece.pattern[y][x]

    def new_piece(self, glob):
        self.piece = self.next
        if self.piece is not None and self.piece.collide(glob):
            self.gameover = True

        n = randint(0, 7)
        if n == 7:
            self.next = Piece(randint(0, 6), glob)
        else:
            self.next = Piece(n, glob)

        self.has_switch = False

    def update(self, glob):
        completed_lines = []
        for y in range(20):
            if not 0 in self.board[y]: # completed line
                completed_lines.append(y)

        last_level = level(glob)
        glob[2] += [0, 40, 100, 250, 1000][len(completed_lines)]
        glob[3] += len(completed_lines)
        for y in completed_lines:
            for y_ in range(y-1, -1, -1):
                self.board[y_+1] = self.board[y_]
            self.board[0] = [0]*10

class Ai:
    def __init__(self):
        self.goto = 0 # x value where the piece needs to go
        self.rotation = 0 # how many times the piece needs to rotate
        self.prev_piece = None
        self.rotation_count = 0
        self.cooldown = 0
        self.forbidden = []

        # functions used as bonuses and penalties depending on their respective multiplier
        self.parameters = [self.low_piece, self.tetris_hole, self.lines,
                           self.every_piece_possible, self.holes, self.height_diff, self.long_holes]
        self.good = [True, True, True, True, False, False, False]
        self.multipliers = [0.8, 1, 10, 0.5, -2, -1, -2]

    def low_piece(self, glob):
        if self.holes():
            return glob[0].piece.pos[1]*2
        return glob[0].piece.pos[1]

    def lines(self, glob):
        if self.holes():
            return glob[3]*5
        return glob[3]

    def holes(self, glob):
        has_piece = [False]*10
        holes = 0
        for y in range(20):
            for x in range(10):
                if glob[0].board[y][x]:
                    has_piece[x] = True
                elif has_piece[x]:
                    holes += 1
        return holes

    def long_holes(self, glob):
        top = []
        for x in range(8): # do not count the last one
            top.append(0)
            while top[-1] < 20 and not glob[0].board[top[-1]][x]:
                top[-1] += 1
        holes = 0
        for x in range(7):
            if abs(top[x]-top[x+1]) >= 3:
                holes += 1
        return holes

    def tetris_hole(self, glob):
        height1 = height2 = 0
        for x in range(20):
            if not glob[0].board[x][8]:
                height1 = x
            if not glob[0].board[x][9]:
                height2 = x
        if self.holes(): # if hole, change the algorithm to mine to them
            return min(height1-height2, 0)
        return min(height2-height1-3, 1)

    def height_diff(self, glob):
        top = []
        for x in range(9):
            top.append(0)
            while top[-1] < 20 and not glob[0].board[top[-1]][x]:
                top[-1] += 1
        mean = sum(top)/10
        variance = sum([(x-mean)**2 for x in top])/10
        return variance**0.5

    def every_piece_possible(self, glob):
        top = []
        for x in range(9):
            top.append(0)
            while top[-1] < 20 and not glob[0].board[top[-1]][x]:
                top[-1] += 1
        differences = [top[x+1]-top[x] for x in range(8)]
        bonus = 0
        if 0 in differences:
            bonus += 1
        if 1 in differences:
            bonus += 2
        if -1 in differences:
            bonus += 2
        if sum([differences[x] == differences[x+1] == 2 for x in range(7)]):
            bonus += 0.5
        if sum([differences[x] == differences[x+1] == -2 for x in range(7)]):
            bonus += 0.5
        return bonus

    def rotate_piece(self, rotation, glob):
        if self.rotation_count%4 != rotation:
            if (rotation-self.rotation_count) % 4 == 1: # turn right
                glob[0].piece.rotate()
                self.rotation_count += 1
                if glob[0].piece.collide(glob):
                    for _ in range(3):
                        glob[0].piece.rotate()
                    self.rotation_count -= 1
            else: # turn left
                for _ in range(3):
                    glob[0].piece.rotate()
                self.rotation_count -= 1
                if glob[0].piece.collide(glob):
                    glob[0].piece.rotate()
                    self.rotation_count += 1

    def calculate(self, glob):
        # make saves of global variables
        board_ = glob[0].board
        piece = glob[0].piece
        scores = []
        for x in range(14):
            scores.append([0]*4)
        heights = [0]*14
        score_ = glob[2]
        lines_ = glob[3]

        for x in range(-2, 12):
            for rotation in range(4):
                # reset variables
                glob[0].board = copy(board_)
                glob[0].piece = Piece(0, glob)
                glob[0].piece.pos = [x, piece.pos[1]]
                glob[0].piece.pattern = piece.pattern
                glob[3] = 0
                self.rotation_count = 0
                while not glob[0].piece.collide(glob):
                    self.rotate_piece(rotation, glob)

                    glob[0].update(glob)
                    glob[0].piece.move(glob, True)
                glob[0].update(glob) # check if any completed line
                glob[0].piece.pos[1] -= 1
                if glob[0].piece.pos[1] <= 0 or (x, rotation) in self.forbidden: # the piece spawns out of bounds
                    scores[x+2][rotation] = -1000000
                else:
                    scores[x+2][rotation] = sum([self.parameters[x](glob)*self.multipliers[x] for x in range(len(self.parameters))])
                heights[x+2] = glob[0].piece.pos[1]

        bests = [max(x) for x in scores]
        self.goto = bests.index(max(bests))-2
        self.rotation = scores[self.goto+2].index(max(scores[self.goto+2]))

        glob[0].board = board_
        glob[0].piece = piece
        glob[0].gameover = False # in case you die on this turn
        glob[2] = score_
        glob[3] = lines_
        self.rotation_count = 0
        self.prev_piece = glob[0].piece

    def process(self, glob):
        if self.prev_piece != glob[0].piece:
            self.forbidden = [] # reset the forbidden positions and rotations
            self.calculate(glob)

        if not self.cooldown:
            self.cooldown = 5
            if glob[0].piece.pos[0] > self.goto:
                if not glob[0].piece.left(glob): # did not succeed: needs to go around sth?
                    self.forbidden.append((self.goto, self.rotation))
                    self.calculate(glob) # retry, but forbid this position and rotation
            elif glob[0].piece.pos[0] < self.goto:
                if not glob[0].piece.right(glob):
                    self.forbidden.append((self.goto, self.rotation))
                    self.calculate(glob)
            else:
                glob[4] = 3

            self.rotate_piece(self.rotation, glob)
        self.cooldown -= 1

def falling_delay_alg(glob): # in frames per cell
    if level(glob) < 9:
        return 48 - 5*level(glob)
    if level(glob) == 9:
        return 6
    if 10 <= level(glob) <= 12:
        return 5
    if 13 <= level(glob) <= 15:
        return 4
    if 16 <= level(glob) <= 18:
        return 3
    if 19 <= level(glob) <= 28:
        return 2
    return 1

def copy(b): # copy a 2D list
    board = []
    for y in range(20):
        board.append(b[y][:])
    return board

def reset():
    global globals_
    globals_ = []

pygame.init()
ticks = pygame.time.get_ticks
reset()
level = lambda glob: glob[3]//10

def from_learn_file(parameters): # go fast, launched by another file
    global globals_
    index = len(globals_)
    globals_.append([]) # each thread has its own globals
    # board, ai, score, lines, falling_delay
    globals_[index] = glob = [Board(), Ai(), 0, 0, 0]
    glob[0].new_piece(glob)
    glob[0].new_piece(glob)
    glob[1].multipliers = parameters

    start = time.time()
    while not glob[0].gameover:
        glob[4] = falling_delay_alg(glob)
        glob[1].process(glob)
        glob[0].update(glob)
        glob[0].piece.move(glob)

    return glob[3]+(time.time()-start)/30
