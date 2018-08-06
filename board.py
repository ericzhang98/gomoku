from __future__ import print_function
import pygame
from randplay import *
from mcts import *

# maintains current game state and interactions
class Board:
    def __init__(self):
        self.grid_size = 26
        self.start_x, self.start_y = 30, 50
        self.edge_size = 0
        self.grid_count = 19
        self.piece = 'b'
        self.winner = None
        self.game_over = False
        self.grid = []
        for i in range(self.grid_count):
            self.grid.append(list("." * self.grid_count))
    def handle_key_event(self, e):
        origin_x = self.start_x - self.edge_size
        origin_y = self.start_y - self.edge_size
        size = (self.grid_count - 1) * self.grid_size + self.edge_size * 2
        pos = e.pos
        if origin_x <= pos[0] <= origin_x + size and origin_y <= pos[1] <= origin_y + size:
            if not self.game_over:
                x = pos[0] - origin_x
                y = pos[1] - origin_y
                r = int(y // self.grid_size)
                c = int(x // self.grid_size)
                if self.set_piece(r, c):
                    self.check_win(r, c)
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
        #TODO: Modify player1 to be use MCTS instead of Randplay
            player1 = MCTS(self.grid, self.piece)
            r,c = player1.make_move()
            print("Auto", self.piece, "move: (", r, ",", c, ")")
            self.set_piece(r, c)
            self.check_win(r, c)    
        if not self.game_over:
            player2 = Randplay(self.grid, self.piece)
            r,c = player2.make_move()
            print("Auto", self.piece, "move: (", r, ",", c, ")")
            self.set_piece(r, c)
            self.check_win(r, c)
    #Computer as one of the two players
    def semi_autoplay(self):
        if not self.game_over:
            #Optional: Change this to MCTS AI and see whether you can win
            player1 = MCTS(self.grid, self.piece)
            r,c = player1.make_move()
            print("Semi-Auto", self.piece, "move: (", r, ",", c, ")")
            self.set_piece(r, c)
            self.check_win(r, c)
    # check if a move causes a win
    def check_win(self, r, c):
        def get_continuous_count(r, c, dr, dc):
            piece = self.grid[r][c]
            result = 0
            i = 1
            while True:
                new_r = r + dr * i
                new_c = c + dc * i
                if 0 <= new_r < self.grid_count and 0 <= new_c < self.grid_count:
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
        if (n_count + s_count + 1 >= 5) or (e_count + w_count + 1 >= 5) or \
                (se_count + nw_count + 1 >= 5) or (ne_count + sw_count + 1 >= 5):
            self.winner = self.grid[r][c]
            self.game_over = True
    def restart(self):
        for r in range(self.grid_count):
            for c in range(self.grid_count):
                self.grid[r][c] = '.'
        self.piece = 'b'
        self.winner = None
        self.game_over = False
    def draw(self, screen):
        # board and lines
        pygame.draw.rect(screen, (185, 122, 87),
                         [self.start_x - self.edge_size, self.start_y - self.edge_size,
                          (self.grid_count - 1) * self.grid_size + self.edge_size * 2, (self.grid_count - 1) * self.grid_size + self.edge_size * 2], 0)
        for r in range(self.grid_count):
            y = self.start_y + r * self.grid_size
            pygame.draw.line(screen, (0, 0, 0), [self.start_x, y], [self.start_x + self.grid_size * (self.grid_count - 1), y], 2)
        for c in range(self.grid_count):
            x = self.start_x + c * self.grid_size
            pygame.draw.line(screen, (0, 0, 0), [x, self.start_y], [x, self.start_y + self.grid_size * (self.grid_count - 1)], 2)
        # coordinates
        font = pygame.font.SysFont("comicsansms", 20)
        for i in range(19):
            screen.blit(font.render("{}".format(i), True, (0, 0, 0)), (5, 35 + i*26))
            screen.blit(font.render("{}".format(i), True, (0, 0, 0)), (25 + i*26, 515))
        # pieces
        for r in range(self.grid_count):
            for c in range(self.grid_count):
                piece = self.grid[r][c]
                if piece != '.':
                    if piece == 'b':
                        color = (0, 0, 0)
                    else:
                        color = (255, 255, 255)
                    x = self.start_x + c * self.grid_size
                    y = self.start_y + r * self.grid_size
                    pygame.draw.circle(screen, color, [x, y], self.grid_size // 2)