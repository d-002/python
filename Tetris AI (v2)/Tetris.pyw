import pygame
from random import random, randint, shuffle, seed
from pygame.locals import *

from ai import *

pieces = ['0000 1111 0000 0000', # I
          '0000 0110 0110 0000', # O
          '010 111 000', # T
          '100 111 000', # J
          '001 111 000', # L
          '011 110 000', # S
          '110 011 000'] # Z
colors = [(15, 155, 215),
          (227, 159, 2),
          (175, 41, 138),
          (33, 65, 198),
          (227, 91, 2),
          (89, 177, 1),
          (215, 15, 55),
          (50, 50, 50), # shadow
          (150, 150, 150)] # garbage
kick_table_normal = {(0, 1): [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
                     (1, 0): [(1, 0), (1, -1), (0, 2), (1, 2)],
                     (1, 2): [(1, 0), (1, -1), (0, 2), (1, 2)],
                     (2, 1): [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
                     (2, 3): [(1, 0), (1, 1), (0, -2), (1, -2)],
                     (3, 2): [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
                     (3, 0): [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
                     (0, 3): [(1, 0), (1, 1), (0, -2), (1, -2)]}
kick_table_I = {(0, 1): [(-2, 0), (1, 0), (-2, -1), (1, 2)],
                (1, 0): [(2, 0), (-1, 0), (2, 1), (-1, -2)],
                (1, 2): [(-1, 0), (2, 0), (-1, 2), (2, -1)],
                (2, 1): [(1, 0), (-2, 0), (1, -2), (-2, 1)],
                (2, 3): [(2, 0), (-1, 0), (2, 1), (-1, -2)],
                (3, 2): [(-2, 0), (1, 0), (-2, -1), (1, 2)],
                (3, 0): [(1, 0), (-2, 0), (1, -2), (-2, 1)],
                (0, 3): [(-1, 0), (2, 0), (-1, 2), (2, -1)]}

class Board:
    def __init__(self, pos, size, seed, controller):
        w, h = size[0]//10*10, size[1]//20*20
        self.rect = Rect(*pos, w, h)

        self.controller = controller

        self.board = [[0 for x in range(10)] for y in range(40)]

        self.seed = seed
        self.n_pieces = 0
        self.bag = []

        self.piece = self.new()
        self.next = [self.new() for _ in range(5)]
        self.hold = None
        self.has_hold = False

        self.target = None
        self.garbage = []
        self.total_lines = 0

        self.text = ['', 0] # text to print, when it appeared

    def new(self):
        if not len(self.bag):
            self.bag = list(range(1, 8))
            seed(self.seed+self.n_pieces)
            shuffle(self.bag)
        self.n_pieces += 1
        return Piece(self, self.bag.pop())

    def switch(self):
        # hold the piece
        if not self.has_hold:
            self.has_hold = True

        if self.hold is None:
            self.hold, self.piece = self.piece, self.next.pop(0)
            self.next.append(self.new())
        else:
            self.hold, self.piece = self.piece, self.hold
        self.hold.__init__(self, self.hold.index)

    def drop(self):
        # append the piece to the board
        for x in range(self.piece.len):
            for y in range(self.piece.len):
                if self.piece.pattern[y][x]:
                    self.board[y+self.piece.y+20][x+self.piece.x] = self.piece.index

        # check line clears
        lines = self.lines()

        # add garbage only if didn't clear lines
        if not lines[0]:
            self.add_garbage()

        # new piece
        self.piece = self.next.pop(0)
        self.next.append(self.new())

        # reset variables
        self.has_hold = False

        return lines

    def cleared_lines(self):
        # only check what are the filled lines and return them
        cleared = []
        for y in range(40):
            if not 0 in self.board[y]:
                cleared.append(y)
        self.total_lines += len(cleared)
        return cleared

    def lines(self):
        cleared = self.cleared_lines()

        # check for t-spin
        tspin = False
        # if T piece and rotated last
        if self.piece.index == 3 and self.controller.last_move == 1:
            n = 0
            for x, y in [(0, 0), (2, 0), (2, 2), (0, 2)]:
                X, Y = self.piece.x+x, self.piece.y+y+20
                n += not 0 <= X < 10 or not 0 <= Y < 40 or bool(self.board[Y][X])
            if n >= 3: # needs at least 3 filled corners to count as a t-spin
                tspin = True

        # clear filled lines
        if cleared:
            for line in cleared:
                for y in range(line, 0, -1):
                    self.board[y] = self.board[y-1]
                self.board[0] = [0]*10

        # check for pc
        pc = len(cleared) and not sum([sum(line) for line in self.board])

        return len(cleared), tspin, pc

    def add_garbage(self):
        # add garbage to the board
        total = 0
        while total < garbage_cap and len(self.garbage):
            add = min(garbage_cap-total, self.garbage[0])
            column = randint(0, 9)

            for n in range(add):
                for y in range(39):
                    self.board[y] = self.board[y+1]
                self.board[39] = [9]*10
                self.board[39][column] = 0

            total += add
            self.garbage[0] -= add
            if not self.garbage[0]:
                self.garbage.pop(0)

    def cancel(self, send):
        # try to cancel garbage: if cancelled, return updated sent lines
        if send > sum(self.garbage):
            send -= sum(self.garbage)
            self.garbage = []
            return send

        while send:
            g = self.garbage[0]
            if g <= send:
                send -= self.garbage.pop(0)
            else:
                self.garbage[0] -= send
                send = 0
        return send

    @staticmethod
    def getlines(lines):
        # number of lines sent after t-spins etc
        n, tspin, pc = lines
        if not n: return 0
        if tspin:
            send = 2*n
        else:
            send = [0, 1, 2, 4][n-1]
        return send + 10*pc

    def update(self, *args):
        # redirect actions to self.controller
        lines = self.controller.update(self, *args)

        # check line clears
        if lines is not None:
            send = self.getlines(lines)
            n, tspin, pc = lines
            if n:
                send = self.cancel(send)
                if send and self.target is not None:
                    self.target.garbage.append(send)

                # update action text
                self.text[1] = ticks()
                clears = ['Single', 'Double', 'Triple', 'Tetris']
                self.text[0] = 'Perfect\nClear\n'*pc
                if tspin:
                    self.text[0] += 'T-spin\n'+clears[n-1]
                else:
                    self.text[0] += clears[n-1]

    def draw(self):
        w, h = self.rect.w/10, self.rect.h/20

        # draw background
        pygame.draw.rect(screen, bg, self.rect)
        for x in range(11):
            if x in [0, 10]:
                c = 127
            else:
                c = 60
            x = self.rect.x + x*w
            pygame.draw.line(screen, (c, c, c), (x, self.rect.y), (x, self.rect.y + 20*h))
        for y in range(21):
            if y in [0, 20]:
                c = 127
            else:
                c = 60
            y = self.rect.y + y*h
            pygame.draw.line(screen, (c, c, c), (self.rect.x+1, y), (self.rect.x + 10*w - 1, y))

        # draw visible board tiles
        for x in range(10):
            for y in range(20):
                index = self.board[y+20][x]
                if index:
                    rect = Rect(self.rect.x + w*x, self.rect.y + h*y, w, h)
                    pygame.draw.rect(screen, colors[index-1], rect)

        # draw current piece and shadow
        prev_y = self.piece.y
        while not self.piece.collide():
            self.piece.y += 1
        self.piece.y, offset = prev_y, self.piece.y-prev_y-1

        for x in range(self.piece.len):
            for y in range(self.piece.len):
                if self.piece.pattern[y][x]:
                    X, Y = self.piece.x+x, self.piece.y+y
                    rect = Rect(self.rect.x + w*X, self.rect.y + h*Y, w, h)
                    pygame.draw.rect(screen, colors[self.piece.index-1], rect)
                    if offset:
                        shadow_rect = Rect(rect.x, rect.y + h*offset, w, h)
                        pygame.draw.rect(screen, colors[7], shadow_rect)

        # draw hold and next
        array = []
        y = 0
        for piece in self.next:
            array.append(((11, y), piece))
            y += piece.len
        if self.hold is not None:
            array.append(((-1.5-self.hold.len, 0), self.hold))

        for pos, piece in array:
            pos = (self.rect.x + w*pos[0], self.rect.y + h*pos[1])
            for x in range(piece.len):
                for y in range(piece.len):
                    if piece.pattern[y][x]:
                        rect = Rect(pos[0] + w*x, pos[1] + h*y, w, h)
                        pygame.draw.rect(screen, colors[piece.index-1], rect)

        # draw incoming garbage (limit in height)
        rect = Rect(self.rect.x - w/2, self.rect.y, w/2, 20*h + 1)
        pygame.draw.rect(screen, (127, 127, 127), rect)
        rect = Rect(rect.x+1, rect.y+1, rect.w-2, rect.h-2)
        pygame.draw.rect(screen, (0, 0, 0), rect)

        visible = []
        total = 0
        for g in self.garbage:
            y = min(g, 20.5-total)
            if y:
                visible.append(y)

            total += g
            if total > 20:
                break

        y = self.rect.y + 20*h
        for g in visible:
            g *= h
            pygame.draw.rect(screen, (255, 0, 0), Rect(self.rect.x - w/2 + 1, y-g+2, w/2 - 2, g-2))
            y -= g

        # draw garbage cap
        y = self.rect.y + (20-garbage_cap)*h
        pygame.draw.line(screen, (127, 127, 127), (self.rect.x - w/2, y), (self.rect.x, y))

        # draw action text
        if self.text[0] and ticks()-self.text[1] < 2000:
            x, y = self.rect.x - 3*w, self.rect.y + 10*h - 8

            for text in self.text[0].split('\n'):
                text = font.render(text, True, (255, 255, 255))
                text.set_alpha(min(255, (2000+self.text[1]-ticks()) / 1000 * 255))
                screen.blit(text, (x - text.get_width()/2, y))

                y += 16

        # display stats
        text = font.render('Lines cleared: %d' %self.total_lines, 1, (255, 255, 255))
        screen.blit(text, (self.rect.x + 5*w - text.get_width()/2, self.rect.y + 21*h))

class Piece:
    def __init__(self, master, index):
        self.master = master
        self.index = index # /!\ starts at 1
        self.x, self.y = 3, -1
        self.master.last_move = 0

        self.pattern = [[int(x)*self.index for x in line] for line in pieces[self.index-1].split(' ')]
        self.rotation = 0 # used for wall kicks
        self.len = len(self.pattern)

    def setindex(self, i):
        # used by NewAi, faster __init__
        self.index = i
        self.pattern = [[int(x)*self.index for x in line] for line in pieces[self.index-1].split(' ')]
        self.rotation = 0
        self.len = len(self.pattern)

    def move(self, x):
        self.x += x
        if self.collide():
            self.x -= x
            return False # did not succeed
        self.master.controller.last_move = 0
        return True # successfully moved

    def rotate(self, n, force=False):
        for _ in range(n):
            self._rotate_()

        goal = (self.rotation+n) % 4
        if force:
            succeed = True
        else:
            if n == 2:
                succeed = not self.collide()
            else:
                succeed = True
                if self.collide() and not self.wall_kick(self.rotation, goal):
                    succeed = False

        if succeed:
            self.rotation = goal
            self.master.controller.last_move = 1
        else:
            for _ in range(4-n): # rotate back
                self._rotate_()
        return succeed

    def wall_kick(self, a, b): # a and b are rotation indices
        prev_pos = (self.x, self.y)

        if self.index > 1:
            table = kick_table_normal
        else:
            table = kick_table_I

        for x, y in table[(a, b)]:
            self.x += x
            self.y -= y
            if not self.collide(): # found a valid position
                return True
            self.x, self.y = prev_pos # go back

        return False # couldn't wall kick

    def _rotate_(self):
        # rotate clockwise by 90 degrees
        new = [[0 for x in range(self.len)] for y in range(self.len)]
        for x in range(self.len):
            for y in range(self.len):
                new[x][y] = self.pattern[self.len-1-y][x]
        self.pattern = new

    def collide(self):
        for x in range(self.len):
            for y in range(self.len):
                X, Y = self.x+x, self.y+y+20
                if self.pattern[y][x]:
                    if not 0 <= X < 10 or not 0 <= Y < 40:
                        return True # out of bounds
                    if self.master.board[Y][X]:
                        return True # touching a board block
        return False

class Player:
    def __init__(self, das=100, arr=0):
        self.das = das
        self.arr = arr

        self.start_move = [None, None] # move left and right
        self.last_move = 0
        self.last_arr = None

    def sd(self, piece):
        # soft drop
        while not piece.collide():
            piece.y += 1
        piece.y -= 1

    def update(self, board, events):
        lines = None

        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_s:
                    self.sd(board.piece)
                    lines = board.drop()
                elif event.key == K_LEFT:
                    board.piece.rotate(3)
                elif event.key == K_DOWN:
                    board.piece.rotate(2)
                elif event.key == K_RIGHT:
                    board.piece.rotate(1)
                elif event.key == K_SPACE:
                    board.switch()

        pressed = pygame.key.get_pressed()
        if pressed[K_q]:
            self.sd(board.piece)
        for direction, index, key in [(-1, 0, K_a), (1, 1, K_d)]:
            if pressed[key]:
                if not self.start_move[index]: # started pressing button
                    board.piece.move(direction)
                    self.last_arr = None

                    # cancel opposite das
                    self.start_move = [None, None]
                    for x in range(2):
                        if x == index:
                            self.start_move[x] = ticks()

                elif self.last_arr is None: # start das
                    if ticks()-self.start_move[index] >= self.das:
                        if self.arr:
                            self.last_arr = ticks()
                        else: # move all the way directly
                            ok = True
                            while ok:
                                ok = board.piece.move(direction)

                elif ticks()-self.last_arr > self.arr: # in das, using arr
                    board.piece.move(direction)
                    self.last_arr = ticks()
            else:
                self.start_move[index] = None

        return lines

def restart(s=None):
    global player, ai, SEED
    if s is None: s = random()
    SEED = s
    player = Board((110, 50), (200, 400), SEED, Player())
    #ai = Board((500, 50), (200, 400), SEED, Ai(5, 1))
    ai = Board((500, 50), (200, 400), SEED, NewAi(3, 2))
    player.target = ai
    ai.target = player

pygame.init()

screen = pygame.display.set_mode((900, 500))
pygame.display.set_caption('Tetris')
font = pygame.font.SysFont('consolas', 16)
clock = pygame.time.Clock()
ticks = pygame.time.get_ticks

bg = (0, 0, 0)
garbage_cap = 8

restart()

test_ai = False
send(Piece, Board, screen, clock, ticks, font)

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            quit()
        elif event.type == KEYDOWN:
            if event.key == K_F4: restart()
            if event.key == K_0: test_ai = not test_ai # for testing Ai()

    screen.fill((30, 30, 30))

    player.update(events)
    player.draw()
    if test_ai:
        ai.controller.test(ai, events)
    else:
        ai.update()
    ai.draw()

    pygame.display.flip()
    clock.tick(60)
