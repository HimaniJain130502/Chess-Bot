"""
Chess search engine: Negamax + Alpha-Beta, Iterative Deepening, Transposition Table
with Zobrist Hashing, MVV-LVA + Killer Move ordering, and Quiescence search.
"""
import random
from Game_logic import get_all_legal_moves, is_in_check

# Material values (centipawns)

PIECE_VALUES = {
    "Pawn": 100,
    "Knight": 320,
    "Bishop": 330,
    "Rook": 500,
    "Queen": 900,
    "King": 20000
}

# Piece-square tables (from White's perspective; flipped for Black)

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
PST_MAP = {
    "Pawn":   PAWN_TABLE,
    "Knight": KNIGHT_TABLE,
    "Bishop": BISHOP_TABLE,
    "Rook":   ROOK_TABLE,
    "Queen":  QUEEN_TABLE,
    "King":   KING_MIDDLE,
}

# ---------------------------------------------------------------------------
# Zobrist Hashing tables
# ---------------------------------------------------------------------------
_PIECE_INDEX = {
    ("white", "Pawn"): 0, ("white", "Knight"): 1, ("white", "Bishop"): 2,
    ("white", "Rook"): 3, ("white", "Queen"):  4, ("white", "King"):   5,
    ("black", "Pawn"): 6, ("black", "Knight"): 7, ("black", "Bishop"): 8,
    ("black", "Rook"): 9, ("black", "Queen"): 10, ("black", "King"):  11,
}
# 12 piece types × 64 squares + side-to-move + 4 castling rights + 8 ep files
_rng = random.Random(0xDEADBEEF)
_ZOBRIST_PIECES  = [[_rng.getrandbits(64) for _ in range(64)] for _ in range(12)]
_ZOBRIST_SIDE    = _rng.getrandbits(64)
_ZOBRIST_CASTLE  = [_rng.getrandbits(64) for _ in range(4)]   # wKS, wQS, bKS, bQS
_ZOBRIST_EP      = [_rng.getrandbits(64) for _ in range(8)]   # ep file a-h

# ---------------------------------------------------------------------------
# Transposition table
# TT entry: {"depth": int, "score": int, "flag": "EXACT"|"LOWER"|"UPPER",
#            "best_move": (piece_obj, (tr, tc))}
# ---------------------------------------------------------------------------
TT: dict = {}
TT_MAX_SIZE = 1 << 20   # ~1 M entries; evict on overflow


def compute_zobrist(game):
    """Compute full 64-bit Zobrist hash of the current board position."""
    h = 0
    for piece in game.pieces:
        if piece is None:
            continue
        idx = _PIECE_INDEX.get((piece.color, piece.__class__.__name__))
        if idx is not None:
            sq = piece.row * 8 + piece.col
            h ^= _ZOBRIST_PIECES[idx][sq]

    if game.turn == "black":
        h ^= _ZOBRIST_SIDE

    # Castling rights approximated by king/rook first_move flags
    for i, (r, c) in enumerate([(7, 7), (7, 0), (0, 7), (0, 0)]):
        p = game.grid[r][c]
        if p is not None and p.__class__.__name__ == "Rook" and p.first_move:
            h ^= _ZOBRIST_CASTLE[i]

    if game.en_passant_target is not None:
        h ^= _ZOBRIST_EP[game.en_passant_target[1]]

    return h


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------
def get_pst_value(piece):
    """Return piece-square bonus for the given piece at its current position."""
    table = PST_MAP.get(piece.__class__.__name__)
    if table is None:
        return 0
    r, c = (piece.row, piece.col) if piece.color == "white" else (7 - piece.row, piece.col)
    return table[r][c]


def evaluate_board(game):
    """Calculate static board score from white's perspective (centipawns)."""
    score = 0
    for piece in game.pieces:
        if piece is None:
            continue
        v = PIECE_VALUES.get(piece.__class__.__name__, 0) + get_pst_value(piece)
        score += v if piece.color == "white" else -v
    return score


# ---------------------------------------------------------------------------
# Killer moves: 2 slots per depth, max search depth 10
# ---------------------------------------------------------------------------
MAX_DEPTH = 10
_killers: list = [[None, None] for _ in range(MAX_DEPTH + 1)]


def store_killer(ply, move):
    """Record a quiet move that caused a beta-cutoff as a killer move at given ply."""
    if move != _killers[ply][0]:
        _killers[ply][1] = _killers[ply][0]
        _killers[ply][0] = move


def is_killer(ply, piece, tr, tc):
    """Check whether a quiet move matches a stored killer move at current ply."""
    for slot in _killers[ply]:
        if slot is not None and slot == (id(piece), tr, tc):
            return True
    return False


# ---------------------------------------------------------------------------
# Move ordering: TT best move → captures (MVV-LVA) → killers → center bias
# ---------------------------------------------------------------------------
def _move_score(game, piece, tr, tc, ply, tt_best):
    """Return ordering priority for a single move (higher = try first)."""
    # TT best move: search first
    if tt_best is not None and id(piece) == id(tt_best[0]) and (tr, tc) == tt_best[1]:
        return 200_000

    target = game.grid[tr][tc]
    is_ep  = (piece.__class__.__name__ == "Pawn" and
              game.en_passant_target is not None and
              (tr, tc) == game.en_passant_target)

    if target is not None or is_ep:
        victim_v  = PIECE_VALUES.get(target.__class__.__name__, 100) if target else 100
        attacker_v = PIECE_VALUES.get(piece.__class__.__name__, 100)
        # MVV-LVA: big victim, small attacker → high score
        return 100_000 + victim_v * 10 - attacker_v

    # Quiet killer moves
    if is_killer(ply, piece, tr, tc):
        return 50_000

    # Center proximity bonus for quiet moves
    return int(100 - (abs(3.5 - tr) + abs(3.5 - tc)) * 10)


def sort_moves(game, moves, ply=0, tt_best=None):
    """Sort legal moves in-place by priority (descending) to maximise alpha-beta cutoffs."""
    moves.sort(key=lambda m: _move_score(game, m[0], m[1][0], m[1][1], ply, tt_best), reverse=True)


# ---------------------------------------------------------------------------
# Move simulation / undo (used exclusively by the search, not the GUI)
# ---------------------------------------------------------------------------
def simulate_move(game, piece, tr, tc):
    """Apply move to the game state and return an undo snapshot; does NOT touch GUI state."""
    orig_r, orig_c = piece.row, piece.col
    orig_fm        = piece.first_move
    captured       = game.grid[tr][tc]
    prev_ep        = game.en_passant_target

    # En passant capture
    ep_cap = None
    is_ep  = (piece.__class__.__name__ == "Pawn" and
              game.en_passant_target is not None and
              (tr, tc) == game.en_passant_target and captured is None)
    if is_ep:
        ep_cap = game.grid[orig_r][tc]
        game.grid[orig_r][tc] = None
        if ep_cap in game.pieces:
            game.pieces.remove(ep_cap)

    # Standard capture
    if captured is not None and captured in game.pieces:
        game.pieces.remove(captured)

    # Place piece
    game.grid[orig_r][orig_c] = None
    game.grid[tr][tc] = piece
    piece.row, piece.col = tr, tc
    piece.first_move   = False

    # Castling: also move the rook
    castled = None
    if piece.__class__.__name__ == "King" and abs(tc - orig_c) == 2:
        rook_c_from, rook_c_to = (7, 5) if tc == 6 else (0, 3)
        rook = game.grid[orig_r][rook_c_from]
        if rook is not None:
            game.grid[orig_r][rook_c_from] = None
            game.grid[orig_r][rook_c_to]   = rook
            rook.col = rook_c_to
            castled  = (rook, orig_r, rook_c_from)

    # Update en passant target
    if piece.__class__.__name__ == "Pawn" and abs(tr - orig_r) == 2:
        game.en_passant_target = ((orig_r + tr) // 2, orig_c)
    else:
        game.en_passant_target = None

    # Pawn promotion in search: silently promote to Queen
    promoted = None
    if piece.__class__.__name__ == "Pawn" and (tr == 0 or tr == 7):
        from Pieces import Queen as Q
        promoted = Q(piece.color, tr, tc)
        promoted.first_move = False
        game.pieces.remove(piece)
        game.pieces.append(promoted)
        game.grid[tr][tc] = promoted

    # Switch side
    game.turn = "black" if game.turn == "white" else "white"

    return {
        "piece": piece, "orig": (orig_r, orig_c), "orig_fm": orig_fm,
        "captured": captured,
        "ep_cap": (ep_cap, orig_r, tc) if (is_ep and ep_cap) else None,
        "castled": castled,
        "promoted": promoted,
        "prev_ep": prev_ep,
    }


def undo_simulated_move(game, snap):
    """Revert game state from the snapshot returned by simulate_move."""
    piece  = snap["piece"]
    orig_r, orig_c = snap["orig"]
    cur_r,  cur_c  = piece.row, piece.col
    captured = snap["captured"]

    # Revert promotion
    if snap["promoted"] is not None:
        game.pieces.remove(snap["promoted"])
        game.pieces.append(piece)
        game.grid[cur_r][cur_c] = piece

    # Restore piece
    game.grid[cur_r][cur_c]   = captured
    game.grid[orig_r][orig_c] = piece
    piece.row, piece.col = orig_r, orig_c
    piece.first_move     = snap["orig_fm"]

    if captured is not None:
        game.pieces.append(captured)

    # Restore en passant capture
    if snap["ep_cap"] is not None:
        ep_p, ep_r, ep_c = snap["ep_cap"]
        game.grid[ep_r][ep_c] = ep_p
        game.pieces.append(ep_p)

    # Restore castled rook
    if snap["castled"] is not None:
        rook, r_orig_r, r_orig_c = snap["castled"]
        game.grid[rook.row][rook.col] = None
        game.grid[r_orig_r][r_orig_c] = rook
        rook.col  = r_orig_c

    # Restore en passant target and turn
    game.en_passant_target = snap["prev_ep"]
    game.turn = "black" if game.turn == "white" else "white"


# ---------------------------------------------------------------------------
# Quiescence search (stand-pat + captures only)
# ---------------------------------------------------------------------------
def quiescence(game, alpha, beta, ply, q_limit=4):
    """Extend search with captures until quiet; prevents horizon-effect blunders."""
    color       = game.turn
    sign        = 1 if color == "white" else -1
    stand_pat   = sign * evaluate_board(game)

    if q_limit == 0:
        return stand_pat

    if stand_pat >= beta:
        return beta
    alpha = max(alpha, stand_pat)

    all_moves = get_all_legal_moves(game, color)
    captures  = [(p, m) for p, m in all_moves if game.grid[m[0]][m[1]] is not None]
    sort_moves(game, captures, ply)

    for piece, (tr, tc) in captures:
        snap  = simulate_move(game, piece, tr, tc)
        score = -quiescence(game, -beta, -alpha, ply + 1, q_limit - 1)
        undo_simulated_move(game, snap)

        if score >= beta:
            return beta
        alpha = max(alpha, score)

    return alpha


# ---------------------------------------------------------------------------
# Negamax with Alpha-Beta, TT, and killer moves
# ---------------------------------------------------------------------------
MATE_SCORE = 99_000  # score returned for checkmate (adjusted by ply for faster-mate preference)


def negamax(game, depth, alpha, beta, ply, tt_best_in=None):
    """Negamax search with Alpha-Beta pruning, Transposition Table, and killer move ordering."""
    orig_alpha = alpha

    # --- Transposition table probe ---
    z_key = compute_zobrist(game)
    tt_entry = TT.get(z_key)
    tt_best  = None
    if tt_entry is not None and tt_entry["depth"] >= depth:
        tt_score = tt_entry["score"]
        flag     = tt_entry["flag"]
        tt_best  = tt_entry.get("best_move")
        if flag == "EXACT":
            return tt_score
        elif flag == "LOWER":
            alpha = max(alpha, tt_score)
        elif flag == "UPPER":
            beta  = min(beta,  tt_score)
        if alpha >= beta:
            return tt_score

    # --- Leaf node ---
    if depth <= 0:
        return quiescence(game, alpha, beta, ply)

    color     = game.turn
    all_moves = get_all_legal_moves(game, color)

    if not all_moves:
        if is_in_check(game.grid, game.pieces, color):
            return -(MATE_SCORE - ply)   # Prefer faster checkmates
        return 0  # Stalemate

    sort_moves(game, all_moves, ply, tt_best)

    best_score = -float("inf")
    best_move  = None

    for piece, (tr, tc) in all_moves:
        snap  = simulate_move(game, piece, tr, tc)
        score = -negamax(game, depth - 1, -beta, -alpha, ply + 1)
        undo_simulated_move(game, snap)

        if score > best_score:
            best_score = score
            best_move  = (piece, (tr, tc))

        alpha = max(alpha, score)
        if alpha >= beta:
            # Store killer for quiet moves only
            if game.grid[tr][tc] is None:
                store_killer(ply, (id(piece), tr, tc))
            break

    # --- Store result in Transposition Table ---
    if len(TT) >= TT_MAX_SIZE:
        TT.clear()   # Simple replacement: evict all when full

    flag = ("EXACT" if best_score > orig_alpha and best_score < beta else
            "LOWER" if best_score >= beta else "UPPER")
    TT[z_key] = {"depth": depth, "score": best_score, "flag": flag, "best_move": best_move}

    return best_score


# ---------------------------------------------------------------------------
# Iterative Deepening with time budget
# ---------------------------------------------------------------------------
def find_best_move(game, depth=3, time_limit_ms=800):
    """Search for optimal move using Iterative Deepening Negamax with time budget."""
    import time

    # Reset killer table for new search
    for i in range(MAX_DEPTH + 1):
        _killers[i] = [None, None]

    all_moves = get_all_legal_moves(game, game.turn)
    if not all_moves:
        return None

    # Seed ordering for depth-1 so iterative deepening can feed TT entries forward
    sort_moves(game, all_moves, ply=0)

    best_move   = all_moves[0]  # Always have a fallback after depth-1
    t_start     = time.time()

    for current_depth in range(1, depth + 1):
        # Stop if time already exceeded
        if (time.time() - t_start) * 1000 >= time_limit_ms:
            break

        z_key    = compute_zobrist(game)
        tt_best  = TT.get(z_key, {}).get("best_move")

        # Sort with TT best move from previous iteration at the front
        sort_moves(game, all_moves, ply=0, tt_best=tt_best)

        color      = game.turn
        sign       = 1 if color == "white" else -1
        alpha      = -float("inf")
        beta       = float("inf")
        depth_best = None

        for piece, (tr, tc) in all_moves:
            snap  = simulate_move(game, piece, tr, tc)
            score = -negamax(game, current_depth - 1, -beta, -alpha, ply=1)
            undo_simulated_move(game, snap)

            if score > alpha:
                alpha      = score
                depth_best = (piece, (tr, tc))

        if depth_best is not None:
            best_move = depth_best

    return best_move
