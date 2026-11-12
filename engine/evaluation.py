"""
Evaluation module for Chess-Bot.
Calculates dynamic board scores using material, piece-square tables,
pawn structure, king safety, mobility, and middlegame/endgame phase tapering.
"""

PIECE_VALUES = {
    "Pawn": 100,
    "Knight": 320,
    "Bishop": 330,
    "Rook": 500,
    "Queen": 900,
    "King": 20000,
}

PAWN_TABLE = [
    [0,   0,   0,   0,   0,   0,   0,   0],
    [50,  50,  50,  50,  50,  50,  50,  50],
    [10,  10,  20,  30,  30,  20,  10,  10],
    [5,   5,  10,  25,  25,  10,   5,   5],
    [0,   0,   0,  20,  20,   0,   0,   0],
    [5,  -5, -10,   0,   0, -10,  -5,   5],
    [5,  10,  10, -20, -20,  10,  10,   5],
    [0,   0,   0,   0,   0,   0,   0,   0],
]

KNIGHT_TABLE = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20,   0,   0,   0,   0, -20, -40],
    [-30,   0,  10,  15,  15,  10,   0, -30],
    [-30,   5,  15,  20,  20,  15,   5, -30],
    [-30,   0,  15,  20,  20,  15,   0, -30],
    [-30,   5,  10,  15,  15,  10,   5, -30],
    [-40, -20,   0,   5,   5,   0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50],
]

BISHOP_TABLE = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10,   0,   0,   0,   0,   0,   0, -10],
    [-10,   0,   5,  10,  10,   5,   0, -10],
    [-10,   5,   5,  10,  10,   5,   5, -10],
    [-10,   0,  10,  10,  10,  10,   0, -10],
    [-10,  10,  10,  10,  10,  10,  10, -10],
    [-10,   5,   0,   0,   0,   0,   5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20],
]

ROOK_TABLE = [
    [0,   0,   0,   0,   0,   0,   0,  0],
    [5,  10,  10,  10,  10,  10,  10,  5],
    [-5,  0,   0,   0,   0,   0,   0, -5],
    [-5,  0,   0,   0,   0,   0,   0, -5],
    [-5,  0,   0,   0,   0,   0,   0, -5],
    [-5,  0,   0,   0,   0,   0,   0, -5],
    [-5,  0,   0,   0,   0,   0,   0, -5],
    [0,   0,   0,   5,   5,   0,   0,  0],
]

QUEEN_TABLE = [
    [-20, -10, -10,  -5,  -5, -10, -10, -20],
    [-10,   0,   0,   0,   0,   0,   0, -10],
    [-10,   0,   5,   5,   5,   5,   0, -10],
    [ -5,   0,   5,   5,   5,   5,   0,  -5],
    [  0,   0,   5,   5,   5,   5,   0,  -5],
    [-10,   5,   5,   5,   5,   5,   0, -10],
    [-10,   0,   5,   0,   0,   0,   0, -10],
    [-20, -10, -10,  -5,  -5, -10, -10, -20],
]

KING_MIDDLE = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [ 20,  20,   0,   0,   0,   0,  20,  20],
    [ 20,  30,  10,   0,   0,  10,  30,  20],
]

KING_ENDGAME = [
    [-50, -30, -30, -30, -30, -30, -30, -50],
    [-30, -10,   0,   0,   0,   0, -10, -30],
    [-30,   0,  20,  30,  30,  20,   0, -30],
    [-30,   0,  30,  40,  40,  30,   0, -30],
    [-30,   0,  30,  40,  40,  30,   0, -30],
    [-30,   0,  20,  30,  30,  20,   0, -30],
    [-30, -10,   0,   0,   0,   0, -10, -30],
    [-50, -30, -30, -30, -30, -30, -30, -50],
]

PST_MAP = {
    "Pawn":   PAWN_TABLE,
    "Knight": KNIGHT_TABLE,
    "Bishop": BISHOP_TABLE,
    "Rook":   ROOK_TABLE,
    "Queen":  QUEEN_TABLE,
    "King":   KING_MIDDLE,
}


def compute_phase(game) -> int:
    """Calculate game phase: 24 (opening) down to 0 (endgame)."""
    phase_weights = {"Knight": 1, "Bishop": 1, "Rook": 2, "Queen": 4}
    phase = 0
    for p in game.pieces:
        if p is not None:
            phase += phase_weights.get(p.__class__.__name__, 0)
    return max(0, min(24, phase))


def get_pst_value(piece, phase: int = 24) -> int:
    """Return piece-square bonus for piece, smoothly interpolating King for endgame."""
    p_type = piece.__class__.__name__
    r, c = (piece.row, piece.col) if piece.color == "white" else (7 - piece.row, piece.col)

    if p_type == "King":
        mg_val = KING_MIDDLE[r][c]
        eg_val = KING_ENDGAME[r][c]
        return (mg_val * phase + eg_val * (24 - phase)) // 24

    table = PST_MAP.get(p_type)
    return table[r][c] if table else 0


def material_score(game) -> int:
    """Raw material sum in centipawns from White's perspective."""
    score = 0
    for piece in game.pieces:
        if piece is None:
            continue
        val = PIECE_VALUES.get(piece.__class__.__name__, 0)
        score += val if piece.color == "white" else -val
    return score


def pst_score(game, phase: int = 24) -> int:
    """Piece-square table positional score from White's perspective."""
    score = 0
    for piece in game.pieces:
        if piece is None:
            continue
        val = get_pst_value(piece, phase)
        score += val if piece.color == "white" else -val
    return score


def pawn_structure_score(game, phase: int = 24) -> int:
    """
    Evaluate pawn structure:
    - Doubled pawns (-20 cp)
    - Isolated pawns (-20 cp)
    - Passed pawns (+20 to +80 cp, dynamically boosted in endgame)
    """
    score = 0
    white_pawns = [p for p in game.pieces if p is not None and p.__class__.__name__ == "Pawn" and p.color == "white"]
    black_pawns = [p for p in game.pieces if p is not None and p.__class__.__name__ == "Pawn" and p.color == "black"]

    white_files = [p.col for p in white_pawns]
    black_files = [p.col for p in black_pawns]

    # Doubled pawns
    for col in range(8):
        w_count = white_files.count(col)
        if w_count > 1:
            score -= (w_count - 1) * 20
        b_count = black_files.count(col)
        if b_count > 1:
            score += (b_count - 1) * 20

    # Isolated pawns
    for p in white_pawns:
        if (p.col - 1) not in white_files and (p.col + 1) not in white_files:
            score -= 20
    for p in black_pawns:
        if (p.col - 1) not in black_files and (p.col + 1) not in black_files:
            score += 20

    # Passed pawns: bonus increases in endgame when pawns are closer to promoting
    passed_boost = (24 - phase) // 4
    for p in white_pawns:
        if not any(bp.col in (p.col - 1, p.col, p.col + 1) and bp.row < p.row for bp in black_pawns):
            advancement = 6 - p.row
            score += 20 + max(0, advancement) * (10 + passed_boost)

    for p in black_pawns:
        if not any(wp.col in (p.col - 1, p.col, p.col + 1) and wp.row > p.row for wp in white_pawns):
            advancement = p.row - 1
            score -= 20 + max(0, advancement) * (10 + passed_boost)

    return score


def king_safety_score(game, phase: int = 24) -> int:
    """
    Evaluate king safety dynamically based on phase:
    In the endgame (few major pieces left), king safety drops to zero as the king centralizes.
    """
    if phase <= 6:
        return 0

    score = 0
    pawns = [p for p in game.pieces if p is not None and p.__class__.__name__ == "Pawn"]

    for color, sign in [("white", 1), ("black", -1)]:
        king = next((p for p in game.pieces if p is not None and p.__class__.__name__ == "King" and p.color == color), None)
        if king is None:
            continue

        shield_dir = -1 if color == "white" else 1

        for dc in [-1, 0, 1]:
            fc = king.col + dc
            if 0 <= fc < 8:
                shield_row = king.row + shield_dir
                if 0 <= shield_row < 8:
                    occupant = game.grid[shield_row][fc]
                    if occupant is not None and occupant.color == color and occupant.__class__.__name__ == "Pawn":
                        score += sign * 15

                file_pawns = [p for p in pawns if p.col == fc]
                if not file_pawns:
                    score -= sign * 25
                elif not any(p.color == color for p in file_pawns):
                    score -= sign * 15

    return score


def mobility_score(game) -> int:
    """Reward piece activity based on count of available moves."""
    weights = {"Knight": 4, "Bishop": 4, "Rook": 2, "Queen": 1}
    score = 0
    for piece in game.pieces:
        if piece is None:
            continue
        w = weights.get(piece.__class__.__name__, 0)
        if w == 0:
            continue
        moves = piece.get_possible_moves(game.grid)
        sign = 1 if piece.color == "white" else -1
        score += sign * w * len(moves)
    return score


def rook_placement_score(game) -> int:
    """Reward rooks on open files (+20 cp), half-open files (+10 cp), and 7th rank (+20 cp)."""
    score = 0
    pawns = [p for p in game.pieces if p is not None and p.__class__.__name__ == "Pawn"]

    for piece in game.pieces:
        if piece is None or piece.__class__.__name__ != "Rook":
            continue

        sign = 1 if piece.color == "white" else -1
        file_pawns = [p for p in pawns if p.col == piece.col]
        friendly_pawns = [p for p in file_pawns if p.color == piece.color]

        if not file_pawns:
            score += sign * 20
        elif not friendly_pawns:
            score += sign * 10

        seventh_rank = 1 if piece.color == "white" else 6
        if piece.row == seventh_rank:
            score += sign * 20

    return score


def bishop_pair_score(game) -> int:
    """Bonus for retaining both bishops (+35 cp)."""
    score = 0
    white_bishops = sum(1 for p in game.pieces if p is not None and p.color == "white" and p.__class__.__name__ == "Bishop")
    black_bishops = sum(1 for p in game.pieces if p is not None and p.color == "black" and p.__class__.__name__ == "Bishop")

    if white_bishops >= 2:
        score += 35
    if black_bishops >= 2:
        score -= 35

    return score


def evaluate(game) -> int:
    """
    Master dynamic evaluation function.
    Returns centipawn score from White's perspective with game phase tapering.
    """
    phase = compute_phase(game)

    score = 0
    score += material_score(game)
    score += pst_score(game, phase)
    score += pawn_structure_score(game, phase)
    score += king_safety_score(game, phase)
    score += mobility_score(game)
    score += rook_placement_score(game)
    score += bishop_pair_score(game)
    return score


def evaluate_board(game) -> int:
    """Drop-in alias for search engine."""
    return evaluate(game)
