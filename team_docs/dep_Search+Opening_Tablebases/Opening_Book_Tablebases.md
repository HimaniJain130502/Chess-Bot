# Task: Opening Book & Endgame Tablebases
**Assigned To:** Member D  
**Topic:** Polyglot opening books, Lichess API integration, Syzygy tablebases  
**Dependencies:**
- **Requires:** `Search_Engine_Optimization.md` (Member B) — specifically the stable `find_best_move()` function and the Zobrist hashing infrastructure (`compute_zobrist()`) in `Minimax_Alpha_Beta_Logic.py`. The opening book lookup uses the **same Zobrist key** as the TT to identify positions.
- You can build and test the book reader independently using a standalone script. Only wire it into the game once Member B confirms the search is stable.

---

## Context

The current engine searches from move 1. That is expensive and unnecessary — the first 10–15 moves of most games are well-known grandmaster theory. An **opening book** provides instant, human-expert moves for the opening phase with zero compute cost.

For endgames with 6 or fewer pieces, **Syzygy tablebases** contain perfect play computed offline. Rather than searching, we can simply look up the optimal move.

---

## Tasks (in recommended order)

### D-1 · Polyglot Opening Book Reader

**What is Polyglot?** A standard binary format (`.bin`) where each 16-byte record stores:
- 8 bytes: Zobrist key (position hash)
- 2 bytes: move in Polyglot encoding
- 2 bytes: weight (how often this move was played)
- 4 bytes: learning data (ignore)

**Where to get a book:**
```
gm2001.bin  — from CCRL / various open chess websites
Performance.bin
fruit.bin
```
Recommended download link: https://www.chessprogramming.org/Polyglot

**Implementation:**

Create a new file: `OpeningBook.py`

```python
# OpeningBook.py
import struct, os, random

ENTRY_SIZE = 16

class PolyglotBook:
    """Binary Polyglot opening book reader."""

    def __init__(self, path: str):
        """Load and index a Polyglot .bin opening book file."""
        self.entries = []
        if not os.path.exists(path):
            return
        with open(path, "rb") as f:
            data = f.read()
        for i in range(0, len(data), ENTRY_SIZE):
            entry = data[i:i + ENTRY_SIZE]
            if len(entry) < ENTRY_SIZE:
                break
            key, move, weight, _ = struct.unpack(">QHHI", entry)
            self.entries.append((key, move, weight))

    def lookup(self, zobrist_key: int):
        """Return a list of (polyglot_move, weight) for the given position hash."""
        return [(m, w) for k, m, w in self.entries if k == zobrist_key]

    def pick_move(self, zobrist_key: int, weighted=True):
        """Pick a book move by weight (or uniformly at random if weighted=False)."""
        candidates = self.lookup(zobrist_key)
        if not candidates:
            return None
        if weighted:
            total = sum(w for _, w in candidates)
            r = random.randint(0, total - 1)
            cumulative = 0
            for move_int, w in sorted(candidates, key=lambda x: -x[1]):
                cumulative += w
                if r < cumulative:
                    return move_int
        return random.choice(candidates)[0]
```

---

### D-2 · Polyglot Move Decoder

Polyglot encodes moves as a 16-bit integer:
```
bits 0-5:   destination column (a=0 … h=7) ← note: Polyglot uses file first
bits 6-11:  destination row    (1=0 … 8=7)
bits 12-17: origin column
bits 18-23: origin row
bits 12-14: promotion piece (0=none, 1=knight, 2=bishop, 3=rook, 4=queen)
```

```python
def decode_polyglot_move(move_int: int):
    """Decode a 16-bit Polyglot move integer into (from_row, from_col, to_row, to_col, promo)."""
    to_col   = (move_int >> 0)  & 0b111
    to_row   = (move_int >> 3)  & 0b111
    from_col = (move_int >> 6)  & 0b111
    from_row = (move_int >> 9)  & 0b111
    promo    = (move_int >> 12) & 0b111

    # Polyglot uses rank 0=rank1, our grid uses row 0=rank8
    from_grid_row = 7 - from_row
    to_grid_row   = 7 - to_row
    return from_grid_row, from_col, to_grid_row, to_col, promo
```

---

### D-3 · Wire Opening Book into Game Flow

In `Game.make_ai_move()` (in `Game.py`), **check the book first**:

```python
# At the top of Game.make_ai_move():
from OpeningBook import PolyglotBook, decode_polyglot_move
from Minimax_Alpha_Beta_Logic import compute_zobrist

BOOK = PolyglotBook("assets/books/gm2001.bin")

def make_ai_move(self):
    """Calculate and initiate animated AI move: book first, then Negamax."""
    if self.game_over or self.turn != self.ai_color or self.active_animation is not None:
        return

    # 1. Try opening book
    z_key    = compute_zobrist(self)
    book_int = BOOK.pick_move(z_key)
    if book_int is not None:
        fr, fc, tr, tc, _ = decode_polyglot_move(book_int)
        piece = self.grid[fr][fc]
        if piece is not None and piece.color == self.ai_color:
            # Verify it is actually legal
            from Game_logic import get_legal_moves
            if (tr, tc) in get_legal_moves(self, piece):
                self.game_status_text = "Computer plays (Book)"
                self.start_move(piece, tr, tc)
                return

    # 2. Fall back to Negamax search
    best_move = find_best_move(self, depth=3, time_limit_ms=800)
    if best_move is not None:
        piece, (target_row, target_col) = best_move
        self.start_move(piece, target_row, target_col)
```

Place the book file at: `assets/books/gm2001.bin`

---

### D-4 · HUD "Book Move" Indicator

When the AI plays a book move, show a small badge:
```
📖 Book  ← shown in the HUD status text
```

Already handled by: `self.game_status_text = "Computer plays (Book)"` above.  
Member A can style this badge further in their HUD work.

---

### D-5 · Lichess Opening Explorer API (live statistics)

The Lichess API provides real-time opening statistics for any position, including:
- Top moves played and their win rates
- Number of games in the database
- Average ELO of players who reached this position

```python
import urllib.request, json

def query_lichess_opening(fen: str, variant="standard") -> dict:
    """Query Lichess Opening Explorer API for move statistics at a given FEN position."""
    url = f"https://explorer.lichess.ovh/lichess?fen={urllib.parse.quote(fen)}&variant={variant}"
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            return json.loads(resp.read())
    except Exception:
        return {}
```

> You will need to generate FEN strings from the board state. Consider adding a `board_to_fen(game)` function to `Moves.py`.  
> This feature requires internet access — disable gracefully when offline.

---

### D-6 · Lichess Tablebase API (perfect endgame play)

When 6 or fewer pieces remain, query the cloud Lichess Tablebase for the perfect move (WDL + DTZ):

```python
def query_tablebase(fen: str):
    """Query Lichess Tablebase API for perfect play when ≤ 6 pieces remain."""
    url = f"https://tablebase.lichess.ovh/standard?fen={urllib.parse.quote(fen)}"
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            data = json.loads(resp.read())
            # data["moves"] is sorted: best move is data["moves"][0]["uci"]
            if data.get("moves"):
                best_uci = data["moves"][0]["uci"]  # e.g. "e1e2"
                return best_uci  # Parse UCI into (from_sq, to_sq)
    except Exception:
        return None
```

Wire this into `make_ai_move()`: if `len(game.pieces) <= 6`, call the tablebase instead of search.

---

### D-7 · Local Syzygy Tablebases (if time permits)

Downloading and locally probing Syzygy `.rtbw` / `.rtbz` files avoids network latency and works offline.  
Library: `python-chess` has built-in Syzygy probing via `chess.syzygy`.

> This task requires downloading several GB of tablebase files. Only pursue it if time and disk space permit.

---

## Completion Criteria

- [ ] `OpeningBook.py` loads a Polyglot `.bin` book and returns legal moves for starting positions
- [ ] AI plays book moves for the first several moves without calling Negamax
- [ ] HUD shows "Book Move" indicator when a book move is played
- [ ] Fallback to Negamax search works correctly when position is not in the book
- [ ] Lichess Tablebase API queried when ≤ 6 pieces; correct move played
- [ ] Application never crashes when internet is unavailable (graceful fallback)

> **Note:** Tasks D-1 through D-4 are the core deliverables. D-5 and D-6 (Lichess API) are valuable additions — implement them if D-1 through D-4 are stable. D-7 (local Syzygy) is a stretch goal requiring significant storage and is optional.
