# Chess Bot — Handover Document

> **Last updated:** November 2026  
> **Project lead:** Himani Jain (Repo: `HimaniJain130502/Chess-Bot`)

## 1. Project Overview

A fully playable **Player vs AI Chess Game** built in Python with Pygame. The player (White) faces a computer opponent (Black) powered by a Negamax search engine with Alpha-Beta pruning, Transposition Table, Iterative Deepening, MVV-LVA + Killer Move ordering, and dynamic game-phase tapered evaluation.

The goal is to progressively strengthen the engine and add quality-of-life features, following the phase-by-phase plan in `STEPWISE_PLAN.md`.

## 2. Tech Stack

| Layer | Technology |
| :--- | :--- |
| Language | Python 3.10+ |
| GUI Framework | `pygame-ce` 2.5+ |
| AI Search | Custom Negamax + Alpha-Beta |
| Version Control | Git / GitHub |

## 3. Project Structure

```
Chess-Bot/
├── main.py                     # Entry point — Pygame loop, fullscreen, resize, shortcuts
├── requirements.txt            # Project dependencies for setup
├── core/                       # Chess rules, piece physics & coordinate representations
│   ├── pieces.py               # Piece classes — movement rules with collision/capture logic
│   ├── game_logic.py           # Rules engine — legal moves, check, checkmate, stalemate
│   ├── moves.py                # Algebraic notation helpers — square conversion, move formatting
│   └── fen.py                  # FEN string loader and board state parser
├── engine/                     # AI decision making: search & evaluation
│   ├── evaluation.py           # Dynamic evaluation (material, PST, pawns, king safety, phase tapering)
│   ├── search.py               # Search engine — Negamax, Alpha-Beta, TT, ID, Quiescence
│   ├── opening_book.py         # Polyglot opening book reader
│   └── openings.bin            # Polyglot opening book binary data
├── gui/                        # Visual presentation & user interactions
│   ├── board.py                # Board rendering — squares, coordinate labels, responsive scale
│   └── game.py                 # Game controller — state, turns, animation, undo/redo, draw
├── tests/                      # Automated unit test suite
│   ├── test_evaluation.py      # Unit tests for evaluation terms
│   └── benchmark_rating.py     # Calibrated tactical benchmark & Elo estimator
├── team_docs/                  # Per-member task files (see Section 5)
├── PLAN.md                     # Architecture + Phase roadmap
├── STEPWISE_PLAN.md            # Ordered step-by-step implementation plan (all phases)
├── HANDOVER.md                 # This file
└── .gitignore
```

## 4. How to Run

```bash
# Install dependencies from requirements.txt
pip install -r requirements.txt

# Launch game
python main.py

# Run unit tests
python -m unittest discover tests
```

**Keyboard shortcuts:**

| Key | Action |
| :--- | :--- |
| `Click` | Select piece / move |
| `U` or `Ctrl+Z` | Undo move |
| `Y` or `Ctrl+Y` | Redo move |
| `R` | Restart game |
| `F11` | Toggle fullscreen |

## 5. Team & Task File Map

Each team member has dedicated files and documentation:

| Member | Topic | Code Working Files | Documentation | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Member A** | GUI, UX & Assets | `gui/board.py`, `gui/game.py` | `team_docs/GUI_and_UX.md` | Active |
| **Member B** | Search Optimization | `engine/search.py` | `team_docs/dep_Search+Evaluation/Search_Engine_Optimization.md` | Next Up |
| **Member C** | Evaluation & Tuning | `engine/evaluation.py` | `team_docs/dep_Search+Evaluation/Evaluation_Function_Tuning.md` | Complete |
| **Member D** | Opening Book & Tablebases | `engine/search.py` (hooks) | `team_docs/dep_Search+Opening_Tablebases/Opening_Book_Tablebases.md` | Queued |
| **Member E** | Testing & Benchmarking | `tests/` | `team_docs/dep_Testing+RL/Testing_Benchmarking_RL.md` | Active |

### Handover Note for Member B (Search Engine Optimization)
- The evaluation function has been completely decoupled from the search logic and lives in `engine/evaluation.py`.
- Your working file is `engine/search.py`.
- The evaluation API imported by `engine/search.py` is `from engine.evaluation import evaluate_board, PIECE_VALUES`.
- You can now implement your search optimizations (Null-Move Pruning, Late Move Reductions, History Heuristics, PVS) directly in `engine/search.py` without touching the evaluation logic.

## 6. Current AI Engine Capabilities

| Feature | Status | Location |
| :--- | :--- | :--- |
| Negamax + Alpha-Beta | Done | `engine/search.py` |
| Iterative Deepening (depth 3, 800ms) | Done | `engine/search.py` |
| Transposition Table (Zobrist, ~1M entries) | Done | `engine/search.py` |
| MVV-LVA move ordering | Done | `engine/search.py` |
| Killer move heuristic (2 slots/ply) | Done | `engine/search.py` |
| Quiescence search (capture extension, depth 4) | Done | `engine/search.py` |
| Dynamic Material & PST scoring | Done | `engine/evaluation.py` |
| Pawn structure (doubled, isolated, passed) | Done | `engine/evaluation.py` |
| King safety (pawn shields, open file threat) | Done | `engine/evaluation.py` |
| Piece mobility scoring | Done | `engine/evaluation.py` |
| Rook file placements & 7th rank | Done | `engine/evaluation.py` |
| Bishop pair bonus | Done | `engine/evaluation.py` |
| Game Phase Tapering (Middlegame vs Endgame) | Done | `engine/evaluation.py` |
| Null-move pruning | Member B Next | `engine/search.py` |
| Late Move Reductions (LMR) | Member B Next | `engine/search.py` |
| History heuristic | Member B Next | `engine/search.py` |
| PVS + aspiration windows | Member B Next | `engine/search.py` |
| Opening book (Polyglot) | Member D Next | `engine/search.py` |

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

## 8. Known Bugs / Open Issues

1. **Pawn promotion** silently upgrades to Queen during AI search simulation — no promotion choice for the AI. This is intentional for now; Member A can add a GUI promotion picker for the human player.
2. **Redo stack is cleared** when the player makes a new move (correct standard behavior).
3. **Stalemate and repetition** are detected but the **50-move rule** is not yet enforced.

## 9. Contacts & Resources

| Resource | Link |
| :--- | :--- |
| Repository | https://github.com/HimaniJain130502/Chess-Bot |
| Lichess Open API | https://lichess.org/api |
| Lichess Piece Sets (SVG) | https://github.com/lichess-org/lila/tree/master/public/piece |
