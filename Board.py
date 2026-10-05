import pygame

class Board:
    def __init__ (self):
        self.rows = 8
        self.cols = 8
        self.sq_size = 80
        self.width = self.cols * self.sq_size
        self.height = self.rows * self.sq_size
        self.ligsq = (255, 206, 158)
        self.darsq = (181,136,99)
        self.board = self.cr_b()
    def cr_b(self):
        board = [[("black", "R"), ("black", "N"), ("black", "B"), ("black", "Q"), ("black", "K"), ("black", "B"), ("black", "N"), ("black", "R")],
                [("black", "P"), ("black", "P"), ("black", "P"), ("black", "P"), ("black", "P"), ("black", "P"), ("black", "P"), ("black", "P")],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [("white", "P"), ("white", "P"), ("white", "P"), ("white", "P"), ("white", "P"), ("white", "P"), ("white", "P"), ("white", "P")],
                [("white", "R"), ("white", "N"), ("white", "B"), ("white", "Q"), ("white", "K"), ("white", "B"), ("white", "N"), ("white", "R")]
                ]
        return board
    def draw(self,screen):
        for row in range(self.rows):
            for col in range(self.cols):
                if (row + col) % 2 == 0:
                    color = self.ligsq
                else:
                    color = self.darsq
                pygame.draw.rect(screen, color, (col * self.sq_size, row * self.sq_size, self.sq_size, self.sq_size))