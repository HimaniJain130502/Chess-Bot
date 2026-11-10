# Task: Testing, Benchmarking & Reinforcement Learning
**Assigned To:** Member E  
**Topic:** Perft verification, tactics suites, engine-vs-engine SPRT, RL exploration  
**Dependencies:**
- **Requires:** `Search_Engine_Optimization.md` (Member B) — perft and engine matches cannot run until the move generator and search are stable.
- **Requires for RL tasks:** `Evaluation_Function_Tuning.md` (Member C) — RL work builds on the eval function.
- You can write the perft framework and test infrastructure immediately. Run it once Member B declares the move generator stable.

---

## Context

Every upgrade to the search engine or evaluation must be **verified to actually improve strength**. Without rigorous testing:
- A bug might cause the engine to play illegal positions (caught by perft).
- A "feature" might actually reduce Elo (caught only by engine-vs-engine matches).
- Tactical sharpness might drop (caught by WAC suite).

Your job is to build the measurement infrastructure so every team member can confidently say "this change made the engine X Elo stronger."

---

## Tasks (in recommended order)

### E-1 · Perft Test Suite (move generator verification)

**Perft** counts the exact number of leaf nodes at depth N from a given position. Any deviation from the reference means a bug in move generation or legal move filtering.

Create `tests/perft.py`:

```python
# tests/perft.py
import os; os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame; pygame.init()
from Game import Game
from Minimax_Alpha_Beta_Logic import simulate_move, undo_simulated_move
from Game_logic import get_all_legal_moves


def perft(game, depth: int) -> int:
    """Count all leaf nodes at given depth from current position."""
    if depth == 0:
        return 1
    total = 0
    color = game.turn
    moves = get_all_legal_moves(game, color)
    for piece, (tr, tc) in moves:
        snap = simulate_move(game, piece, tr, tc)
        total += perft(game, depth - 1)
        undo_simulated_move(game, snap)
    return total


# Standard perft reference values from starting position
PERFT_EXPECTED = {
    1: 20,
    2: 400,
    3: 8902,
    4: 197281,
    5: 4865609,
}


def run_perft_suite():
    """Run perft at depths 1–5 and compare against reference counts."""
    game = Game(640, 700)
    all_passed = True
    for depth, expected in PERFT_EXPECTED.items():
        result = perft(game, depth)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"Perft({depth}): got {result:,}  expected {expected:,}  {status}")
        if result != expected:
            all_passed = False
    return all_passed


if __name__ == "__main__":
    run_perft_suite()
```

> Run this after **every change** to `Game_logic.py`, `Pieces.py`, or `Minimax_Alpha_Beta_Logic.py`. If perft fails, there is a bug in move generation — do not proceed until it passes.

---

### E-2 · WAC Tactics Suite (tactical sharpness test)

**Win at Chess (WAC)** is a set of 300 tactical positions. The engine should find the best move within a time limit. Measures tactical strength independently of Elo rating.

```python
# tests/wac_test.py
"""
WAC positions in EPD format.
Download WAC.epd from: https://www.chessprogramming.org/Win_at_Chess
Each line: FEN + "bm <best_move>;" (best move in SAN or UCI)
"""

def parse_epd(epd_line: str):
    """Parse one EPD line and return (fen, best_move_uci)."""
    parts = epd_line.strip().split(" bm ")
    fen   = parts[0]
    bm    = parts[1].split(";")[0].strip() if len(parts) > 1 else ""
    return fen, bm


def run_wac(engine_function, epd_path="tests/WAC.epd", time_limit_ms=500):
    """Test engine against WAC suite and report solve rate."""
    solved, total = 0, 0
    with open(epd_path) as f:
        for line in f:
            fen, bm = parse_epd(line)
            # Set up position from FEN (requires a FEN loader — see note below)
            # game = game_from_fen(fen)
            # move = engine_function(game, time_limit_ms=time_limit_ms)
            # if move matches bm: solved += 1
            total += 1
    print(f"WAC: {solved}/{total} solved ({100*solved/total:.1f}%)")
```

> **Note:** You will need a `game_from_fen(fen)` function to load arbitrary FEN positions. Coordinate with Member B or implement it yourself in `Moves.py`.

---

### E-3 · Nodes-Per-Second Tracker

Add lightweight performance instrumentation to the search:

```python
# In Minimax_Alpha_Beta_Logic.py, add a global counter:
_nodes_searched = 0

# Increment in negamax() at the top of each call:
global _nodes_searched
_nodes_searched += 1

# In find_best_move(), report at the end:
import time
elapsed = time.time() - t_start
nps = _nodes_searched / max(elapsed, 0.001)
print(f"Depth {depth} | Nodes: {_nodes_searched:,} | NPS: {nps:,.0f} | Time: {elapsed*1000:.0f}ms")
_nodes_searched = 0
```

Track NPS before and after each search technique (Null-move, LMR, PVS) to verify that node count decreases with no strength regression.

---

### E-4 · Engine-vs-Engine Match Harness

Write a script that plays two engine versions against each other and collects win/draw/loss statistics.

```python
# tests/engine_match.py
"""
Compare two engine configurations head-to-head.
Version A: current engine settings
Version B: new settings (e.g. different depth, eval change)
"""

import os; os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame; pygame.init()
from Game import Game
from Minimax_Alpha_Beta_Logic import find_best_move


def play_game(depth_white=2, depth_black=2, time_ms=500) -> str:
    """Play one complete game between two engine configs. Returns 'white', 'black', or 'draw'."""
    game = Game(640, 700)
    for _ in range(200):  # max 200 half-moves
        if game.game_over:
            break
        depth = depth_white if game.turn == "white" else depth_black
        move = find_best_move(game, depth=depth, time_limit_ms=time_ms)
        if move is None:
            break
        piece, (tr, tc) = move
        game.execute_move(piece, tr, tc)

    if "White" in game.game_status_text:
        return "white"
    elif "Black" in game.game_status_text or "Computer" in game.game_status_text:
        return "black"
    return "draw"


def run_match(games=20, depth_a=2, depth_b=3):
    """Run N games alternating colors and report win rate."""
    results = {"white": 0, "black": 0, "draw": 0}
    for i in range(games):
        # Alternate who plays which side
        if i % 2 == 0:
            result = play_game(depth_white=depth_a, depth_black=depth_b)
        else:
            result = play_game(depth_white=depth_b, depth_black=depth_a)
            result = {"white": "black", "black": "white", "draw": "draw"}[result]
        results[result] += 1
        print(f"Game {i+1}/{games}: {result}")

    print(f"\nResults: A wins={results['white']} B wins={results['black']} draws={results['draw']}")
    return results


if __name__ == "__main__":
    run_match(games=20, depth_a=2, depth_b=3)
```

---

### E-5 · SPRT (Statistical Verification of Elo Gains)

SPRT tells you whether a result is statistically significant **before** running 1000 games.

```python
# tests/sprt.py
import math

def elo_from_score(score: float) -> float:
    """Convert win-rate score to Elo difference."""
    if score <= 0 or score >= 1:
        return float("inf") if score >= 1 else float("-inf")
    return -400 * math.log10(1 / score - 1)


def sprt(wins: int, draws: int, losses: int, elo0=0, elo1=10, alpha=0.05, beta=0.05):
    """
    Sequential Probability Ratio Test.
    H0: Elo gain = elo0 (null: no improvement)
    H1: Elo gain = elo1 (alternative: at least +10 Elo)
    Returns: 'accept H1' | 'accept H0' | 'continue'
    """
    n = wins + draws + losses
    if n == 0:
        return "continue"

    score = (wins + 0.5 * draws) / n
    p0    = 1 / (1 + 10 ** (-elo0 / 400))
    p1    = 1 / (1 + 10 ** (-elo1 / 400))

    llr   = (wins * math.log(p1 / p0) +
             draws * math.log((1-p1+p1**2)**0.5 / (1-p0+p0**2)**0.5) +
             losses * math.log((1-p1) / (1-p0)))

    lower = math.log(beta / (1 - alpha))
    upper = math.log((1 - beta) / alpha)

    if llr >= upper:
        return f"Accept H1: change gains ≥ {elo1} Elo  (LLR={llr:.2f})"
    elif llr <= lower:
        return f"Accept H0: change gains < {elo1} Elo  (LLR={llr:.2f})"
    else:
        return f"Continue testing  (LLR={llr:.2f}, need {lower:.2f}..{upper:.2f})"
```

---

### E-6 · STS Positional Test Suite (if time permits)

The **Strategic Test Suite** measures positional understanding through 1500 positions with scored move lists.

Download from: https://www.chessprogramming.org/Strategic_Test_Suite

> Implement similarly to WAC (parse EPD, test best move). STS is broader — it tests positional concepts like outposts, pawn breaks, and piece coordination rather than pure tactics.

---

### E-7 · Reinforcement Learning: TD-Leaf(λ)

> **Prerequisites:** Phases 2 and 3 (search + eval) must be complete. This is the final step.

**TD-Leaf(λ)** applies temporal-difference learning through the alpha-beta search:

1. Play self-play games, recording positions and final game outcomes.
2. At each position, compute: `TD_error = V(final) - V(position)`
3. Update eval weights via gradient: `weight += α × TD_error × ∂V/∂weight`

```python
# rl/td_leaf.py

def self_play_game(game, depth=2):
    """Play one game of engine vs engine, recording (position_snapshot, eval) pairs."""
    history = []
    while not game.game_over:
        move = find_best_move(game, depth=depth)
        if move is None:
            break
        # Record eval before move
        eval_before = evaluate_board(game)
        history.append(eval_before)
        piece, (tr, tc) = move
        game.execute_move(piece, tr, tc)
    return history, game.game_status_text


def td_leaf_update(history, outcome, lam=0.7, lr=0.01):
    """Update eval weights using TD(λ) across recorded position evals."""
    n = len(history)
    for t in range(n):
        td_target = sum(lam**(k-t) * history[k] for k in range(t, n))
        td_error  = outcome - history[t]
        # weight_update = lr * td_error * gradient_of_eval_at_t
        # (gradient computation depends on eval parameterization)
        pass   # Expand this once Evaluation.py is parameterized
```

---

### E-8 · Small Policy/Value Network (stretch goal)

If TD-Leaf is working and time permits:
1. Train a small MLP (3–5 layers) on board features using supervised learning from Lichess database games.
2. Use the value head as a replacement for `evaluate_board()`.
3. Optionally wrap the search in MCTS guided by the policy head.

> This is a large research task. Only pursue it after E-1 through E-5 are complete and time permits.

---

## Test File Structure

```
tests/
├── perft.py          # E-1: Move generator correctness
├── wac_test.py       # E-2: Tactical sharpness (needs WAC.epd)
├── engine_match.py   # E-4: Head-to-head engine comparison
├── sprt.py           # E-5: Statistical significance test
└── WAC.epd           # Tactics positions (download separately)
rl/
├── td_leaf.py        # E-7: TD-Leaf RL training loop
└── policy_net.py     # E-8: Small neural network (stretch)
```

---

## Completion Criteria

- [ ] `perft.py` passes all 5 depth levels from starting position
- [ ] `engine_match.py` can run 20 games headlessly and report W/D/L
- [ ] SPRT module correctly signals when to stop testing
- [ ] WAC suite: engine solves ≥ 150 / 300 positions at depth 3 (≥ 50%)
- [ ] NPS tracker integrated and reports after each search call
- [ ] TD-Leaf self-play loop runs and updates eval weights without crashing

> **Note:** Complete tasks E-1 through E-5 in order — these are the essential testing infrastructure. E-6 (STS), E-7 (TD-Leaf), and E-8 (policy network) are progressively more ambitious. Work on them in order if time permits after the core tasks are done.
