# Task: Search Engine Optimization
**Assigned To:** Member B  
**Topic:** Negamax, Null-Move Pruning, LMR, PVS, History Heuristic, Futility Pruning  
**Dependencies:** None — the baseline Negamax engine is already in place. Work directly in `Minimax_Alpha_Beta_Logic.py`.

> **Important for teammates:** Member C (Evaluation), Member D (Opening Book), and Member E (Testing) all depend on a **stable, correct** search engine. Avoid breaking the `find_best_move()` interface. If you change its signature, notify those teammates immediately.

---

## Context

The current engine in `Minimax_Alpha_Beta_Logic.py` implements:

| Feature | Status |
| :--- | :--- |
| Negamax + Alpha-Beta | ✅ Done |
| Iterative Deepening (800ms budget) | ✅ Done |
| Transposition Table (Zobrist, 1M entries) | ✅ Done |
| MVV-LVA capture ordering | ✅ Done |
| Killer move heuristic (2 slots/ply) | ✅ Done |
| Quiescence search (depth 4) | ✅ Done |
| **Null-move pruning** | ⬜ Your task |
| **Late Move Reductions (LMR)** | ⬜ Your task |
| **PVS + aspiration windows** | ⬜ Your task |
| **History heuristic** | ⬜ Your task |
| **Futility pruning** | ⬜ Your task |
| **50-move rule + repetition** | ⬜ Your task |

---

## Tasks (in recommended order)

### B-1 · History Heuristic for Quiet Move Ordering

Killer moves capture only 2 moves per ply. The **history heuristic** tracks *all* quiet moves that caused beta-cutoffs across the entire search, weighted by depth.

```python
# Add near top of Minimax_Alpha_Beta_Logic.py
_history: dict = {}   # key: (piece_class_name, to_square) → score

def update_history(piece, tr, tc, depth):
    """Reward a quiet move that caused a beta-cutoff by depth²."""
    key = (piece.__class__.__name__, tr * 8 + tc)
    _history[key] = _history.get(key, 0) + depth * depth

def history_score(piece, tr, tc):
    """Return accumulated history bonus for a quiet move."""
    return _history.get((piece.__class__.__name__, tr * 8 + tc), 0)
```

In `_move_score()`: after killers but before center-bias, add `history_score(piece, tr, tc)`.  
In `negamax()`: call `update_history(piece, tr, tc, depth)` when a quiet move causes a cutoff (`alpha >= beta`).  
Reset `_history` at the start of each `find_best_move()` call (or age it by halving).

---

### B-2 · Null-Move Pruning

If we can skip our turn and still be above beta, the position is so good we can prune the branch.

```python
# Inside negamax(), after the TT probe, before the move loop:
NULL_MOVE_R = 2  # reduction factor

# Safety checks before attempting null-move
in_check   = is_in_check(game.grid, game.pieces, game.turn)
piece_count = sum(1 for p in game.pieces if p.__class__.__name__ not in ("King", "Pawn"))
endgame    = piece_count <= 2  # Avoid null-move in zugzwang-prone endgames

if depth >= 3 and not in_check and not endgame:
    # Make a null move: just flip the side to move
    game.turn = "black" if game.turn == "white" else "white"
    prev_ep = game.en_passant_target
    game.en_passant_target = None

    null_score = -negamax(game, depth - 1 - NULL_MOVE_R, -beta, -beta + 1, ply + 1)

    game.turn = "black" if game.turn == "white" else "white"
    game.en_passant_target = prev_ep

    if null_score >= beta:
        return beta  # Null-move cutoff
```

> ⚠️ **Never apply null-move in check** (you can't skip a turn when in check). Also disable in King+pawn endgames where zugzwang is possible.

---

### B-3 · Late Move Reductions (LMR)

Moves tried late in the ordered list are likely to be bad. Search them at reduced depth; only re-search at full depth if they surprise you.

```python
# Inside the move loop of negamax(), after the first move:
LMR_MIN_DEPTH = 3
LMR_MIN_MOVE  = 4   # Start reducing from the 4th move onward

for move_index, (piece, (tr, tc)) in enumerate(all_moves):
    is_capture = game.grid[tr][tc] is not None
    is_check   = is_in_check(game.grid, game.pieces, game.turn)  # check before move

    snap = simulate_move(game, piece, tr, tc)

    if (move_index >= LMR_MIN_MOVE and depth >= LMR_MIN_DEPTH
            and not is_capture and not is_check):
        # Reduced-depth search
        reduction = max(1, int(depth ** 0.5))
        score = -negamax(game, depth - 1 - reduction, -alpha - 1, -alpha, ply + 1)
        # Re-search at full depth if the reduced search beats alpha
        if score > alpha:
            score = -negamax(game, depth - 1, -beta, -alpha, ply + 1)
    else:
        score = -negamax(game, depth - 1, -beta, -alpha, ply + 1)

    undo_simulated_move(game, snap)
    # ... rest of the loop
```

---

### B-4 · Principal Variation Search (PVS)

After the first (best) move is searched with a full `[alpha, beta]` window, search all remaining moves with a narrow null window `[alpha, alpha+1]`. Only re-search with full window if the null-window search fails high.

```python
# In the move loop, after move_index 0:
if move_index == 0:
    score = -negamax(game, depth - 1, -beta, -alpha, ply + 1)
else:
    # Null window search
    score = -negamax(game, depth - 1, -alpha - 1, -alpha, ply + 1)
    # Re-search if it beats alpha (potential new PV node)
    if alpha < score < beta:
        score = -negamax(game, depth - 1, -beta, -alpha, ply + 1)
```

---

### B-5 · Aspiration Windows

Instead of starting with `[-∞, +∞]` at the root of each iterative deepening iteration, start with a narrow window around the previous iteration's score. Widen on failure.

```python
# In find_best_move(), within the iterative deepening loop:
ASPIRATION_DELTA = 50  # 0.5 pawns in centipawns

if current_depth > 1 and prev_score is not None:
    alpha = prev_score - ASPIRATION_DELTA
    beta  = prev_score + ASPIRATION_DELTA
else:
    alpha = -float("inf")
    beta  =  float("inf")

while True:
    score = root_search(game, current_depth, alpha, beta)
    if score <= alpha:
        alpha -= ASPIRATION_DELTA * 2   # Widen left
    elif score >= beta:
        beta  += ASPIRATION_DELTA * 2   # Widen right
    else:
        prev_score = score
        break
```

---

### B-6 · 50-Move Rule & Threefold Repetition

**50-move rule:** Track half-move counter; if it reaches 100 (50 moves per side), return 0 (draw).

**Repetition:** Store a list of recent Zobrist keys during search. If the current key appears twice already in the list, return 0.

```python
# Add to simulate_move() return dict:
"halfmove_clock": game.halfmove_clock  # increment on quiet moves, reset on captures/pawn moves

# In negamax(), before move generation:
if game.halfmove_clock >= 100:
    return 0  # 50-move draw
if game.position_history.count(compute_zobrist(game)) >= 2:
    return 0  # Threefold repetition
```

---

### B-7 · Futility Pruning (if time permits)

At depth 1 (frontier nodes), if the static evaluation plus a margin is still below alpha, skip the move entirely.

```python
FUTILITY_MARGIN = {1: 100, 2: 300, 3: 500}  # centipawns per depth

# In negamax() before the move loop, at low depths:
if depth <= 3 and not is_in_check(...):
    static_eval = sign * evaluate_board(game)
    margin = FUTILITY_MARGIN.get(depth, 0)
    if static_eval + margin <= alpha:
        return quiescence(game, alpha, beta, ply)
```

---

## Completion Criteria

- [ ] History heuristic updates and improves quiet move ordering (measure: more cutoffs per node)
- [ ] Null-move pruning never fires in check; engine still passes all perft counts
- [ ] LMR reduces average search time at depth 3 by at least 20% vs. no-LMR baseline
- [ ] PVS + aspiration windows implemented and tested against baseline in 100 games
- [ ] 50-move and repetition rules prevent the bot from playing into known draws
- [ ] Perft test suite passes unchanged after every change

> **Note:** Complete tasks in order B-1 → B-6. Task B-7 (futility pruning) is a bonus — tackle it only if B-1 through B-6 are solid and time permits.

