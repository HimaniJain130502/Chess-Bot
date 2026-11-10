# Task: Evaluation Function & Tuning
**Assigned To:** Member C  
**Topic:** Pawn structure, king safety, mobility, Texel tuning, NNUE integration  
**Dependencies:**
- **Requires:** `Search_Engine_Optimization.md` (Member B) — the search must be stable and passing perft tests before you tune the evaluation, otherwise you cannot tell whether Elo changes come from the search or the eval.
- **Coordinate with:** Member E (Testing) — use their benchmarking harness to validate every eval change.

> **Start:** You can design and unit-test individual evaluation terms (pawn structure, king safety, etc.) independently of the search. Only integrate them into the live engine once Member B signals the search is stable.

---

## Context

The current evaluation function in `Minimax_Alpha_Beta_Logic.py` is:

```
Score = Σ (material_value + PST_value) for each piece
```

This is a **pure material + positional** evaluation. It has no understanding of pawn structure, king danger, or piece mobility. Your task is to extend it in layers, then optionally replace the hand-crafted weights with learned ones via Texel tuning and NNUE.

All new evaluation code lives in a **new file: `Evaluation.py`**. The existing `evaluate_board()` in `Minimax_Alpha_Beta_Logic.py` will import from it.

---

## Tasks (in recommended order)

### C-1 · Refactor into `Evaluation.py`

Create `Evaluation.py` and move the existing PST-based evaluation there:

```python
# Evaluation.py

from Minimax_Alpha_Beta_Logic import PIECE_VALUES, PST_MAP, get_pst_value

def evaluate(game) -> int:
    """Master evaluation function: returns score in centipawns from white's view."""
    score = 0
    score += material_score(game)
    score += pst_score(game)
    score += pawn_structure_score(game)   # C-2
    score += king_safety_score(game)      # C-3
    score += mobility_score(game)         # C-4
    score += rook_placement_score(game)   # C-5
    return score
```

Then in `Minimax_Alpha_Beta_Logic.py`:
```python
from Evaluation import evaluate as evaluate_board
```

---

### C-2 · Pawn Structure

Penalty terms (all in centipawns):

| Term | White Penalty | Description |
| :--- | :--- | :--- |
| Doubled pawn | −20 | Two white pawns on the same file |
| Isolated pawn | −20 | No friendly pawns on adjacent files |
| Passed pawn bonus | +20 to +80 (by rank) | No enemy pawns blocking or guarding ahead |

```python
def pawn_structure_score(game) -> int:
    """Evaluate pawn structure: doubled, isolated, and passed pawns."""
    score = 0
    white_pawn_files = [p.col for p in game.pieces if p.__class__.__name__ == "Pawn" and p.color == "white"]
    black_pawn_files = [p.col for p in game.pieces if p.__class__.__name__ == "Pawn" and p.color == "black"]

    for p in game.pieces:
        if p.__class__.__name__ != "Pawn":
            continue

        col = p.col
        sign = 1 if p.color == "white" else -1
        own_files = white_pawn_files if p.color == "white" else black_pawn_files
        opp_files = black_pawn_files if p.color == "white" else white_pawn_files

        # Doubled pawn: more than one own pawn on same file
        if own_files.count(col) > 1:
            score -= sign * 20

        # Isolated pawn: no own pawns on adjacent files
        if (col - 1) not in own_files and (col + 1) not in own_files:
            score -= sign * 20

        # Passed pawn: no enemy pawns on same or adjacent files ahead of this pawn
        direction = -1 if p.color == "white" else 1
        rows_ahead = range(p.row + direction, 0 if direction == -1 else 8, direction)
        is_passed = all(
            opp_col not in [col - 1, col, col + 1]
            for opp_col in opp_files
        )
        if is_passed:
            # Bigger bonus closer to promotion
            advancement = (6 - p.row) if p.color == "white" else (p.row - 1)
            score += sign * (20 + advancement * 10)

    return score
```

---

### C-3 · King Safety

The King needs shelter. Evaluate:
1. **Pawn shield:** Bonus for friendly pawns in the 3 squares directly in front of the king.
2. **Open files:** Penalty for open or half-open files near the king (rooks/queens can attack).
3. **Enemy attackers near king:** Penalty weighted by attacker value.

```python
def king_safety_score(game) -> int:
    """Evaluate king safety: pawn shield, open files, and nearby attackers."""
    score = 0
    for color, sign in [("white", 1), ("black", -1)]:
        king = next((p for p in game.pieces if p.__class__.__name__ == "King" and p.color == color), None)
        if king is None:
            continue

        opp = "black" if color == "white" else "white"
        shield_direction = -1 if color == "white" else 1

        # Pawn shield bonus (up to 3 pawns in front)
        for dc in [-1, 0, 1]:
            shield_col = king.col + dc
            shield_row = king.row + shield_direction
            if 0 <= shield_col < 8 and 0 <= shield_row < 8:
                if game.grid[shield_row][shield_col] is not None:
                    p = game.grid[shield_row][shield_col]
                    if p.color == color and p.__class__.__name__ == "Pawn":
                        score += sign * 15

        # Open file near king: penalty
        for dc in [-1, 0, 1]:
            fc = king.col + dc
            if 0 <= fc < 8:
                file_pawns = [p for p in game.pieces if p.__class__.__name__ == "Pawn" and p.col == fc]
                if not file_pawns:
                    score -= sign * 20   # Fully open file: big danger
                elif not any(p.color == color for p in file_pawns):
                    score -= sign * 10   # Half-open file: moderate danger

    return score
```

---

### C-4 · Piece Mobility

Reward pieces that have many legal squares available. This encourages development and central control.

```python
def mobility_score(game) -> int:
    """Reward pieces with many available moves (legal pseudo-moves excluding King)."""
    score = 0
    MOBILITY_WEIGHT = {
        "Knight": 4, "Bishop": 3, "Rook": 2, "Queen": 1, "Pawn": 0, "King": 0
    }
    for piece in game.pieces:
        w = MOBILITY_WEIGHT.get(piece.__class__.__name__, 0)
        if w == 0:
            continue
        moves = piece.get_possible_moves(game.grid)
        sign  = 1 if piece.color == "white" else -1
        score += sign * w * len(moves)
    return score
```

---

### C-5 · Rook Placement

```python
def rook_placement_score(game) -> int:
    """Bonus for rooks on open or half-open files; bonus for rooks on 7th rank."""
    score = 0
    for piece in game.pieces:
        if piece.__class__.__name__ != "Rook":
            continue
        sign = 1 if piece.color == "white" else -1
        col  = piece.col

        # Check if file is open (no pawns) or half-open (no friendly pawns)
        file_pawns = [p for p in game.pieces if p.__class__.__name__ == "Pawn" and p.col == col]
        friendly   = [p for p in file_pawns if p.color == piece.color]
        if not file_pawns:
            score += sign * 20   # Open file
        elif not friendly:
            score += sign * 10   # Half-open file

        # 7th rank bonus (row 1 for white, row 6 for black)
        seventh = 1 if piece.color == "white" else 6
        if piece.row == seventh:
            score += sign * 20

    return score
```

---

### C-6 · Texel Tuning (parameter optimization)

Once evaluation terms are written, **tune their weights** using game outcomes.

**How it works:**
1. Collect a large set of positions (e.g. from self-play games, or from Lichess PGN downloads).
2. For each position, label it: win=1.0, draw=0.5, loss=0.0.
3. Use gradient descent to minimize: `Σ (sigmoid(eval(pos) / 400) − result)²`

```python
import math

def sigmoid(x, k=400):
    """Squash evaluation score into [0, 1] probability."""
    return 1.0 / (1.0 + math.exp(-x / k))

def texel_error(positions_results, weights):
    """Mean squared error between sigmoid(eval) and actual game result."""
    total = 0.0
    for pos, result in positions_results:
        score = evaluate_with_weights(pos, weights)
        total += (sigmoid(score) - result) ** 2
    return total / len(positions_results)
```

Use `scipy.optimize.minimize` or simple gradient-free SPSA for the optimization loop.

---

### C-7 · NNUE Integration (if time permits)

**NNUE** (Efficiently Updatable Neural Network) is the evaluation used by modern Stockfish. It can be integrated as a drop-in replacement for `evaluate_board()`.

**Approach:**
1. Download a pre-trained small NNUE model (e.g. from the Stockfish evaluation repository).
2. Use the `python-chess` library's NNUE probing or implement a simple forward pass in numpy.
3. The NNUE output plugs directly into `evaluate_board()`.

> This task requires significant research time. Implement C-1 through C-5 first. NNUE is a stretch goal.

---

## Completion Criteria

- [ ] `Evaluation.py` created and imported by `Minimax_Alpha_Beta_Logic.py`
- [ ] Pawn structure terms (doubled, isolated, passed) implemented and unit-tested
- [ ] King safety score reduces king exposure in test positions
- [ ] Mobility score rewards developed pieces
- [ ] Rook placement bonus encourages open files
- [ ] Texel tuning pipeline can run offline and output improved weights
- [ ] Engine with new eval beats old pure-PST engine in 100 self-play games (measured by Member E)

> **Note:** Complete tasks C-1 through C-5 in order. C-6 (Texel tuning) requires positions data to be collected first. C-7 (NNUE) is a stretch goal — only pursue it if all other tasks are complete and time permits.
