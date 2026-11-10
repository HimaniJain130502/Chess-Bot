# Chess Bot — Handover Document

> **Last updated:** November 2026  
> **Project lead:** Himani Jain (Repo: `HimaniJain130502/Chess-Bot`)

---

## 1. Project Overview

A fully playable **Player vs AI Chess Game** built in Python with Pygame. The player (White) faces a computer opponent (Black) powered by a Negamax search engine with Alpha-Beta pruning, Transposition Table, Iterative Deepening, and MVV-LVA + Killer Move ordering.

The goal is to progressively strengthen the engine and add quality-of-life features, following the phase-by-phase plan in `STEPWISE_PLAN.md`.

---

## 2. Tech Stack

| Layer | Technology |
| :--- | :--- |
| Language | Python 3.11+ |
| GUI Framework | `pygame-ce` 2.5+ |
| AI Search | Custom Negamax + Alpha-Beta |
| Version Control | Git / GitHub |

---

## 3. Project Structure

```
Chess-Bot/
├── Main.py                     # Entry point — Pygame loop, fullscreen, resize, shortcuts
├── Game.py                     # Game controller — state, turns, animation, undo/redo, draw
├── Board.py                    # Board rendering — squares, coordinate labels, responsive scale
├── Pieces.py                   # Piece classes — movement rules with collision/capture logic
├── Game_logic.py               # Rules engine — legal moves, check, checkmate, stalemate
├── Moves.py                    # Algebraic notation helpers — square conversion, move formatting
├── Minimax_Alpha_Beta_Logic.py # AI engine — Negamax, Alpha-Beta, TT, ID, Quiescence
├── PLAN.md                     # Architecture + Phase roadmap
├── STEPWISE_PLAN.md            # Ordered step-by-step implementation plan (all phases)
├── HANDOVER.md                 # This file
├── .gitignore
└── team_docs/                  # Per-member task files (see Section 5)
```

---

## 4. How to Run

```bash
# Install dependency (only pygame-ce needed)
pip install pygame-ce

# Launch game
python Main.py
```

**Keyboard shortcuts:**

| Key | Action |
| :--- | :--- |
| `Click` | Select piece / move |
| `U` or `Ctrl+Z` | Undo move |
| `Y` or `Ctrl+Y` | Redo move |
| `R` | Restart game |
| `F11` | Toggle fullscreen |

---

## 5. Team & Task File Map

Each team member has one or more markdown task files in `team_docs/`. Task files that share a dependency are grouped in a subfolder.

| Member | Topic | File Location |
| :--- | :--- | :--- |
| **Member A** | GUI, UX & Assets | `team_docs/GUI_and_UX.md` |
| **Member B** | Search Engine Optimization | `team_docs/dep_Search+Evaluation/Search_Engine_Optimization.md` |
| **Member C** | Evaluation Function & Tuning | `team_docs/dep_Search+Evaluation/Evaluation_Function_Tuning.md` |
| **Member D** | Opening Book & Tablebases | `team_docs/dep_Search+Opening_Tablebases/Opening_Book_Tablebases.md` |
| **Member E** | Testing, Benchmarking & RL | `team_docs/dep_Testing+RL/Testing_Benchmarking_RL.md` |

### Dependency Map

```
GUI_and_UX                   ← Independent (start immediately)

Search_Engine_Optimization   ← Independent (start immediately)
  └── Evaluation_Function    ← Needs stable search first
  └── Opening_Tablebases     ← Needs stable search first
        └── Testing + RL     ← Needs stable search + eval
```

---

## 6. Current AI Engine Capabilities (Phase 1 → Phase 2 Transition)

| Feature | Status |
| :--- | :--- |
| Negamax + Alpha-Beta | ✅ Done |
| Iterative Deepening (depth 3, 800ms) | ✅ Done |
| Transposition Table (Zobrist, ~1M entries) | ✅ Done |
| MVV-LVA move ordering | ✅ Done |
| Killer move heuristic (2 slots/ply) | ✅ Done |
| Quiescence search (capture extension, depth 4) | ✅ Done |
| Piece-Square Tables (PST) | ✅ Done |
| Null-move pruning | ⬜ Next |
| Late Move Reductions (LMR) | ⬜ Next |
| PVS + aspiration windows | ⬜ Next |
| Opening book | ⬜ Next |
| NNUE evaluation | ⬜ Future |
| RL self-play | ⬜ Future |

---

## 7. Git Workflow

```bash
git pull origin main           # Always pull before starting work
git checkout -b feature/<name> # Create a feature branch
# ... make changes ...
git add .
git commit -m "feat: <short description>"
git push origin feature/<name>
# Open a Pull Request into main
```

**Never push directly to `main`.** Open a PR and get at least one review.

---

## 8. Known Bugs / Open Issues

1. **Pawn promotion** silently upgrades to Queen during AI search simulation — no promotion choice for the AI. This is intentional for now; Member A can add a GUI promotion picker for the human player.
2. **Redo stack is cleared** when the player makes a new move (correct behavior — same as most editors).
3. **Stalemate and repetition** are detected but the **50-move rule** is not yet enforced.

---

## 9. Contacts & Resources

| Resource | Link |
| :--- | :--- |
| Repository | https://github.com/HimaniJain130502/Chess-Bot |
| Lichess Open API | https://lichess.org/api |
| Lichess Piece Sets (SVG) | https://github.com/lichess-org/lila/tree/master/public/piece |
| Polyglot Opening Books | https://www.chessprogramming.org/Polyglot |
| Syzygy Tablebases | https://syzygy-tables.info |
| Chess Programming Wiki | https://www.chessprogramming.org |
| WAC Tactics Suite | https://www.chessprogramming.org/Win_at_Chess |

