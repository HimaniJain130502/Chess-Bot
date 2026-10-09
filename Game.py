import pygame

from Board import Board
from Pieces import Pawn, Rook, Knight, Bishop, Queen, King

class Game:
    def __init__(self):
        self.board = Board()
        self.selected_piece = None
        self.turn = "white" #White always starts first, needs to decide whether COmp or Human strats first irl
        self.pieces = self.cp() #Here, i Shall create the pieces
        self.font = pygame.font.SysFont("Arial", 55)
    def cp(self):
        pieces = []
        for row in range(8):
            for col in range(8):
                square = self.board.board[row][col]
                if square is None:
                    continue
                color, piece_type = square
                if piece_type == "P":
                    piece = Pawn(color, row, col)
                elif piece_type == "R":
                    piece = Rook(color, row, col)
                elif piece_type == "N":
                    piece = Knight(color, row, col)
                elif piece_type == "B":
                    piece = Bishop(color, row, col)
                elif piece_type == "Q":
                    piece = Queen(color, row, col)
                elif piece_type == "K":
                    piece = King(color, row, col)
                pieces.append(piece)
        return pieces
    def draw(self,screen):
        self.board.draw(screen)
        for piece in self.pieces:
            symbol = self.get_symbol(piece)
            text = self.font.render(symbol,True,(0,0,0))
            text_rect = text.get_rect(center=(piece.col * 80 + 40, piece.row * 80 + 40))
            screen.blit(text,text_rect)
        if self.selected_piece is not None:
            pygame.draw.rect(screen,(0,255,0),(
                self.selected_piece.col * 80,
                self.selected_piece.row * 80,
                80,80
            ),4)
    def get_symbol(self,piece):
        symbols = {

            ("white", "K"): "♔",
            ("white", "Q"): "♕",
            ("white", "R"): "♖",
            ("white", "B"): "♗",
            ("white", "N"): "♘",
            ("white", "P"): "♙",

            ("black", "K"): "♚",
            ("black", "Q"): "♛",
            ("black", "R"): "♜",
            ("black", "B"): "♝",
            ("black", "N"): "♞",
            ("black", "P"): "♟"
        }
        return symbols[((piece.color, piece.__class__.__name__[0]))]
    def handle_click(self,mouse_pos):
        x,y = mouse_pos
        col = x//80
        row = y //80
        if self.selected_piece is None:
            for piece in self.pieces:
                if piece.row == row and piece.col == col:
                    if piece.color == self.turn:
                        self.selected_piece = piece
                    return
                else:
                    piece = self.selected_piece
                    possible_moves = piece.possible_moves()
                    if (row,col) in possible_moves:
                        self.move_piece(piece,row,col)
                    self.selected_piece = None
    def move_piece(self,piece,row,col):
        captur = None
        for other_pi in self.pieces:
            if(other_pi.row == row and other_pi.col == col):
                captur = other_pi
                break
        if captur is not None:
            self.piece.remove(captur)
        piece.move(row,col)
        piece.first_move = False if hasattr(piece, "First Move") else None
        if self.turn == "white":
            self.turn = "black"
        else:
            self.turn = "white"