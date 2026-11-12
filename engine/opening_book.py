"""
Polyglot opening-book adapter for the project's custom board representation.

The game rules, board UI, evaluation and search engine remain the original project
implementation. python-chess is used only to calculate the standard Polyglot
position key and read the bundled .bin book.
"""
from pathlib import Path

import chess
import chess.polyglot

from core.game_logic import get_legal_moves

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BOOK_PATH = PROJECT_ROOT / "engine" / "openings.bin"

_PIECE_TYPES = {
    "Pawn": chess.PAWN,
    "Knight": chess.KNIGHT,
    "Bishop": chess.BISHOP,
    "Rook": chess.ROOK,
    "Queen": chess.QUEEN,
    "King": chess.KING,
}


def _to_chess_board(game):
    """Translate the current custom Game state into a python-chess board."""
    board = chess.Board(None)

    for piece in game.pieces:
        piece_type = _PIECE_TYPES.get(piece.__class__.__name__)
        if piece_type is None:
            continue
        square = chess.square(piece.col, 7 - piece.row)
        board.set_piece_at(
            square,
            chess.Piece(piece_type, piece.color == "white"),
        )

    board.turn = game.turn == "white"

    # Polyglot hashing includes castling rights. A right exists only when the
    # king and corresponding rook have not moved from their original squares.
    rights = chess.BB_EMPTY
    home_rank = 0 if game.turn == "black" else 7  # overwritten below per colour
    for color, rank in (("white", 7), ("black", 0)):
        king = game.grid[rank][4]
        if king is None or king.__class__.__name__ != "King" or king.color != color or not king.first_move:
            continue
        for rook_col, right_square in ((0, chess.BB_A1 if color == "white" else chess.BB_A8),
                                       (7, chess.BB_H1 if color == "white" else chess.BB_H8)):
            rook = game.grid[rank][rook_col]
            if rook is not None and rook.__class__.__name__ == "Rook" and rook.color == color and rook.first_move:
                rights |= right_square
    board.castling_rights = rights

    if game.en_passant_target is not None:
        row, col = game.en_passant_target
        board.ep_square = chess.square(col, 7 - row)

    return board


class PolyglotBook:
    """Read weighted legal moves from a Polyglot .bin opening book."""

    def __init__(self, path=DEFAULT_BOOK_PATH):
        self.path = Path(path)
        self.available = (
            self.path.is_file()
            and self.path.stat().st_size > 0
            and self.path.stat().st_size % 16 == 0
        )

    def get_move(self, game):
        """
        Return (piece, (target_row, target_col)) for a legal book move,
        or None if the position is not covered by the book.
        """
        if not self.available:
            return None

        board = _to_chess_board(game)
        try:
            with chess.polyglot.open_reader(str(self.path)) as reader:
                entry = reader.weighted_choice(board)
                move = entry.move
        except (IndexError, KeyError, OSError, ValueError):
            return None

        from_col = chess.square_file(move.from_square)
        from_row = 7 - chess.square_rank(move.from_square)
        to_col = chess.square_file(move.to_square)
        to_row = 7 - chess.square_rank(move.to_square)

        piece = game.grid[from_row][from_col]
        if piece is None or piece.color != game.ai_color:
            return None

        # The custom move generator is authoritative for this project.
        if (to_row, to_col) not in get_legal_moves(game, piece):
            return None

        return piece, (to_row, to_col)
