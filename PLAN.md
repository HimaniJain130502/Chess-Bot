# Chess Bot Development Roadmap

This document outlines the tightened engineering roadmap, architecture corrections, external resources, and build order for developing an advanced AI-powered Chess Engine.

---

## Architecture & Search Insights

### 1. Paradigm Roles in Chess AI
| Paradigm | Move Selection Fit | Real-World Application |
| :--- | :--- | :--- |
| **Alpha-Beta (PVS) + NNUE** | **Industry Standard** | Tactical search, deep calculation, and endgame checkmates (Stockfish approach). |
| **MCTS + Deep Neural Net** | **Top Tier** | Probabilistic position rollouts (AlphaZero / Leela Chess Zero). Requires GPU compute & policy network; plain random MCTS is weak in chess. |
| **Proof-Number Search** | **Specialized** | Solving forced-mate problems and endgame studies. |
| **Constraint Satisfaction (CSP)**| **Puzzle Generation Only** | Solving composition puzzles (N-Queens, Knight's Tour, retro-analysis). Not suited for dynamic 2-player game search. |
| **Local Search (SPSA, GA, Texel)**| **Parameter Tuning** | Tuning piece-square tables, mobility weights, and search heuristics via self-play. |
| **Opening Books & Tablebases** | **Instant Lookup** | Grandmaster theory in 0ms; mathematically solved endgames (Syzygy). |

---

## Search Enhancements Build Order (By Payoff)

1. **Alpha-Beta + Negamax (Core Search)**: Clean single-value framework from the side-to-move's perspective.
2. **Move Ordering (Huge Payoff)**:
   - Transposition Table (TT) best move first.
   - Good captures: **MVV-LVA** (*Most Valuable Victim - Least Valuable Attacker*) or **SEE** (*Static Exchange Evaluation*).
   - Killer moves: High-cutoff quiet (non-capture) moves.
   - History heuristic: Tracks quiet moves causing beta-cutoffs across different positions.
3. **Iterative Deepening**:
   - Time management: Depth 1, 2, 3... until time budget expires.
   - Feeds the best move from depth $N$ to be searched first at depth $N+1$.
4. **Transposition Table (Zobrist Hashing)**:
   - 64-bit Zobrist keys capturing pieces, side to move, castling rights, and en passant target.
   - Stores: Zobrist key, search depth, best move, score bound type (`EXACT`, `LOWERBOUND`, `UPPERBOUND`).
   - *Pitfall check*: Adjust mate scores relative to current search ply before storing/retrieving.
5. **Quiescence Search**:
   - Resolves the *horizon effect* by continuing capture moves (and checks/promotions) until the position is tactically quiet.
6. **Null-Move Pruning**:
   - Skip side's turn; if evaluation remains $\ge \beta$, prune the subtree.
   - *Safety guard*: Disabled in check and in zugzwang-prone endgames (e.g., King & pawn endgames).
7. **Late Move Reductions (LMR)**:
   - Search late, quiet candidate moves at reduced depth; re-search at full depth only if they beat $\alpha$.
8. **Principal Variation Search (PVS) & Aspiration Windows**:
   - Search PV move with full window $[\alpha, \beta]$; search remaining moves with zero/null window $[\alpha, \alpha+1]$.
9. **Extensions & Selective Pruning**:
   - Check extensions (extend depth by 1 ply when in check).
   - Futility pruning and reverse futility (static null-move pruning) near leaf nodes.
10. **Repetition, 50-Move Rule, & Mate Distance Scoring**:
    - Avoid threefold repetition or 50-move draws when winning; prefer faster checkmates over distant mates.

---

## Open Resources Available from the Internet

### 1. Visual Sprites & Assets
- **Lichess Vector Piece Sets**: Public domain SVG pieces created by Colin M.L. Burnett (*Cburnett*), widely regarded as the gold standard for clean chess boards.
- **Wikimedia Commons**: Free high-res PNG/SVG piece vectors in various styles (Merida, Alpha, Staunton).

### 2. Opening Books
- **Polyglot Books (`.bin`)**: Open formats like `gm2001.bin`, `Performance.bin`, or `fruit.bin`. Small file size (~1–10 MB), fast binary lookups.
- **Lichess Open API**: Live opening explorer API providing grandmaster move statistics and win percentages.

### 3. Endgame Tablebases
- **Syzygy Tablebases (3, 4, 5, 6-piece)**: Complete game-theoretic evaluations (Win/Loss/Draw + Distance to Zeroing) for all endgames up to 6 pieces.
- **Lichess Tablebase API**: Cloud endpoint for instant tablebase lookups without downloading hundreds of gigabytes locally.

### 4. Neural Network Weights (NNUE)
- **Stockfish NNUE Networks**: Pretrained `.nnue` evaluation weights trained on billions of positions. Available under GPL via the official Stockfish evaluation repository.
- **Compact NNUE architectures**: 768 $\rightarrow$ 256 halfkp networks that run fast on CPU.

### 5. Testing & Verification Harnesses
- **CuteChess / Fastchess**: Standard CLI tools to run automated engine-vs-engine matches with SPRT (Sequential Probability Ratio Test) to verify whether changes actually gain Elo.
- **Test Suites**:
  - **WAC** (*Win at Chess*): 300 tactical test positions.
  - **STS** (*Strategic Test Suite*): Evaluates positional understanding.
  - **Perft Test Suite**: Verifies move generation correctness down to the exact node count.

---

## Development Milestones

### Phase 1: Core Foundation & GUI (Completed)
- [x] Board with rank (1–8) and file (a–h) coordinate markings.
- [x] Collision-aware movement for all 6 piece types.
- [x] Full check, checkmate, and stalemate enforcement.
- [x] Castling, en passant, and pawn promotion rules.
- [x] Player vs Computer mode with Minimax AI.
- [x] Visual alerts for checks, checkmates, and last move highlights.
- [x] Smooth piece slide animations and natural thinking pacing.
- [x] Scalable window, Fullscreen support (F11), Undo (`U`/`Ctrl+Z`), and Redo (`Y`/`Ctrl+Y`).

### Phase 2: Search Optimization (Next Up)
- [ ] Implement Negamax formulation.
- [ ] Implement MVV-LVA move ordering with quiet killer moves.
- [ ] Implement Quiescence search with tactical stand-pat evaluation.
- [ ] Implement 64-bit Zobrist Hashing and Transposition Table (with ply-adjusted mate scores).
- [ ] Implement Iterative Deepening with time manager.

### Phase 3: Engine Intelligence & Resources
- [ ] Polyglot opening book integration.
- [ ] Advanced evaluation: pawn structure, king safety, open files.
- [ ] Null-move pruning and Late Move Reductions (LMR).
- [ ] Difficulty selector (Easy / Medium / Hard).
- [ ] Side panel with captured pieces and move history logger.
