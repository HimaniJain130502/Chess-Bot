# Task: GUI, UX & Assets
**Assigned To:** Member A  
**Topic:** Visual polish, interactive controls, piece sprites, sound  
**Dependencies:** None — this task is fully independent. You can begin immediately alongside any other team member.

---

## Context

The game currently renders chess pieces as Unicode glyphs (e.g. ♔ ♛) using the Segoe UI Symbol font. The board is functional and responsive, but lacks visual polish, sound, a move history panel, and player choice for pawn promotion. Your job is to elevate the experience.

All your changes go into these files:
- `Game.py` → HUD drawing, side panel, promotion dialog
- `Board.py` → Board theme support
- `Main.py` → Difficulty selector, side-switching
- New file: `Assets.py` → Sprite loading, sound synthesis

---

## Tasks (in recommended order)

### A-1 · Piece Sprite Loader (`Assets.py`)

Replace Unicode glyphs with high-resolution PNG sprites from the **Lichess Cburnett set** (public domain).

**How to get sprites:**
```
https://github.com/lichess-org/lila/tree/master/public/piece/cburnett
```
Download the 12 PNG files (`wK.png`, `wQ.png`, `wR.png`, `wB.png`, `wN.png`, `wP.png` and black equivalents).
Place them in a new folder: `assets/pieces/cburnett/`

**What to implement:**
```python
# assets.py
import pygame, os

PIECE_SPRITES: dict = {}   # filled by load_sprites()

def load_sprites(sq_size: int) -> None:
    """Load and scale all 12 piece PNGs to current square size."""
    piece_map = {
        ("white","King"): "wK", ("white","Queen"): "wQ", ("white","Rook"): "wR",
        ("white","Bishop"): "wB", ("white","Knight"): "wN", ("white","Pawn"): "wP",
        ("black","King"): "bK", ("black","Queen"): "bQ", ("black","Rook"): "bR",
        ("black","Bishop"): "bB", ("black","Knight"): "bN", ("black","Pawn"): "bP",
    }
    for key, name in piece_map.items():
        path = os.path.join("assets", "pieces", "cburnett", f"{name}.png")
        img  = pygame.image.load(path).convert_alpha()
        PIECE_SPRITES[key] = pygame.transform.smoothscale(img, (sq_size, sq_size))
```

Then in `Game.draw_piece()` check `if PIECE_SPRITES` and blit the sprite instead of rendering the Unicode font.

> **Fallback:** If sprites are absent (e.g. on a team member's machine), keep the current Unicode glyph rendering as the fallback so the game never crashes.

---

### A-2 · Side Panel (move history + material + evaluation bar)

Widen the window to `640 + 220 = 860px` and draw a side panel to the right of the board.

**Panel contents:**
1. **Move history** — scrollable list in algebraic notation (`1. e4 e5`, `2. Nf3 Nc6`, …). Pull from `game.move_history`.
2. **Captured pieces** — icons of pieces taken by each side, sorted by value.
3. **Material advantage** — `+3 ♙` or `−2 ♟` badge at top of panel.
4. **Evaluation bar** — a vertical bar scaled from –10 to +10 pawns, shaded white/black based on `evaluate_board(game)` from `Minimax_Alpha_Beta_Logic.py`.

---

### A-3 · Pawn Promotion Dialog

Currently the game auto-promotes to Queen. Add a small popup that appears when a human pawn reaches the 8th rank.

**Flow:**
1. In `Game.execute_move()`, detect promotion *before* creating the Queen.
2. Set a flag `self.awaiting_promotion = (row, col, color)` and pause all input.
3. In `Game.draw()`, render a 4-button card showing Queen / Rook / Bishop / Knight sprites.
4. On player click, create the chosen piece, clear the flag, and resume normal play.

---

### A-4 · Procedural Sound Effects

No external audio files needed — synthesize everything with `numpy` + `pygame.sndarray`.

```python
import numpy as np, pygame

def make_tone(freq=440, duration=0.06, decay=80, volume=0.4) -> pygame.mixer.Sound:
    """Generate a short synthesized tone without loading any audio file."""
    sr  = 44100
    t   = np.linspace(0, duration, int(sr * duration), False)
    wav = np.sin(2 * np.pi * freq * t) * np.exp(-t * decay) * volume
    mono   = (wav * 32767).astype(np.int16)
    stereo = np.column_stack((mono, mono))
    return pygame.sndarray.make_sound(stereo)

SOUNDS = {}
def load_sounds():
    """Pre-generate all game sound effects."""
    SOUNDS["move"]    = make_tone(freq=600,  duration=0.05, decay=90)
    SOUNDS["capture"] = make_tone(freq=320,  duration=0.09, decay=50)
    SOUNDS["check"]   = make_tone(freq=880,  duration=0.14, decay=40)
    SOUNDS["game_over"] = make_tone(freq=200, duration=0.3, decay=15)
```

Play the right sound in `Game.execute_move()` depending on what happened.

---

### A-5 · Difficulty Selector

Add a startup screen (or in-game menu) with three difficulty settings:

| Level | Search Depth | Time Limit |
| :--- | :--- | :--- |
| Easy | 1 | 200 ms |
| Medium | 2 | 500 ms |
| Hard | 3+ | 800 ms |

Pass the chosen `depth` and `time_limit_ms` through to `find_best_move()` in `Game.make_ai_move()`.

---

### A-6 · Play as Black Option

Currently the player always plays White. Allow switching:
- Add a `game.player_color` toggle on the startup screen or via keyboard shortcut.
- When `player_color == "black"`, flip the board display (row 0 at the bottom) and let the AI move first.

---

### A-7 · Board Theme Selector (if time permits)

Add 3 board colour presets selectable from a menu:

| Theme | Light Square | Dark Square |
| :--- | :--- | :--- |
| Classic | `(240, 217, 181)` | `(181, 136, 99)` |
| Dark | `(100, 111, 64)` | `(49, 61, 25)` |
| High-contrast | `(255, 255, 255)` | `(50, 50, 50)` |

Store the choice in `Board` and re-render on the next frame.

---

## Completion Criteria

- [ ] Piece sprites load and render at all window sizes (fallback to Unicode if absent)
- [ ] Side panel shows last 20 moves in scrollable list with material count
- [ ] Pawn promotion dialog appears and respects player choice
- [ ] 4 sound effects play at correct moments
- [ ] Difficulty selector changes AI search depth
- [ ] Game never crashes if `assets/` folder is missing

> **Note:** Not all tasks need to be finished. Complete them in order — A-1 through A-4 deliver the most value. A-5 through A-7 are quality-of-life additions to tackle if time permits after the core tasks are done.

