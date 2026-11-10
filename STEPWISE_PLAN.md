# Chess Bot — Step-by-Step Implementation Plan

> **Progress Philosophy:** Each phase delivers a working, testable game. Complete what you can — anything left at the end of a phase can be carried forward if time permits. Depth and polish come before the next phase begins.

---

## Phase 1 — Core Foundation & Playable GUI ✅ Complete

| Step | Task | Status |
| :--- | :--- | :--- |
| 1.1 | Initialize Pygame window with 8×8 chessboard | ✅ |
| 1.2 | Render rank (1–8) and file (a–h) coordinate labels | ✅ |
| 1.3 | Implement all piece movement with collision detection (Pawn, Rook, Knight, Bishop, Queen, King) | ✅ |
| 1.4 | Implement castling, en passant, and pawn promotion | ✅ |
| 1.5 | Implement check, checkmate, and stalemate detection | ✅ |
| 1.6 | Player vs Computer mode with basic Minimax AI | ✅ |
| 1.7 | Visual highlights: check warnings, selected square, valid move markers | ✅ |
| 1.8 | Smooth piece slide animation (cubic ease-out, 220ms) | ✅ |
| 1.9 | Scalable window + fullscreen toggle (F11) | ✅ |
| 1.10 | Undo (`U`/`Ctrl+Z`) and Redo (`Y`/`Ctrl+Y`) with full board state restoration | ✅ |
| 1.11 | `.gitignore`, `PLAN.md`, `HANDOVER.md`, team task files | ✅ |

---

## Phase 2 — Search Engine Optimization 🔄 In Progress

> **Goal:** Push the AI from depth-2 Minimax to a genuinely strong depth-3+ engine playable in under 1 second per move.

| Step | Task | Status | Member |
| :--- | :--- | :--- | :--- |
| 2.1 | Negamax framework (unified sign from side-to-move's view) | ✅ Done | B |
| 2.2 | Iterative Deepening with 800ms time budget | ✅ Done | B |
| 2.3 | Transposition Table (Zobrist 64-bit hashing, 1M entries, EXACT/LOWER/UPPER flags) | ✅ Done | B |
| 2.4 | MVV-LVA capture ordering | ✅ Done | B |
| 2.5 | Killer move heuristic (2 slots/ply) for quiet moves | ✅ Done | B |
| 2.6 | Quiescence search (capture extension, depth 4) | ✅ Done | B |
| 2.7 | Null-move pruning (R=2, disabled in check and endgames) | ⬜ Next | B |
| 2.8 | Late Move Reductions — LMR (reduce depth for late quiet moves, re-search if score beats α) | ⬜ Next | B |
| 2.9 | Principal Variation Search (PVS) + aspiration windows | ⬜ Next | B |
| 2.10 | History heuristic for quiet move ordering | ⬜ Next | B |
| 2.11 | Futility pruning at frontier nodes | ⬜ Next | B |
| 2.12 | Mate-distance scoring (prefer faster mates) | ⬜ Next | B |
| 2.13 | 50-move rule and threefold repetition detection | ⬜ Next | B |

---

## Phase 3 — Evaluation Function & Tuning 🔄 Parallel with Phase 2

> **Goal:** Replace pure material + PST evaluation with a richer, structurally aware scoring function.

| Step | Task | Status | Member |
| :--- | :--- | :--- | :--- |
| 3.1 | Pawn structure: doubled, isolated, passed pawn bonuses/penalties | ⬜ | C |
| 3.2 | King safety: pawn shelter, open files near king, attackers near king | ⬜ | C |
| 3.3 | Piece mobility: bonus per legal move available | ⬜ | C |
| 3.4 | Rook on open/half-open file bonus | ⬜ | C |
| 3.5 | Bishop pair bonus | ⬜ | C |
| 3.6 | Endgame detection (low material → switch to endgame king table) | ⬜ | C |
| 3.7 | Texel tuning — gradient descent on eval weights using game outcomes | ⬜ | C |
| 3.8 | NNUE evaluation: integrate pre-trained Stockfish NNUE `.nnue` weights | ⬜ | C |

---

## Phase 4 — Opening Book & Endgame Tablebases

> **Goal:** Make the first 10–15 moves instant and grandmaster-accurate; convert simple endgames perfectly.

| Step | Task | Status | Member |
| :--- | :--- | :--- | :--- |
| 4.1 | Load a Polyglot `.bin` opening book (`gm2001.bin`) | ⬜ | D |
| 4.2 | Query book by Zobrist key; fall back to Negamax when out of book | ⬜ | D |
| 4.3 | Display "Book Move" indicator in HUD when a book move is played | ⬜ | D |
| 4.4 | Lichess Opening Explorer API integration (live statistics overlay) | ⬜ | D |
| 4.5 | Lichess Tablebase API: query perfect play when ≤ 6 pieces remain | ⬜ | D |
| 4.6 | Local Syzygy WDL probing (optional — large download, only if time permits) | ⬜ | D |

---

## Phase 5 — GUI, UX & Assets

> **Goal:** Make the board visually polished and pleasant to play on any screen size.

| Step | Task | Status | Member |
| :--- | :--- | :--- | :--- |
| 5.1 | Load Lichess Cburnett SVG/PNG sprite set; render scaled sprites instead of Unicode glyphs | ⬜ | A |
| 5.2 | Side panel: move history (algebraic notation), material count, evaluation bar | ⬜ | A |
| 5.3 | Pawn promotion dialog — popup letting the player choose Queen / Rook / Bishop / Knight | ⬜ | A |
| 5.4 | Procedural sound effects (move click, capture thud, check bell) using numpy synthesis | ⬜ | A |
| 5.5 | Difficulty selector UI: Easy (depth 1–2) / Medium (depth 3) / Hard (depth 4+) | ⬜ | A |
| 5.6 | Side-switching option: play as Black | ⬜ | A |
| 5.7 | Board theme selector (Classic / Dark / High-contrast) | ⬜ | A |

---

## Phase 6 — Testing & Benchmarking

> **Goal:** Prove each Phase 2 / 3 upgrade actually raises strength before merging.

| Step | Task | Status | Member |
| :--- | :--- | :--- | :--- |
| 6.1 | Perft test suite: verify exact node counts at depths 1–5 from starting position | ⬜ | E |
| 6.2 | WAC tactics suite (300 positions): measure how many the engine solves | ⬜ | E |
| 6.3 | Automated engine-vs-engine match harness using CuteChess / Fastchess | ⬜ | E |
| 6.4 | SPRT (Sequential Probability Ratio Test) for statistically verified Elo gains | ⬜ | E |
| 6.5 | Nodes-per-second and effective-depth tracking for regression detection | ⬜ | E |
| 6.6 | STS (Strategic Test Suite) positional understanding score | ⬜ | E |

---

## Phase 7 — Reinforcement Learning (Last & Optional)

> **Prerequisite:** Phases 2–6 must be stable and benchmarked before starting RL work. RL is a separate experimental branch — the main engine remains the alpha-beta baseline.

| Step | Task | Description | Member |
| :--- | :--- | :--- | :--- |
| 7.1 | TD-Leaf(λ) on existing eval | Simplest RL: backpropagate temporal-difference errors through alpha-beta search leaf values. No GPU needed. | E |
| 7.2 | Texel / SPSA weight tuning | Use self-play game results to gradient-search better eval coefficients. | C + E |
| 7.3 | Small policy/value network | 3–5 layer MLP on board features; trained via supervised learning on Lichess database (10M+ positions). | E |
| 7.4 | MCTS + policy network | Replace Negamax with MCTS guided by trained policy/value heads. Compare Elo against alpha-beta baseline. | E |
| 7.5 | NNUE training pipeline | Label positions with the alpha-beta engine; train a 768→256 halfkp NNUE; integrate into search. | C + E |
| 7.6 | AlphaZero self-play (ambitious) | Bootstrap from supervised pretraining on labeled data; run self-play on GPU if available. | E |

---

## Notes

- **Build one feature at a time.** Each search technique can interact with others in unexpected ways. Test after every change with the perft suite and at least 100 engine-vs-engine games.
- **Never tune eval and search simultaneously.** Change one, verify it works, then tackle the other.
- **Keep a rollback commit** before any major Phase 2/3 change so you always have a working engine.
- **RL is last for a reason.** A buggy or weak alpha-beta baseline makes RL training results uninterpretable. Finish and benchmark the classical engine first.

