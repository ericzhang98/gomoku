import pygame
from pygame.locals import *
from board import *
import time

# main driver program for pygame
class Gomoku():
    # game settings and init
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((530, 550))
        pygame.display.set_caption("Gomoku")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("comicsansms",24)
        self.going = True
        self.board = Board()
        self.auto = False
        self.semiauto = True
        self.mcts_turn = False # True if mcts should go first, False if human should go first
        self.update_time = time.time()
    def loop(self):
        while self.going:
            self.update()
            self.draw()
            self.clock.tick(60)
        print("Game finished.")
        pygame.quit()

    # game controls
    def update(self):
        if time.time() > self.update_time+0.1 and (self.auto or (self.semiauto and self.mcts_turn)):
            self.board.mcts_play()
            if self.mcts_turn:
                self.mcts_turn = False
            self.update_time = time.time()
        for e in pygame.event.get():
            if e.type == QUIT:
                self.going = False
            if e.type == MOUSEBUTTONDOWN:
                self.auto = False
                success = self.board.handle_key_event(e)
                if success:
                    if self.semiauto:
                        self.mcts_turn = True
                        self.update_time = time.time()
                else:
                    print "Bad mouse event"
            if e.type == KEYDOWN:
                if e.key == K_RETURN:
                    self.auto = not self.auto
                if e.key == K_SPACE:
                    self.board.restart()
                if e.key == K_m:
                    self.auto = False
                    self.semiauto = not self.semiauto
                    self.mcts_turn = False

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.board.draw(self.screen)
        if self.board.game_over:
            self.screen.blit(self.font.render("{0} Won. Press Space to restart.".format("Black" if self.board.winner == 'b' else "White"), True, (0, 0, 0)), (10, 10))
        elif self.auto:
            self.screen.blit(self.font.render("AI ({}) Playing. Press Enter for semiauto".format("Black" if self.board.piece == 'b' else "White"), True, (0, 0, 0)), (10, 10))
        elif self.semiauto and not self.mcts_turn:
            self.screen.blit(self.font.render("Human's Turn ({0}). Press Enter for auto.".format("Black" if self.board.piece == 'b' else "White"), True, (0, 0, 0)), (10, 10))
        elif self.semiauto and self.mcts_turn:
            self.screen.blit(self.font.render("AI ({}) Thinking...".format("Black" if self.board.piece == 'b' else "White"), True, (0, 0, 0)), (10, 10))
        else:
            self.screen.blit(self.font.render("Manual Play. {0}'s Turn.".format("Black" if self.board.piece == 'b' else "White"), True, (0, 0, 0)), (10, 10))
        pygame.display.update()

if __name__ == '__main__':
    game = Gomoku()
    game.loop()
