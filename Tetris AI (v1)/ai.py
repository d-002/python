import time
import pygame
from pygame.locals import *
from threading import Thread

def send_globals(*args):
    global board, Piece, copy, level
    board, Piece, copy, level = args

class Ai:
    def __init__(self, fast):
        self.goto = 0 # x value where the piece needs to go
        self.rotation = 0 # how many times the piece needs to rotate
        self.switch = False # if needs to switch to hold
        self.ready = True
        self.fast = fast
        self.prev_piece = None
        self.rotation_count = 0
        self.forbidden = []
        self.globals = [] # board.board, board.piece, score, lines, rotation_count, holes_before, next, hold
        self.queue = [] # for threads to launch one after another
        self.thread_index = 0

        # functions used as bonuses and penalties depending on their respective multiplier
        self.parameters = [self.low_piece, self.tetris_hole, self.lines,
                           self.holes, self.height_diff, self.long_holes]
        self.multipliers = [2, 1, 10, -2, -1, -2]

    def low_piece(self):
        if self.globals[5]: # if holes, change the algorithm to mine to them
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

    def afraid(self):
        # afraid (aka tries to make lines instead of tetrices)
        return self.holes()

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

        if self.globals[5]:
            return min(height2-height1-3, 1) / 2
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

    def rotate_piece(self, rotation, piece_=None):
        pressed = [] # will be added to the main keys list

        def update_count1():
            self.rotation_count = rotation
        def update_count2():
            self.globals[4] = rotation

        if piece_ is None: # turning the real piece
            piece_ = board.piece
            collide = piece_.collide
            count = self.rotation_count
            update_count = update_count1
        else: # use ai collide function: not moving the real piece
            collide = self.piece_collide
            count = self.globals[4]
            update_count = update_count2

        if count != rotation:
            if (rotation-count) % 4 == 1: # turn right
                piece_.rotate()
                if not collide():
                    pressed.append(K_RIGHT)
                # rotate back if the piece is the real piece
                # the AI will just check if it's possible to turn
                if piece_ == board.piece:
                    for _ in range(3):
                        piece_.rotate()
            elif (rotation-count) % 4 == 3: # turn left
                for _ in range(3):
                    piece_.rotate()
                if not collide():
                    pressed.append(K_LEFT)
                if piece_ == board.piece:
                    piece_.rotate()
            else: # turn 180°
                for _ in range(2):
                    piece_.rotate()
                if not collide():
                    pressed.append(K_DOWN)
                if piece_ == board.piece:
                    for _ in range(2):
                        piece_.rotate()
        update_count()
        return pressed

    def update_board_fast(self):
        completed_lines = []
        for y in range(20):
            if not 0 in self.globals[0][y]: # completed line
                completed_lines.append(y)

        if len(completed_lines):
            self.globals[2] += board.points_per_line[len(completed_lines)]*level()
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
        if self.globals[7]:
            self.globals[1], self.globals[6] = self.globals[7], self.globals[1]
        else:
            self.globals[7] = self.globals[1]
            self.new_piece()

        self.has_switch = True

    def from_pattern(self, pattern, pos=[3, 0]):
        piece = Piece(0)
        piece.pattern = pattern
        piece.pos = pos
        return piece

    def rate_board(self):
        return sum([self.parameters[p]()*self.multipliers[p] for p in range(len(self.parameters))])

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

        for index, current_pat in [(0, pat), (1, hold_pat)]:
            for x in range(-2, 8):
                for rotation in range(4):
                    # reset variables
                    board_ = copy(b_copy)
                    self.globals = [board_, self.from_pattern(current_pat, [x, pos]), 0, 0, 0, None, self.from_pattern(next_piece.pattern, [x, pos]), self.from_pattern(hold_piece.pattern, [x, pos])]
                    if index:
                        self.switch_pieces()
                    piece_ = self.globals[1] # update after eventually switching
                    self.globals[5] = self.afraid()
                    if self.piece_collide() or (x, rotation) in self.forbidden:
                        scores[index][x+2][rotation] = -1000000
                        continue # not worth checking this case
                    while not self.piece_collide() or self.globals[4]%4 != rotation:
                        self.rotate_piece(rotation, piece_)

                        self.update_board_fast()
                        self.move_piece_fast()
                    self.update_board_fast() # check if any completed line
                    piece_.pos[1] -= 1
                    scores[index][x+2][rotation] = self.rate_board()

        bests = [[max(x) for x in scores[0]], [max(x) for x in scores[1]]]
        best_piece = int(max(bests[1]) > max(bests[0]))
        goto = bests[best_piece].index(max(bests[best_piece]))-2
        rotation = scores[best_piece][goto+2].index(max(scores[best_piece][goto+2]))

        self.ready = False # do not update the position rotation etc while modifying
        self.goto, self.rotation, self.switch = goto, rotation, best_piece
        self.ready = True
        self.queue.pop(0)

    def play(self):
        pressed = [] # will return this list that will trigger different events

        if self.prev_piece != board.piece:
            self.ready = False
            if board.hold:
                hold = board.hold
            else:
                hold = board.next
            args = (copy(board.board), board.piece.pos[1], [y[:] for y in board.piece.pattern], [y[:] for y in board.next.pattern], [y[:] for y in hold.pattern])
            self.goto = 3
            self.rotation = self.rotation_count = 0
            Thread(target=lambda: self.calculate(*args)).start()
            self.prev_piece = board.piece

        if self.switch:
            board.switch()
            self.switch = False
            self.rotation_count = 0
            self.prev_piece = board.piece

        if self.ready:
            pressed.extend(self.rotate_piece(self.rotation))
            if True:
                if board.piece.pos[0] > self.goto:
                    if board.piece.left():
                        board.piece.right() # cancel the movement
                        pressed.append(K_q)
                    else: # did not succeed: needs to go around sth?
                        self.forbidden.append((self.goto, self.rotation))
                        # retry, but forbid this position and rotation
                        self.prev_piece = None
                elif board.piece.pos[0] < self.goto:
                    if board.piece.right():
                        board.piece.left()
                        pressed.append(K_d)
                    else:
                        self.forbidden.append((self.goto, self.rotation))
                        self.prev_piece = None
                else:
                    if self.fast:
                        pressed.append(K_s)
                    else:
                        pressed.append(K_a)

        return pressed
