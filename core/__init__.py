"""
Core chess logic package: pieces, game rules, move notation, and FEN loader.
"""

from core.pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King
from core.game_logic import (
    get_legal_moves,
    get_all_legal_moves,
    is_in_check,
    is_checkmate,
    is_stalemate,
    find_king,
)
from core.moves import square_to_algebraic, format_move
from core.fen import load_fen
