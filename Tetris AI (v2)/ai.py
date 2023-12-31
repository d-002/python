import pygame
from random import choice
from pygame.locals import *
from threading import Thread

def send(*args):
    global Piece, Board, screen, clock, ticks, font
    Piece, Board, screen, clock, ticks, font = args

    global PseudoBoard, NewPseudoBoard
    class PseudoBoard(Board):
        # class like Board but with only what is needed during AI calculations
        def __init__(self, board):
            x, y, w, h = board.rect
            super().__init__((x, y), (w, h), board.seed, board.controller)
            
            # needed during calculations
            self.board = Ai.copy(board.board)

            # needes by internal functions and utilities
            self.garbage = board.garbage.copy()
            self.piece = self.hold = None # will be defined later, used by draw()
            self.next = [] # need a dummy value for draw()

        def drop(self, piece):
            # append the piece to the board
            for x in range(piece.len):
                for y in range(piece.len):
                    if piece.pattern[y][x]:
                        self.board[y+piece.y+20][x+piece.x] = piece.index

            # check line clears
            self.piece = piece
            lines = self.lines()

            # add garbage only if didn't clear lines
            if not lines[0]:
                g = self.garbage.copy()
                self.add_garbage()
                self.garbage = g # but make sure to not edit self.garbage

            return lines

    class NewPseudoBoard(Board):
        def __init__(self, board):
            x, y, w, h = board.rect
            super().__init__((x, y), (w, h), board.seed, board.controller)
            
        def drop(self, piece):
            # append the piece to the board
            for x in range(piece.len):
                for y in range(piece.len):
                    if piece.pattern[y][x]:
                        self.board[y+piece.y+20][x+piece.x] = piece.index

            # check line clears
            self.piece = piece
            lines = self.lines()

            # add garbage only if didn't clear lines
            if not lines[0]:
                g = self.garbage.copy()
                self.add_garbage()
                self.garbage = g # but make sure to not edit self.garbage

            return lines

class Ai:
    def __init__(self, pps, deep):
        self.pps = pps
        self.deep = deep

        self.last = 0

        # 0: upstack
        # 1: downstack
        self.strat = 0
        self.calculating = False
        self.action = None

        self.last_move = 0

        # when testing this AI
        self.tests = ['2220110222', '5555555340', '0133402444']
        self.test_index = 0

    def test(self, board, events):
        i = self.test_index
        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_1:
                    i -= 1
                elif event.key == K_3:
                    i += 1
                elif event.key == K_2: # refresh
                    self.test_index = 'dummy'

        if i != self.test_index:
            self.test_index = i%len(self.tests)
            height = [int(x) for x in self.tests[self.test_index]]
            copy = self.make_copy_for_thread(board)

            for x in range(10):
                for y in range(40):
                    if y < 40-height[x]:
                        copy['board'][y][x] = 0
                    else:
                        copy['board'][y][x] = 9
            _, self.action = self.calculate(copy['board'], copy['piece'], copy['hold'], copy['next'], self.deep)

            # update board to be the same as the copy
            for y in range(40):
                board.board[y] = copy['board'][y]
            self.act(board)

    @staticmethod
    def copy(array):
        return [[x for x in line] for line in array]

    def make_copy_for_thread(self, board):
        # make a copy of information about board to use it in parallel

        board_ = PseudoBoard(board)
        if board.hold is None:
            hold = None
        else:
            hold = Piece(board_, board.hold.index)

        return {'board': self.copy(board.board),
                'piece': Piece(board_, board.piece.index),
                'hold': hold,
                'next': [Piece(board_, piece.index) for piece in board.next],
                'board_obj': board_}

    def height(self, board):
        height = [40]*10
        for y in range(40):
            for x in range(10):
                if board[y][x] and height[x] == 40:
                    height[x] = y
        return height

    def holes(self, board):
        holes = 0
        height = [40]*10

        for y in range(40):
            for x in range(10):
                if board[y][x] and height[x] == 40:
                    height[x] = y
                elif not board[y][x] and height[x] != 40:
                    holes += 1
        return holes

    def height_diff(self, board):
        height = self.height(board)
        return [height[x+1]-height[x] for x in range(9)]

    def perfect(self, board, nexts):
        # checks if the next piece can be placed perfectly in different ways
        diff = self.height_diff(board)

        # how good it will be to place certain pieces
        score = [0]*7

        for x in range(8):
            # 3-long flat: good for T, J and L
            if diff[x] == diff[x+1] == 0:
                score[2] += 1
                score[3] += 1
                score[4] += 1

            # one wide hole: good for T
            if diff[x] == 1 and diff[x+1] == -1:
                score[2] += 1

        # 2-long flat: good for O
        score[1] += diff.count(0)

        for n in [0, 1]:
            for x in range(8):
                # 2-tall then 1-tall or opposite: good for S/Z
                if diff[x+n] == 2:
                    if diff[x+1-n] == 1:
                        score[5] += 1
                    elif diff[x+1-n] == -1:
                        score[6] += 1

                # 2-long flat next to 1-tall upstep: good for S/Z
                if diff[x+n] == 0:
                    if diff[x+1-n] == 2*n - 1:
                        score[5+n] += 1

        if len(nexts):
            return score[nexts[0].index-1]
        return sum(score)/7 # don't know what piece it will be: average value

    """def find_well(self, board, default=9):
        y_start = None
        for y in range(40):
            if sum(board[y]):
                y_start = y
                break
        if y_start is None:
            print('none')
            return default # no blocks in the board

        # find first at least 3-tall well and its column
        cols = [[y_start, 0, 0] for x in range(10)] # start, end, prev state (0=empty, 1=full)
        for y in range(y_start, 40):
            for x in range(10):
                b = bool(board[y][x])
                if b != cols[x][2]:
                    if b: # end of hole
                        print('end', x, y-20)
                        cols[x][1] = y
                        if cols[x][0] and cols[x][1]-cols[x][0] >= 3:
                            print('deep enough', x)
                            return x # found well
                    else: # start of hole
                        print('start', x, y-20)
                        cols[x][0] = y
                cols[x][2] = b
        # end open holes at the bottom
        print('bottom end')
        best = best_x = 0
        for x in range(10):
            if not cols[x][2]:
                h = 40-cols[x][0]
                print('score for', x, h)
                if h > best:
                    best, best_x = h, x
        print(best, best_x)
        return best_x"""

    def find_well(self, diff, default=9):
        likely = [0]*10
        likely[0] = -diff[0]
        likely[9] = diff[8]
        for x in range(1, 9):
            likely[x] = (diff[x-1]-diff[x])/2
        best, best_x = 0, default
        for x in range(10):
            if likely[x] > best:
                best, best_x = likely[x], x
        return best_x

    def I_dependency(self, board, ignore_well=False):
        diff = self.height_diff(board)
        if ignore_well:
            well = -1
        else: # exclude I dependencies for the well if specified
            well = self.find_well(diff)

        bad = 0
        for x in range(10):
            if x == 0:
                l = 0 # no height difference on the left for the left side
            else:
                l = diff[x-1]
            if x == 9:
                r = 0 # same on the right
            else:
                r = -diff[x]
            if (x == 0 or l >= 2) and (x == 9 or r >= 2):
                add = max(l+r-4, 0)
                if x != well:
                    bad += add
        return bad

    def cliffs(self, board):
        count = 0
        for h in self.height_diff(board):
            if abs(h) >= 3:
                count += abs(h)
        return count

    def lower_sides(self, board):
        height = self.height(board)
        return height[0]+height[9] - 2*sum(height)/10

    def strategy(self, board):
        holes = self.holes(board)

        top = 40 # get the top height
        for y in range(40):
            if sum(board[y]):
                top = y
                break

        if self.strat == 0:
            if top < 30:
                print('strat', 1)
                self.strat = 1
        elif self.strat == 1:
            if not holes and top > 30:
                print('strat', 0)
                self.strat = 0

    def score(self, board, nexts, piece, lines):
        #return -self.holes(board) + piece.y+lines[0]

        holes = self.holes(board)
        down = piece.y+lines[0]
        #cliffs = self.cliffs(board)

        if self.strat == 0:
            I_dep = self.I_dependency(board)
            normal_lines = lines[0] and lines[0] < 4 and not lines[1] and not lines[2]
            apm_lines = (lines[0] == 4)*4 or bool(lines[1])*lines[0]*2 or lines[2]*10

            #return -holes + down/2 - cliffs/5 + 10*apm_lines - 5*normal_lines
            #print(-holes, down/2, 5*I_dep, 10*apm_lines, -3*normal_lines)
            return -holes + down/2 - 5*I_dep + 10*apm_lines - 3*normal_lines

        if self.strat == 1:
            I_dep = self.I_dependency(board, True)
            lower_sides = self.lower_sides(board)
            #perfect = self.perfect(board, nexts)
            return -holes + down - 2*I_dep - lower_sides/2

    """
--- how calculate(n) works ---

bests = []
for each position/rotation:
    score = self.score()
    if n > 1:
        score2, _ = calculate(n-1)
        if score2 is not None:
            score += score2

    update bests if needed with (get score + score, action)

return choice(bests)
    """

    def calculate(self, board, piece, hold, nexts, n):
        # calculate the actions that make the best score for one piece

        bests = []
        max_score = None
        before = self.copy(board) # make a backup before this piece

        for h in [False, True]:
            if h:
                if hold is None:
                    piece, hold, nexts = nexts[0], piece, nexts[1:]
                else:
                    piece, hold = hold, piece
                hold.__init__(hold.master, hold.index) # revert changes made to hold

            for x in range(-2, 9):
                for rot in range(4):
                    if rot:
                        piece.rotate(rot, True)
                    piece.x = x

                    if not piece.collide(): # check if valid combination
                        while not piece.collide():
                            piece.y += 1
                        piece.y -= 1

                        self.strategy(board)
                        lines = piece.master.drop(piece)
                        board = piece.master.board
                        score = self.score(board, nexts, piece, lines)

                        score2 = None
                        if n > 1: # recursively update the score
                            new_piece, new_next = nexts[0], nexts[1:]
                            score2, _ = self.calculate(board, nexts[0], hold, nexts[1:], n-1)
                            piece.master.piece = piece # revert piece changes
                            if score2 is not None:
                                score += score2

                        if max_score is None or score >= max_score:
                            if score != max_score:
                                # found better solution than all others
                                bests = []
                                max_score = score
                            bests.append([x, rot, h])

                        if pygame.key.get_pressed()[K_LCTRL]:
                            piece.master.draw()
                            screen.blit(font.render(str(score), 1, (255, 255, 255)), (600, 200))
                            pygame.display.flip()
                            if pygame.key.get_pressed()[K_RCTRL]:
                                clock.tick(20)
                            else:
                                clock.tick(4)
                            pygame.event.get()

                    # revert changes
                    for y in range(len(before)):
                        board[y] = before[y].copy()
                    board = self.copy(before)
                    piece.__init__(piece.master, piece.index)

        if len(bests):
            return max_score, choice(bests)
        # didn't have any options (lose)
        return None, None

    def thread(self, board):
        copy = self.make_copy_for_thread(board)
        _, self.action = self.calculate(copy['board'], copy['piece'], copy['hold'], copy['next'], self.deep)
        self.calculating = False

    def act(self, board):
        x, rot, hold = self.action
        self.action = None

        if hold:
            board.switch()
        if rot:
            board.piece.rotate(rot)
        board.piece.x = x

        # drop the piece
        while not board.piece.collide():
            board.piece.y += 1
        board.piece.y -= 1

        #board.text = [str(self.find_well(self.height_diff(board.board))), ticks()]

        return board.drop()

    def update(self, board):
        if ticks()-self.last >= 1000/self.pps and self.action is None and not self.calculating:
            Thread(target=self.thread, args=(board,)).start()
            self.calculating = True
            self.last = ticks()
            return

        if self.action: # do the best action if calculated
            return self.act(board)

class NewAi:
    # some pieces (e.g. O) rotate differently, avoid testing useless cases
    piece_rotations = [2, 1, 4, 4, 4, 2, 2]

    def __init__(self, pps, deep):
        self.pps = pps
        self.deep = deep

        self.last = 0
        self.action = None
        self.calculating = False

        self.last_move = 0 # TODO: t-spins
        self.strat = 0 # 0: normal, 1: unstable board

    def test(self, *arg): return

    @staticmethod
    def copy(array):
        return [[x for x in line] for line in array]

    def fast_collide(self, piece):
        # same as piece.collide but less checks
        for y in range(piece.len):
            Y = piece.y+y+20
            for x in range(piece.len):
                if piece.pattern[y][x]:
                    if x+piece.x > 9 or Y > 39 or piece.master.board[Y][piece.x+x]:
                        return True

    def lr_collide(self, piece):
        # check if piece is out of bounds (left or right)
        for x in range(piece.len):
            X = x+piece.x
            for y in range(piece.len):
                if (X < 0 or X > 9) and piece.pattern[y][x]:
                    return True
        return False

    def cover_holes(self, board, piece_obj):
        # check if covered a pit trying to place the piece low
        holes = 0
        for x in range(piece_obj.x, piece_obj.x+piece_obj.len):
            covered = 0
            for y in range(piece_obj.y, 40):
                if 0 <= x < 10:
                    if board[y][x]:
                        if covered == 0: covered += 1
                        else: break
                    elif covered == 1: holes += 1
        return holes

    def new_holes(self, board, piece_obj):
        # search the minimum amount of cells for newly created holes
        holes = 0
        for x in range(piece_obj.x, piece_obj.x+piece_obj.len):
            covered = False
            for y in range(piece_obj.y, piece_obj.y+piece_obj.len+3):
                if 0 <= x < 10 and y < 20:
                    if board[y+20][x]: covered = True
                    elif covered: holes += 1
        return holes

    def total_holes(self, board):
        # search the entire grid
        holes = 0
        for x in range(10):
            covered = False
            for y in range(20, 40):
                if board[y][x]: covered = True
                elif covered: holes += 1
        return holes

    def bad(self, board):
        # total holes, height difference, pillars
        my = My = None
        dy = 0
        holes = 0
        for x in range(10):
            covered = 0
            height = 40
            for y in range(20,40):
                if board[y][x]:
                    if height == 40: height = y
                    covered = y
                    if my is None or y < my: my = y
                    if My is None or y > My: My = y
                elif covered:
                    holes += y-covered
                    break
            if height < 40 and x:
                dy += abs(height-prev) > 2
            prev = height
        return holes/2 + (My-my)-5 + dy*5-5

    """def lowleft(self, board):
        y2 = 40
        for y in range(20, 40):
            if board[y][1] and y2 == 40: y2 = y
            if board[y][0]: break
        return y-y2 > 4"""

    def score(self, board, piece_obj, lines):
        #holes = self.new_holes(board, piece_obj)
        holes = self.total_holes(board)
        cover = self.cover_holes(board, piece_obj)
        if self.strat == 0:
            lines_score = lines[1]*50 + lines[2]*1000 - (0 < lines[0] < 4)
            return -holes + piece_obj.y/2 + lines_score
        send = Board.getlines(lines)
        return -holes + piece_obj.y + send*20 - cover*5

    def calculate(self, copy, n):
        # TODO: fast place cancelling
        n -= 1

        piece_id = copy[2]

        piece_obj = Piece(copy[0], piece_id)
        n_rot = self.piece_rotations[piece_id-1]

        best = None
        best_score = 0
        for hold in (0, 1):
            if hold:
                if copy[2] == copy[3]: continue
                if copy[3] is None:
                    i, copy[3], copy[4] = copy[4][0], piece_id, copy[4][1:]
                else:
                    i, copy[3] = copy[3], piece_id
                piece_obj.setindex(i)

            for rotation in range(n_rot):
                for x in range(-2, 9):
                    board = self.copy(copy[1])
                    copy[0].board = board

                    # drop the piece at x position
                    piece_obj.x, piece_obj.y = x, 0
                    if piece_obj.collide():
                        continue
                        if self.lr_collide(piece_obj): # not a valid position
                            continue

                    while not self.fast_collide(piece_obj):
                        piece_obj.y += 1
                    piece_obj.y -= 1

                    if piece_obj.y < 0: score = None
                    else:
                        score = self.score(board, piece_obj, copy[0].drop(piece_obj))
                        if n: # continue trying with the next piece
                            copy[0].drop(piece_obj)
                            if len(copy[4]) > 1: _next = copy[4][1:] # use normal next
                            else: _next = shuffle(list(range(1, 8))) # use random next

                            found, _score = self.calculate([copy[0], board, copy[4][0], copy[3], _next], n)
                            if found is not None: score += _score

                    if best_score < score or best is None and score is not None:
                        best, best_score = (x, rotation, hold), score

                if rotation != n_rot-1:
                    piece_obj._rotate_()

        return best, best_score

    def thread(self, board):
        hold = board.hold.index if board.hold else None
        copy = [NewPseudoBoard(board), board.board, board.piece.index, hold, [p.index for p in board.next]]
        self.action, _ = self.calculate(copy, self.deep)
        self.calculating = False # tell the main thread calculations are done

    def act(self, board):
        # TODO: hold
        x, rot, hold = self.action
        if hold: board.switch()
        if rot:
            board.piece.rotate(rot)
        board.piece.x = x
        board.piece.y = 0

        # drop the piece
        while not self.fast_collide(board.piece):
            board.piece.y += 1
        board.piece.y -= 1

        # prepare for next action
        lines = board.drop()
        bad = self.bad(board.board)
        if self.strat == 0 and bad > 4: self.strat = 1
        elif bad < 2: self.strat = 0
        board.text = ["%d %d" %(bad, self.strat), ticks()]
        self.action = None

        return lines

    def update(self, board):
        if ticks()-self.last >= 1000/self.pps and self.action is not None:
            # play if it is time and has calculated
            self.last = ticks()
            return self.act(board)

        if self.action is None and not self.calculating:
            # start planning next move in a thread
            self.calculating = True
            self.action = None
            Thread(target=self.thread, args=(board,)).start()
