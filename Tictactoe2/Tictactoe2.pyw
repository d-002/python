import random
import pygame
from pygame.locals import *

class Game:
    colors = ((50, 50, 255), (255, 50, 50))

    def __init__(self, p1, p2, max):
        self.dot_pos = [(100 + i%3*200, 100 + i//3*200) for i in range(9)]
        self.bg = pygame.Surface((600, 600))
        self.links = [(0, 1), (1, 2), (0, 3), (2, 5), (3, 6), (5, 8), (6, 7), (7, 8)]
        for i in range(9):
            if i != 4: self.links.append((i, 4))
        for a, b in self.links:
            pygame.draw.aaline(self.bg, (100, 100, 100), self.dot_pos[a], self.dot_pos[b])
        for pos in self.dot_pos: pygame.draw.circle(self.bg, (150, 150, 150), pos, 10)

        self.players = (p1(self, 1), p2(self, 2))

        self.turn_id = 0
        self.turn_count = 0
        self.max_placed = max

        self.board = [0]*9

        self.over = False

    def reset(self):
        self.__init__(self.players[1].__class__, self.players[0].__class__, self.max_placed)
        self.colors = (self.colors[1], self.colors[0])

    def linked(self, *args):
        return args in self.links or (args[1], args[0]) in self.links

    def win(self, board):
        # returns 0 if no win, 1 if player 1 wins, 2 if player 2 wins
        for x in range(3):
            p = board[x]
            if p and p == board[x+3] == board[x+6]: return p
        for y in range(0, 9, 3):
            p = board[y]
            if p and p == board[y+1] == board[y+2]: return p
        p = board[4]
        if p and p == board[0] == board[8]: return p
        if p and p == board[2] == board[6]: return p
        if 0 not in board: return -1 # useful?
        return 0

    def update(self, events):
        # play
        if self.players[self.turn_id].play(events):
            self.turn_id = 1-self.turn_id
            if not self.turn_id: self.turn_count += 1

        w = self.win(self.board)
        if w:
            print(['', 'Player 1 wins', 'Player 2 wins', 'Tie'][w])
            self.over = True

    def draw(self):
        screen.blit(self.bg, (0, 0))
        for i in range(9):
            if self.board[i]:
                size = 60 if self.players[self.board[i]-1].selection == i else 50
                pygame.draw.circle(screen, self.colors[self.board[i]-1], (100 + i%3*200, 100 + i//3*200), size)

class Player:
    def __init__(self, game, id):
        self.game = game
        self.id = id
        self.selection = None # when moving a pawn

    def play(self, events):
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                i = x//200 + y//200*3
                if self.game.turn_count < self.game.max_placed:
                    if not self.game.board[i]:
                        self.game.board[i] = self.id
                        return True
                else:
                    if self.game.board[i] == self.id: self.selection = i
                    if not self.game.board[i] and self.selection is not None and self.game.linked(self.selection, i):
                        self.game.board[self.selection] = 0
                        self.game.board[i] = self.id
                        self.selection = None
                        return True

class Ai:
    def __init__(self, game, id):
        self.game = game
        self.id = id
        self.selection = None

    def play(self, events):
        return self._play()

    def _play(self):
        pass

class RandomAi(Ai):
    def __init__(self, *args):
        super().__init__(*args)

    def _play(self):
        empty = [i for i in range(9) if not self.game.board[i]]
        if self.game.turn_count < self.game.max_placed:
            self.game.board[random.choice(empty)] = self.id
        else:
            # get possible destinations from owned pawns
            mine = [i for i in range(9) if self.game.board[i] == self.id]
            possible = []
            for a in mine:
                pos = [b for b in range(9) if not self.game.board[b] and self.game.linked(a, b)]
                if len(pos):
                    possible.append((a, pos))

            a, b = random.choice(possible) # possible should not be empty
            b = random.choice(b)
            self.game.board[a] = 0
            self.game.board[b] = self.id
        return True

class HumanAi(Ai):
    def __init__(self, *args):
        super().__init__(*args)

    def _play(self):
        empty = [i for i in range(9) if not self.game.board[i]]
        if self.game.turn_count < self.game.max_placed:
            for p in empty:
                self.game.board[p] = self.id # try to win
                if self.game.win(self.game.board): return True
                self.game.board[p] = 3-self.id # try to cancel
                if self.game.win(self.game.board):
                    self.game.board[p] = self.id
                    return True
                self.game.board[p] = 0

            # otherwise play randomly
            self.game.board[random.choice(empty)] = self.id

        else:
            # get possible destinations from owned pawns
            mine = [i for i in range(9) if self.game.board[i] == self.id]
            possible = []
            for a in mine:
                pos = [b for b in range(9) if not self.game.board[b] and self.game.linked(a, b)]
                if len(pos):
                    possible.append((a, pos))

            for a, b in possible:
                self.game.board[a] = 0
                for b in b:
                    self.game.board[b] = self.id # try to win
                    if self.game.win(self.game.board): return True
                    self.game.board[b] = 3-self.id # try to cancel
                    if self.game.win(self.game.board):
                        self.game.board[b] = self.id
                        return True
                    self.game.board[b] = 0
                self.game.board[a] = self.id

            # otherwise play randomly
            a, b = random.choice(possible)
            b = random.choice(b)
            self.game.board[a] = 0
            self.game.board[b] = self.id
        return True

class MinimaxAi(Ai):
    def __init__(self, *args):
        super().__init__(*args)

        # /2 turns ahead
        self.deep = 6

    def score(self, w, deep):
        if w < 1: return 0
        return 100+deep if w == self.id else -100-deep

    def minimax(self, board, deep, id, turn):
        # stop when game ended or too deep
        w = self.game.win(board)
        if w or deep == 0:
            return self.score(w, deep)

        # get simulated turn count\
        if deep < self.deep and id == 1: turn += 1
        deep -= 1

        if turn < self.game.max_placed:
            # first phase
            # get possible moves
            possible = [i for i in range(9) if not board[i]]

            scores = []
            for p in possible:
                _board = [id if j == p else board[j] for j in range(9)]
                scores.append((self.minimax(_board, deep, 3-id, turn), p))
        else:
            # second phase
            # get possible destinations from owned pawns
            mine = [i for i in range(9) if board[i] == id]
            possible = []
            for a in mine:
                pos = [b for b in range(9) if not board[b] and self.game.linked(a, b)]
                if len(pos): possible.append((a, pos))

            scores = []
            for a, b in possible:
                for b in b:
                    _board = [0 if j == a else id if j == b else board[j] for j in range(9)]
                    scores.append((self.minimax(_board, deep, 3-id, turn), (a, b)))

        chosen = max(scores) if id == self.id else min(scores)

        # return score or move (at the end)
        return chosen[deep+1 == self.deep]

    def _play(self):
        move = self.minimax(self.game.board[:], self.deep, self.id, self.game.turn_count)
        if self.game.turn_count < self.game.max_placed:
            self.game.board[move] = self.id
        else:
            self.game.board[move[0]] = 0
            self.game.board[move[1]] = self.id
        return True

def printt(board):
    print()
    f = lambda i: '-XO'[board[i]]
    for y in range(0, 9, 3):
        print(f(y), f(y+1), f(y+2))

pygame.init()

screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption('Tic tac toe thing')
clock = pygame.time.Clock()
ticks = pygame.time.get_ticks

game = Game(Player, MinimaxAi, 3)

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            quit()
    
    game.draw()
    if game.over: game.reset()
    if not game.over: game.update(events)

    pygame.display.flip()
    #clock.tick(5)
