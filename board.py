from __future__ import print_function
import pygame
from randplay import *
from pure_mcts import PureMCTS
from gomoku_state import *
from alphazero_mcts import AlphaZeroMCTS

ALPHA_ZERO = True

import numpy as np
seed = np.random.randint(999999)
print("Seed:", seed)
np.random.seed(seed)
# np.random.seed(61912)

# maintains current game state and interactions
class Board:
    def __init__(self):
        # game consts
        self.grid_len = GRID_LEN
        self.win_amt = WIN_AMT

        # ui
        self.grid_size = 46
        self.start_x, self.start_y = 30, 50
        self.edge_size = 0

        # curr game state
        self.piece = 'b'
        self.winner = None
        self.game_over = False
        self.grid = []
        self.history = [None, None]
        for i in range(self.grid_len):
            self.grid.append(list("." * self.grid_len))

    def handle_key_event(self, e):
        origin_x = self.start_x - self.edge_size
        origin_y = self.start_y - self.edge_size
        size = (self.grid_len - 1) * self.grid_size + self.edge_size * 2
        pos = e.pos
        if origin_x <= pos[0] <= origin_x + size and origin_y <= pos[1] <= origin_y + size:
            if not self.game_over:
                x = pos[0] - origin_x
                y = pos[1] - origin_y
                r = int((y+self.grid_size/2) // self.grid_size)
                c = int((x+self.grid_size/2) // self.grid_size)
                #print("Mouse event xy: ({}, {})".format(x, y))
                print("Mouse event rc: ({}, {})".format(r, c))
                if self.set_piece(r, c):
                    self.history.append((r,c))
                    self.check_win(r, c)
                    return True
        return False

    def set_piece(self, r, c):
        if self.grid[r][c] == '.':
            self.grid[r][c] = self.piece
            if self.piece == 'b':
                self.piece = 'w'
            else:
                self.piece = 'b'
            return True
        return False

    def autoplay(self):
        #Two automatic players against each other
        if not self.game_over:

            flat_grid = reduce(lambda x,y: x+y, self.grid)
            curr_state = GomokuState(flat_grid, self.piece, self.history[-1], self.history[-2])
            if ALPHA_ZERO:
                alphazero_mcts = AlphaZeroMCTS(curr_state)
                action = alphazero_mcts.uct_search()
            else:
                pure_mcts = PureMCTS(curr_state)
                action = pure_mcts.uct_search()
            (r, c) = action
            self.history.append(action)

            print("Auto", self.piece, "move: (", r, ",", c, ")")
            self.set_piece(r, c)
            self.check_win(r, c)

        if not self.game_over:

            flat_grid = reduce(lambda x,y: x+y, self.grid)
            curr_state = GomokuState(flat_grid, self.piece, self.history[-1], self.history[-2])
            if ALPHA_ZERO:
                alphazero_mcts = AlphaZeroMCTS(curr_state)
                action = alphazero_mcts.uct_search()
            else:
                pure_mcts = PureMCTS(curr_state)
                action = pure_mcts.uct_search()
            (r, c) = action
            self.history.append(action)

            print("Auto", self.piece, "move: (", r, ",", c, ")")
            self.set_piece(r, c)
            self.check_win(r, c)


    #Computer as one of the two players
    def semi_autoplay(self):
        if not self.game_over:

            flat_grid = reduce(lambda x,y: x+y, self.grid)
            curr_state = GomokuState(flat_grid, self.piece, self.history[-1], self.history[-2], board=None)
            if ALPHA_ZERO:
                alphazero_mcts = AlphaZeroMCTS(curr_state)
                action = alphazero_mcts.uct_search()
            else:
                pure_mcts = PureMCTS(curr_state)
                action = pure_mcts.uct_search()
            (r, c) = action
            self.history.append(action)

            print("Semi-Auto", self.piece, "move: (", r, ",", c, ")")
            self.set_piece(r, c)
            self.check_win(r, c)

            # asdf = AlphaZeroMCTS(GomokuState(reduce(lambda x,y: x+y, self.grid), self.piece, self.history[-1], self.history[-2], board=None))

    # check if a move causes a win
    def check_win(self, r, c):
        def get_continuous_count(r, c, dr, dc):
            piece = self.grid[r][c]
            result = 0
            i = 1
            while True:
                new_r = r + dr * i
                new_c = c + dc * i
                if 0 <= new_r < self.grid_len and 0 <= new_c < self.grid_len:
                    if self.grid[new_r][new_c] == piece:
                        result += 1
                    else:
                        break
                else:
                    break
                i += 1
            return result
        n_count = get_continuous_count(r, c, -1, 0)
        s_count = get_continuous_count(r, c, 1, 0)
        e_count = get_continuous_count(r, c, 0, 1)
        w_count = get_continuous_count(r, c, 0, -1)
        se_count = get_continuous_count(r, c, 1, 1)
        nw_count = get_continuous_count(r, c, -1, -1)
        ne_count = get_continuous_count(r, c, -1, 1)
        sw_count = get_continuous_count(r, c, 1, -1)
        if (n_count + s_count + 1 >= self.win_amt) or (e_count + w_count + 1 >= self.win_amt) or \
                (se_count + nw_count + 1 >= self.win_amt) or (ne_count + sw_count + 1 >= self.win_amt):
            self.winner = self.grid[r][c]
            self.game_over = True
    def restart(self):
        for r in range(self.grid_len):
            for c in range(self.grid_len):
                self.grid[r][c] = '.'
        self.piece = 'b'
        self.winner = None
        self.game_over = False
        self.history = [None, None]
    def draw(self, screen):
        # board and lines
        pygame.draw.rect(screen, (185, 122, 87),
                         [self.start_x - self.edge_size, self.start_y - self.edge_size,
                          (self.grid_len - 1) * self.grid_size + self.edge_size * 2, (self.grid_len - 1) * self.grid_size + self.edge_size * 2], 0)
        for r in range(self.grid_len):
            y = self.start_y + r * self.grid_size
            pygame.draw.line(screen, (0, 0, 0), [self.start_x, y], [self.start_x + self.grid_size * (self.grid_len - 1), y], 2)
        for c in range(self.grid_len):
            x = self.start_x + c * self.grid_size
            pygame.draw.line(screen, (0, 0, 0), [x, self.start_y], [x, self.start_y + self.grid_size * (self.grid_len - 1)], 2)
        # coordinates
        font = pygame.font.SysFont("comicsansms", 20)
        for i in range(self.grid_len):
            screen.blit(font.render("{}".format(i), True, (0, 0, 0)), (5, 35 + i*self.grid_size))
            screen.blit(font.render("{}".format(i), True, (0, 0, 0)), (25 + i*self.grid_size, 515))
        # pieces
        for r in range(self.grid_len):
            for c in range(self.grid_len):
                piece = self.grid[r][c]
                if piece != '.':
                    if piece == 'b':
                        color = (0, 0, 0)
                    else:
                        color = (255, 255, 255)
                    x = self.start_x + c * self.grid_size
                    y = self.start_y + r * self.grid_size
                    pygame.draw.circle(screen, color, [x, y], self.grid_size // 2)
