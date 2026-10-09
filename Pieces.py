class Piece:
    def __init__(self,color,row,col):
        self.color = color
        self.row = row
        self.col = col
    def move(self,row,col):
        self.row = row
        self.col = col

class Pawn(Piece):
    def __init__(self,color,row,col):
        super().__init__(color,row,col)
        self.first_move = True
    def poss_move(self):
        moves = []
        if self.color == "white":
            direction = -1
        else:
            direction = 1
        new_row = self.row + direction
        if 0 <= new_row < 8:
            moves.append((new_row, self.col))
        if self.first_move:
            new_row = self.row + 2 * direction
            if 0 <= new_row < 8:
                moves.append((new_row, self.col))
        return moves

class Rook(Piece):
    def poss_move(self):
        moves = []
        for row in range(self.row - 1, -1, -1):
            moves.append((row, self.col))
        for row in range(self.row + 1, 8):
            moves.append((row, self.col))
        for col in range(self.col - 1, -1, -1):
            moves.append((self.row, col))
        for col in range(self.col + 1, 8):
            moves.append((self.row, col))
        return moves

class Knight(Piece):
    def poss_move(self):
        moves = [
            (self.row - 2, self.col - 1),
            (self.row - 2, self.col + 1),
            (self.row - 1, self.col - 2),
            (self.row - 1, self.col + 2),
            (self.row + 1, self.col - 2),
            (self.row + 1, self.col + 2),
            (self.row + 2, self.col - 1),
            (self.row + 2, self.col + 1)
        ]
        return [
            (row, col)
            for row,col in moves
            if 0 <= row < 8 and 0 <= col < 8
        ]

class Bishop(Piece):
    def poss_moves(self):
        moves = []
        row = self.row - 1
        col = self.row - 1
        while row >= 0 and col >= 0:
            moves.append((row, col))
            row -= 1
            col -= 1
        row = self.row - 1
        col = self.col + 1
        while row >= 0 and col < 8:
            moves.append((row, col))
            row -= 1
            col += 1
        row = self.row + 1
        col = self.col - 1
        while row < 8 and col >= 0:
            moves.append((row, col))
            row += 1
            col -= 1
        row = self.row + 1
        col = self.col + 1
        while row < 8 and col < 8:
            moves.append((row, col))
            row += 1
            col += 1
        return moves

class Queen(Piece):
    def poss_moves(self):
        moves = []
        for row in range(self.row -1, -1, -1):
            moves.append((row, self.col))
        for row in range(self.row + 1, 8):
            moves.append((row, self.col))
        for col in range(self.col - 1, -1, -1):
            moves.append((self.row, col))
        for col in range(self.col + 1, 8):
            moves.append((self.row, col))
        row = self.row - 1
        col = self.col - 1
        while row >= 0 and col >= 0:
            moves.append((row, col))
            row -= 1
            col -= 1
        row = self.row - 1
        col = self.col - 1
        while row >= 0 and col >= 0:
            moves.append((row, col))
            row -= 1
            col -= 1
        row = self.row - 1
        col = self.col + 1
        while row >=0 and col < 8:
            moves.append((row, col))
            row -= 1
            col += 1
        row = self.row + 1
        col = self.col - 1
        while row < 8 and col >= 0:
            moves.append((row, col))
            row += 1
            col -= 1
        row = self.row + 1
        col = self.col + 1
        while row < 8 and col < 8:
            moves.append((row, col))
            row += 1
            col += 1
        return moves

class King(Piece):
    def poss_moves(self):
        moves = []
        for row in [-1,0,1]:
            for col in [-1,0,1]:
                if row == 0 and col == 0:
                    continue
                new_row = self.row + row
                new_col = self.col + col
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    moves.append((new_row, new_col))
        return moves
    