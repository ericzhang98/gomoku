import pygame
from pygame.locals import *
from board import *

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
    def loop(self):
        while self.going:
            self.update()
            self.draw()
            self.clock.tick(60)
        print("Game finished.")
        pygame.quit()
    # game controls
    def update(self):
        if self.auto:
            self.board.autoplay()
        for e in pygame.event.get():
            if e.type == QUIT:
                self.going = False
            if e.type == MOUSEBUTTONDOWN:
                self.auto = False
                success = self.board.handle_key_event(e)
                if success:
                    if self.semiauto:
                        self.board.semi_autoplay()
                else:
                    print "Bad mouse event"
            if e.type == KEYDOWN:
                if e.key == K_RETURN:
                    self.auto = not self.auto
                if e.key == K_SPACE:
                    self.board.restart()
                if e.key == K_m:
                    self.semiauto = not self.semiauto
    def draw(self):
        self.screen.fill((255, 255, 255))
        self.board.draw(self.screen)
        if self.board.game_over:
            self.screen.blit(self.font.render("{0} Won. Press Space to restart.".format("Black" if self.board.winner == 'b' else "White"), True, (0, 0, 0)), (10, 10))
        elif self.auto:
            self.screen.blit(self.font.render("AI Playing.", True, (0, 0, 0)), (10, 10))                        
        elif self.semiauto:
            self.screen.blit(self.font.render("Human's Turn ({0}). Press 'm' for manual play.".format("Black" if self.board.piece == 'b' else "White"), True, (0, 0, 0)), (10, 10))            
        else:
            self.screen.blit(self.font.render("Manual Play. {0}'s Turn.".format("Black" if self.board.piece == 'b' else "White"), True, (0, 0, 0)), (10, 10))            
        pygame.display.update()

if __name__ == '__main__':
    game = Gomoku()
    game.loop()
