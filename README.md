# Chess-Bot

A modular, extensible Player vs. AI Chess Game built in Python with Pygame. Features an interactive responsive Lichess-style GUI, move validation, Polyglot opening book support, and a Negamax search engine with dynamic piece evaluation and game-phase tapering.

## Project Structure

```
Chess-Bot/
├── main.py                     # Entry point (launch the game)
├── requirements.txt            # Project dependencies for setup
├── core/                       # Core chess mechanics & rules
│   ├── pieces.py               # Piece classes and movement vectors
│   ├── game_logic.py           # Legal move filtering, check, checkmate, stalemate
│   ├── moves.py                # Algebraic notation and move formatting
│   └── fen.py                  # FEN string loader and board state parser
├── engine/                     # AI search, evaluation & opening book
│   ├── search.py               # Negamax search, Alpha-Beta pruning, TT, Iterative Deepening
│   ├── evaluation.py           # Dynamic evaluation (material, PST, pawns, king safety, phase tapering)
│   ├── opening_book.py         # Polyglot opening book reader
│   └── openings.bin            # Polyglot opening book binary data
├── gui/                        # Pygame graphical interface
│   ├── board.py                # Board rendering and dynamic square scaling
│   └── game.py                 # Game loop, turns, animations, HUD, undo/redo
├── tests/                      # Automated test & benchmark suite
│   ├── test_evaluation.py      # Unit tests for evaluation terms
│   └── benchmark_rating.py     # Calibrated tactical benchmark & Elo estimator
├── team_docs/                  # Team task assignments and technical roadmaps
├── HANDOVER.md                 # Architecture documentation and developer handover notes
├── PLAN.md                     # Architecture specification
└── STEPWISE_PLAN.md            # Phase-by-phase implementation plan
```

## Initial Setup & Launch

### Prerequisites
- Python 3.10+

### Installation

Install all required dependencies using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### Launch Game

Run the main application:

```bash
python main.py
```

### Controls & Shortcuts
- `Click`: Select piece / destination square
- `U` or `Ctrl+Z`: Undo move
- `Y` or `Ctrl+Y`: Redo move
- `R`: Restart game
- `F11`: Toggle fullscreen

## AI Engine Architecture

1. **Opening Book (`engine/opening_book.py`, `engine/openings.bin`)**:
   - Polyglot `.bin` opening book lookup
   - Instant grandmaster opening move selection

2. **Search Engine (`engine/search.py`)**:
   - Negamax with Alpha-Beta Pruning
   - Iterative Deepening with 800ms time budget
   - Transposition Table with 64-bit Zobrist Hashing
   - Move Ordering: TT best move, MVV-LVA capture sorting, Killer Moves
   - Quiescence Search to eliminate the horizon effect

3. **Dynamic Evaluation (`engine/evaluation.py`)**:
   - Material values and Piece-Square Tables (PST)
   - Dynamic Pawn Structure: doubled pawns, isolated pawns, and passed pawns
   - Dynamic King Safety: pawn shield bonuses and open-file danger penalties
   - Mobility: pseudo-legal move freedom per piece
   - Tactical placements: bishop pair bonus, rooks on open files and 7th rank
   - Game Phase Tapering: smooth interpolation between Middlegame and Endgame

## Testing & Benchmarks

Run the unit tests:
```bash
python -m unittest discover tests
```

Run the Elo rating benchmark:
```bash
python tests/benchmark_rating.py
```
