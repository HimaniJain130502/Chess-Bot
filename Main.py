from Board import Board
import pygame
import sys

from Game import Game

pygame.init()
Width = 640
Height = 640

screen = pygame.display.set_mode(Width,Height)
game = Game()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                game.handle_click(event.pos)
    game.draw(screen)
    pygame.display.update()

pygame.quit()
sys.exit()