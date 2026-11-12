"""
FEN (Forsyth-Edwards Notation) loader.
Sets up board grid, pieces, turn, and en passant target from a FEN string.
"""

from core.pieces import Pawn, Knight, Bishop, Rook, Queen, King

PIECE_CLASS_MAP = {
    'p': Pawn,
    'n': Knight,
    'b': Bishop,
    'r': Rook,
    'q': Queen,
    'k': King,
}


def load_fen(game, fen: str):
    """Populate game state from a standard FEN string."""
    parts = fen.strip().split()
    board_part = parts[0]
    turn_part = parts[1] if len(parts) > 1 else 'w'
    ep_part = parts[3] if len(parts) > 3 else '-'

    game.pieces = []
    game.grid = [[None for _ in range(8)] for _ in range(8)]
    game.turn = "white" if turn_part == 'w' else "black"

    # En passant target
    if ep_part != '-' and len(ep_part) == 2:
        col = ord(ep_part[0].lower()) - ord('a')
        rank = int(ep_part[1])
        row = 8 - rank
        game.en_passant_target = (row, col) if 0 <= row < 8 and 0 <= col < 8 else None
    else:
        game.en_passant_target = None

    rows = board_part.split('/')
    for r_idx, row_str in enumerate(rows):
        c_idx = 0
        for ch in row_str:
            if ch.isdigit():
                c_idx += int(ch)
            else:
                color = "white" if ch.isupper() else "black"
                piece_cls = PIECE_CLASS_MAP[ch.lower()]
                piece = piece_cls(color, r_idx, c_idx)

                if piece_cls == Pawn:
                    start_row = 6 if color == "white" else 1
                    piece.first_move = (r_idx == start_row)
                else:
                    piece.first_move = True

                game.pieces.append(piece)
                game.grid[r_idx][c_idx] = piece
                c_idx += 1

    return game
