"""
Chess piece classes and movement rules with collision detection and special moves.
"""


class Piece:
    """Base class for all chess pieces."""

    def __init__(self, color, row, col):
        """Initialize piece color, grid position, and first move status."""
        self.color = color
        self.row = row
        self.col = col
        self.first_move = True

    def move(self, row, col):
        """Update piece coordinates on the board."""
        self.row = row
        self.col = col

    def get_possible_moves(self, grid, en_passant_target=None):
        """Return list of pseudo-legal (row, col) target squares."""
        raise NotImplementedError("Subclasses must implement get_possible_moves()")

    def get_attack_squares(self, grid):
        """Return list of squares attacked or controlled by this piece."""
        return self.get_possible_moves(grid)


class Pawn(Piece):
    """Pawn piece with forward steps, diagonal captures, and en passant."""

    def get_possible_moves(self, grid, en_passant_target=None):
        """Calculate forward pushes, diagonal captures, and en passant."""
        moves = []
        direction = -1 if self.color == "white" else 1

        # 1-square forward advance
        forward_row = self.row + direction
        if 0 <= forward_row < 8 and grid[forward_row][self.col] is None:
            moves.append((forward_row, self.col))

            # 2-square forward advance from starting rank
            start_row = 6 if self.color == "white" else 1
            double_forward_row = self.row + 2 * direction
            if self.row == start_row and grid[double_forward_row][self.col] is None:
                moves.append((double_forward_row, self.col))

        # Standard diagonal captures
        for dc in [-1, 1]:
            diag_col = self.col + dc
            diag_row = self.row + direction
            if 0 <= diag_row < 8 and 0 <= diag_col < 8:
                target = grid[diag_row][diag_col]
                if target is not None and target.color != self.color:
                    moves.append((diag_row, diag_col))
                elif en_passant_target == (diag_row, diag_col):
                    moves.append((diag_row, diag_col))

        return moves

    def get_attack_squares(self, grid):
        """Return diagonal capture squares controlled by pawn."""
        attacks = []
        direction = -1 if self.color == "white" else 1
        for dc in [-1, 1]:
            diag_col = self.col + dc
            diag_row = self.row + direction
            if 0 <= diag_row < 8 and 0 <= diag_col < 8:
                attacks.append((diag_row, diag_col))
        return attacks


class Rook(Piece):
    """Rook piece moving horizontally and vertically across unoccupied squares."""

    def get_possible_moves(self, grid, en_passant_target=None):
        """Calculate orthogonal ray moves until blocked by pieces or board edge."""
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            r = self.row + dr
            c = self.col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = grid[r][c]
                if target is None:
                    moves.append((r, c))
                else:
                    if target.color != self.color:
                        moves.append((r, c))
                    break
                r += dr
                c += dc

        return moves


class Knight(Piece):
    """Knight piece performing non-blocking L-shaped jumps."""

    def get_possible_moves(self, grid, en_passant_target=None):
        """Calculate valid L-shaped jumps to empty squares or enemy pieces."""
        moves = []
        jumps = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        for dr, dc in jumps:
            r = self.row + dr
            c = self.col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target = grid[r][c]
                if target is None or target.color != self.color:
                    moves.append((r, c))

        return moves


class Bishop(Piece):
    """Bishop piece moving diagonally across unoccupied squares."""

    def get_possible_moves(self, grid, en_passant_target=None):
        """Calculate diagonal ray moves until blocked by pieces or board edge."""
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            r = self.row + dr
            c = self.col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = grid[r][c]
                if target is None:
                    moves.append((r, c))
                else:
                    if target.color != self.color:
                        moves.append((r, c))
                    break
                r += dr
                c += dc

        return moves


class Queen(Piece):
    """Queen piece combining rook and bishop ray movements."""

    def get_possible_moves(self, grid, en_passant_target=None):
        """Calculate 8-directional ray moves until blocked by pieces or board edge."""
        moves = []
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

        for dr, dc in directions:
            r = self.row + dr
            c = self.col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = grid[r][c]
                if target is None:
                    moves.append((r, c))
                else:
                    if target.color != self.color:
                        moves.append((r, c))
                    break
                r += dr
                c += dc

        return moves


class King(Piece):
    """King piece moving one step in any direction."""

    def get_possible_moves(self, grid, en_passant_target=None):
        """Calculate single-step moves in all 8 directions to valid squares."""
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r = self.row + dr
                c = self.col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    target = grid[r][c]
                    if target is None or target.color != self.color:
                        moves.append((r, c))

        return moves
