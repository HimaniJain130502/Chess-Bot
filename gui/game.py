"""
Game controller managing board state, Player vs Computer turns, animations,
Lichess-style dark theme UI, move history side panel, undo, and redo logic.
"""
import pygame
from gui.board import Board
from core.pieces import Pawn, Rook, Knight, Bishop, Queen, King
from core.game_logic import get_legal_moves, is_in_check, is_checkmate, is_stalemate, find_king
from core.moves import format_move
from engine.search import find_best_move
from engine.opening_book import PolyglotBook
from engine.evaluation import PIECE_VALUES

PIECE_SYMBOLS = {
    ("white", "King"): "♔",
    ("white", "Queen"): "♕",
    ("white", "Rook"): "♖",
    ("white", "Bishop"): "♗",
    ("white", "Knight"): "♘",
    ("white", "Pawn"): "♙",
    ("black", "King"): "♚",
    ("black", "Queen"): "♛",
    ("black", "Rook"): "♜",
    ("black", "Bishop"): "♝",
    ("black", "Knight"): "♞",
    ("black", "Pawn"): "♟",
}

THEME = {
    "bg": (22, 21, 18),
    "panel_bg": (38, 36, 33),
    "panel_card": (30, 28, 24),
    "panel_border": (54, 52, 49),
    "text_main": (240, 240, 240),
    "text_dim": (160, 155, 145),
    "text_muted": (120, 115, 105),
    "move_row_even": (38, 36, 33),
    "move_row_odd": (32, 30, 27),
    "move_active": (54, 60, 72),
    "btn_bg": (48, 45, 41),
    "btn_hover": (64, 60, 54),
    "btn_border": (72, 68, 62),
    "accent_green": (98, 153, 36),
    "accent_red": (204, 51, 51),
    "highlight_last": (205, 210, 106, 160),
    "highlight_selected": (247, 236, 116, 180),
}


class Game:
    """Coordinates chess rules, active pieces, user input, AI turns, and Lichess-style GUI."""

    def __init__(self, win_width=980, win_height=700):
        """Initialize board, player colors, piece layout, fonts, undo/redo stacks, and responsive sizing."""
        self.win_width = win_width
        self.win_height = win_height

        self.player_color = "white"
        self.ai_color = "black"

        self.turn = "white"
        self.selected_piece = None
        self.valid_moves = []
        self.pieces = []
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.en_passant_target = None
        self.move_history = []
        self.move_stack = []
        self.redo_stack = []
        self.last_move = None
        self.game_over = False
        self.game_status_text = "Your Turn (White)"
        self.warning_text = ""

        self.active_animation = None
        self.move_scroll_offset = 0

        self.board = Board()
        self.recalculate_layout()
        self.update_fonts()
        self.setup_pieces()
        self.opening_book = PolyglotBook()

    def recalculate_layout(self):
        """Compute responsive layout placing board on left and Lichess panel on right."""
        # Desired side panel width (between 260px and 340px)
        self.panel_width = max(260, min(330, int(self.win_width * 0.32)))
        self.panel_x = self.win_width - self.panel_width - 16
        self.panel_y = 16
        self.panel_height = self.win_height - 32

        # Space available for board on left
        board_area_w = self.panel_x - 24
        board_area_h = self.win_height - 84
        available_size = max(280, min(board_area_w, board_area_h))
        self.sq_size = max(36, available_size // 8)

        board_px = self.sq_size * 8
        self.x_offset = max(16, (board_area_w - board_px) // 2 + 12)
        self.y_offset = (self.win_height - board_px) // 2

        self.top_bar_y = max(8, self.y_offset - 36)
        self.bot_bar_y = min(self.win_height - 36, self.y_offset + board_px + 8)

        self.board.set_geometry(self.sq_size, self.x_offset, self.y_offset)
        self.update_button_positions()

    def update_button_positions(self):
        """Position action buttons at bottom of Lichess side panel."""
        btn_y = self.panel_y + self.panel_height - 48
        btn_h = 36
        pad = 8
        avail_w = self.panel_width - 24
        btn_w = (avail_w - pad * 2) // 3

        bx = self.panel_x + 12
        self.undo_btn_rect = pygame.Rect(bx, btn_y, btn_w, btn_h)
        self.redo_btn_rect = pygame.Rect(bx + btn_w + pad, btn_y, btn_w, btn_h)
        self.restart_btn_rect = pygame.Rect(bx + (btn_w + pad) * 2, btn_y, btn_w, btn_h)

    def update_fonts(self):
        """Update piece and HUD font sizes dynamically based on screen scale."""
        font_path = pygame.font.match_font("segoeuisymbol")
        piece_size = max(22, int(self.sq_size * 0.70))
        if font_path:
            self.piece_font = pygame.font.Font(font_path, piece_size)
            self.mini_piece_font = pygame.font.Font(font_path, 16)
        else:
            self.piece_font = pygame.font.SysFont("Arial", piece_size)
            self.mini_piece_font = pygame.font.SysFont("Arial", 16)

        self.title_font = pygame.font.SysFont("Segoe UI", 16, bold=True)
        self.hud_font = pygame.font.SysFont("Segoe UI", 14, bold=True)
        self.move_font = pygame.font.SysFont("Segoe UI", 14)
        self.move_num_font = pygame.font.SysFont("Segoe UI", 13)
        self.btn_font = pygame.font.SysFont("Segoe UI", 13, bold=True)
        self.badge_font = pygame.font.SysFont("Segoe UI", 12, bold=True)
        self.modal_font = pygame.font.SysFont("Segoe UI", max(18, int(self.sq_size * 0.32)), bold=True)
        self.sub_font = pygame.font.SysFont("Segoe UI", max(12, int(self.sq_size * 0.19)))

    def on_resize(self, new_width, new_height):
        """Recalculate layout geometry, scale board, and reposition controls on window resize."""
        self.win_width = max(600, new_width)
        self.win_height = max(480, new_height)
        self.recalculate_layout()
        self.update_fonts()

    def reset_game(self):
        """Reset board, pieces, move history, and turn states for a fresh match."""
        self.turn = "white"
        self.selected_piece = None
        self.valid_moves = []
        self.pieces = []
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.en_passant_target = None
        self.move_history = []
        self.move_stack = []
        self.redo_stack = []
        self.last_move = None
        self.active_animation = None
        self.game_over = False
        self.game_status_text = "Your Turn (White)"
        self.warning_text = ""
        self.move_scroll_offset = 0
        self.setup_pieces()

    def setup_pieces(self):
        """Populate initial 32 chess pieces on the board grid."""
        back_rank = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        for col, piece_cls in enumerate(back_rank):
            piece = piece_cls("black", 0, col)
            self.pieces.append(piece)
            self.grid[0][col] = piece

        for col in range(8):
            pawn = Pawn("black", 1, col)
            self.pieces.append(pawn)
            self.grid[1][col] = pawn

        for col in range(8):
            pawn = Pawn("white", 6, col)
            self.pieces.append(pawn)
            self.grid[6][col] = pawn

        for col, piece_cls in enumerate(back_rank):
            piece = piece_cls("white", 7, col)
            self.pieces.append(piece)
            self.grid[7][col] = piece

    def get_symbol(self, piece):
        """Retrieve Unicode character representing specified piece."""
        return PIECE_SYMBOLS.get((piece.color, piece.__class__.__name__), "?")

    def handle_click(self, mouse_pos):
        """Process mouse clicks across interactive buttons, board squares, and pieces."""
        if self.active_animation is not None:
            return

        if self.undo_btn_rect.collidepoint(mouse_pos):
            self.undo_turn()
            return

        if self.redo_btn_rect.collidepoint(mouse_pos):
            self.redo_turn()
            return

        if self.restart_btn_rect.collidepoint(mouse_pos):
            self.reset_game()
            return

        if self.game_over:
            return

        if self.turn != self.player_color:
            return

        x, y = mouse_pos
        col = (x - self.x_offset) // self.sq_size
        row = (y - self.y_offset) // self.sq_size

        if not (0 <= row < 8 and 0 <= col < 8):
            return

        clicked_piece = self.grid[row][col]

        if clicked_piece is not None and clicked_piece.color == self.turn:
            self.selected_piece = clicked_piece
            self.valid_moves = get_legal_moves(self, clicked_piece)
            return

        if self.selected_piece is not None:
            if (row, col) in self.valid_moves:
                self.redo_stack.clear()
                self.start_move(self.selected_piece, row, col)
            self.selected_piece = None
            self.valid_moves = []

    def start_move(self, piece, target_row, target_col):
        """Initialize smooth easing slide animation from start square to target square."""
        start_x = self.x_offset + piece.col * self.sq_size + self.sq_size // 2
        start_y = self.y_offset + piece.row * self.sq_size + self.sq_size // 2
        end_x = self.x_offset + target_col * self.sq_size + self.sq_size // 2
        end_y = self.y_offset + target_row * self.sq_size + self.sq_size // 2

        self.active_animation = {
            "piece": piece,
            "target_row": target_row,
            "target_col": target_col,
            "start_pos": (start_x, start_y),
            "end_pos": (end_x, end_y),
            "start_time": pygame.time.get_ticks(),
            "duration": 200
        }

    def update_animation(self):
        """Update active move animation and finalize move upon completion."""
        if self.active_animation is None:
            return

        now = pygame.time.get_ticks()
        elapsed = now - self.active_animation["start_time"]
        t = min(1.0, elapsed / self.active_animation["duration"])

        eased_t = 1.0 - (1.0 - t) ** 3
        sx, sy = self.active_animation["start_pos"]
        ex, ey = self.active_animation["end_pos"]
        cur_x = sx + (ex - sx) * eased_t
        cur_y = sy + (ey - sy) * eased_t
        self.active_animation["current_pos"] = (cur_x, cur_y)

        if t >= 1.0:
            piece = self.active_animation["piece"]
            tr = self.active_animation["target_row"]
            tc = self.active_animation["target_col"]
            self.active_animation = None
            self.execute_move(piece, tr, tc)

    def execute_move(self, piece, target_row, target_col):
        """Finalize piece move, push undo record, evaluate check/checkmate, and switch turn."""
        orig_row, orig_col = piece.row, piece.col
        target_piece = self.grid[target_row][target_col]
        is_capture = target_piece is not None
        orig_first_move = piece.first_move
        prev_en_passant = self.en_passant_target

        # En passant capture
        ep_captured = None
        if piece.__class__.__name__ == "Pawn" and (target_row, target_col) == self.en_passant_target:
            ep_captured = self.grid[orig_row][target_col]
            if ep_captured is not None and ep_captured in self.pieces:
                self.pieces.remove(ep_captured)
                self.grid[orig_row][target_col] = None
                is_capture = True

        # Standard capture
        if target_piece is not None and target_piece in self.pieces:
            self.pieces.remove(target_piece)

        # Move piece on board grid
        self.grid[orig_row][orig_col] = None
        self.grid[target_row][target_col] = piece
        piece.move(target_row, target_col)
        piece.first_move = False

        # Castling: reposition rook
        castled_rook_info = None
        if piece.__class__.__name__ == "King" and abs(target_col - orig_col) == 2:
            if target_col == 6:
                rook = self.grid[orig_row][7]
                if rook is not None:
                    self.grid[orig_row][7] = None
                    self.grid[orig_row][5] = rook
                    rook.move(orig_row, 5)
                    rook.first_move = False
                    castled_rook_info = (rook, orig_row, 7, 5)
            elif target_col == 2:
                rook = self.grid[orig_row][0]
                if rook is not None:
                    self.grid[orig_row][0] = None
                    self.grid[orig_row][3] = rook
                    rook.move(orig_row, 3)
                    rook.first_move = False
                    castled_rook_info = (rook, orig_row, 0, 3)

        # Update en passant target
        if piece.__class__.__name__ == "Pawn" and abs(target_row - orig_row) == 2:
            self.en_passant_target = ((orig_row + target_row) // 2, orig_col)
        else:
            self.en_passant_target = None

        # Pawn promotion
        promoted_queen = None
        promotion_rank = 0 if piece.color == "white" else 7
        if piece.__class__.__name__ == "Pawn" and target_row == promotion_rank:
            promoted_queen = Queen(piece.color, target_row, target_col)
            promoted_queen.first_move = False
            self.pieces.remove(piece)
            self.pieces.append(promoted_queen)
            self.grid[target_row][target_col] = promoted_queen

        self.last_move = ((orig_row, orig_col), (target_row, target_col))

        move_str = format_move(piece, orig_row, orig_col, target_row, target_col, is_capture=is_capture)
        self.move_history.append(move_str)

        # Push state snapshot to undo stack
        self.move_stack.append({
            "piece": piece,
            "orig_pos": (orig_row, orig_col),
            "target_pos": (target_row, target_col),
            "captured": target_piece,
            "ep_captured": (ep_captured, orig_row, target_col) if ep_captured else None,
            "castled_rook": castled_rook_info,
            "promoted_queen": promoted_queen,
            "first_move": orig_first_move,
            "en_passant_target": prev_en_passant,
            "last_move": self.last_move,
            "move_str": move_str
        })

        next_turn = "black" if self.turn == "white" else "white"
        self.turn = next_turn

        # Update check / checkmate status
        if is_checkmate(self, self.turn):
            self.game_over = True
            winner = "You" if self.turn == self.ai_color else "Computer"
            self.game_status_text = f"Checkmate! {winner} Won!"
            self.warning_text = f"CHECKMATE! {winner} won!"
        elif is_stalemate(self, self.turn):
            self.game_over = True
            self.game_status_text = "Stalemate! Draw."
            self.warning_text = "STALEMATE! Game ended in a draw."
        elif is_in_check(self.grid, self.pieces, self.turn):
            if self.turn == self.player_color:
                self.warning_text = "CHECK! Your King is in check!"
                self.game_status_text = "You are in Check!"
            else:
                self.warning_text = "CHECK! Computer is in check!"
                self.game_status_text = "Computer is in Check!"
        else:
            self.warning_text = ""
            if self.turn == self.player_color:
                self.game_status_text = "Your Turn (White)"
            else:
                self.game_status_text = "Computer is thinking..."

    def undo_single_move(self):
        """Revert the most recent move from undo stack and store it on redo stack."""
        if not self.move_stack:
            return False

        record = self.move_stack.pop()
        piece = record["piece"]
        orig_row, orig_col = record["orig_pos"]
        tr, tc = record["target_pos"]
        captured = record["captured"]

        self.redo_stack.append({
            "piece": piece,
            "orig_pos": (orig_row, orig_col),
            "target_pos": (tr, tc),
        })

        if record["promoted_queen"] is not None:
            self.pieces.remove(record["promoted_queen"])
            self.pieces.append(piece)

        self.grid[tr][tc] = None
        self.grid[orig_row][orig_col] = piece
        piece.row, piece.col = orig_row, orig_col
        piece.first_move = record["first_move"]

        if captured is not None:
            self.pieces.append(captured)
            self.grid[tr][tc] = captured

        if record["ep_captured"] is not None:
            ep_piece, ep_r, ep_c = record["ep_captured"]
            self.pieces.append(ep_piece)
            self.grid[ep_r][ep_c] = ep_piece

        if record["castled_rook"] is not None:
            rook, r_row, r_orig_c, r_moved_c = record["castled_rook"]
            self.grid[r_row][r_moved_c] = None
            self.grid[r_row][r_orig_c] = rook
            rook.col = r_orig_c
            rook.first_move = True

        self.en_passant_target = record["en_passant_target"]

        if self.move_history:
            self.move_history.pop()

        self.turn = piece.color
        self.game_over = False
        self.game_status_text = "Your Turn (White)" if self.turn == "white" else "Computer Thinking..."
        self.warning_text = ""
        return True

    def undo_turn(self):
        """Revert moves back to the player's previous turn in Player vs Computer mode."""
        if self.active_animation is not None or not self.move_stack:
            return

        if self.turn == self.player_color:
            self.undo_single_move()
            self.undo_single_move()
        else:
            self.undo_single_move()

        if self.move_stack:
            prev_top = self.move_stack[-1]
            self.last_move = (prev_top["orig_pos"], prev_top["target_pos"])
        else:
            self.last_move = None

    def redo_single_move(self):
        """Re-execute the most recently undone move from redo stack."""
        if not self.redo_stack:
            return False

        redo_record = self.redo_stack.pop()
        piece = redo_record["piece"]
        tr, tc = redo_record["target_pos"]
        self.execute_move(piece, tr, tc)
        return True

    def redo_turn(self):
        """Redo moves forward to the player's next state in Player vs Computer mode."""
        if self.active_animation is not None or not self.redo_stack:
            return

        if len(self.redo_stack) >= 2:
            self.redo_single_move()
            self.redo_single_move()
        else:
            self.redo_single_move()

    def make_ai_move(self):
        """Calculate and initiate animated AI move using search engine."""
        if self.game_over or self.turn != self.ai_color or self.active_animation is not None:
            return

        # Prefer a legal move from the bundled Polyglot opening book.
        # If the position is not covered, retain the original search unchanged.
        book_move = self.opening_book.get_move(self)
        if book_move is not None:
            piece, (target_row, target_col) = book_move
            self.game_status_text = "Computer plays (Book)"
            self.start_move(piece, target_row, target_col)
            return

        best_move = find_best_move(self, depth=3, time_limit_ms=800)
        if best_move is not None:
            piece, (target_row, target_col) = best_move
            self.start_move(piece, target_row, target_col)
        else:
            if is_in_check(self.grid, self.pieces, self.ai_color):
                self.game_over = True
                self.game_status_text = "Checkmate! You win!"
            else:
                self.game_over = True
                self.game_status_text = "Stalemate! Draw."

    def get_material_advantage(self):
        """Calculate captured pieces and net material difference for both players."""
        w_mat = sum(PIECE_VALUES.get(p.__class__.__name__, 0) for p in self.pieces if p.color == "white" and p.__class__.__name__ != "King")
        b_mat = sum(PIECE_VALUES.get(p.__class__.__name__, 0) for p in self.pieces if p.color == "black" and p.__class__.__name__ != "King")

        # Captured pieces: starting counts minus remaining
        starting = {"Pawn": 8, "Knight": 2, "Bishop": 2, "Rook": 2, "Queen": 1}
        w_captured = []  # Black pieces taken by White
        b_captured = []  # White pieces taken by Black

        for p_name, count in starting.items():
            curr_w = sum(1 for p in self.pieces if p.color == "white" and p.__class__.__name__ == p_name)
            curr_b = sum(1 for p in self.pieces if p.color == "black" and p.__class__.__name__ == p_name)
            b_captured.extend([p_name] * max(0, count - curr_w))
            w_captured.extend([p_name] * max(0, count - curr_b))

        diff = (w_mat - b_mat) // 100
        return w_captured, b_captured, diff

    def draw_player_bars(self, screen):
        """Draw Lichess-style player cards above and below the board."""
        w_captured, b_captured, diff = self.get_material_advantage()

        # Top Bar: AI Bot
        bot_rect = pygame.Rect(self.x_offset, self.top_bar_y, self.sq_size * 8, 30)
        bot_label = self.hud_font.render("🤖 AI Bot", True, THEME["text_main"])
        screen.blit(bot_label, (self.x_offset, self.top_bar_y + 4))

        # Rating badge
        badge_surf = self.badge_font.render("1400", True, THEME["text_dim"])
        badge_rect = pygame.Rect(self.x_offset + bot_label.get_width() + 8, self.top_bar_y + 5, 40, 18)
        pygame.draw.rect(screen, (45, 42, 38), badge_rect, border_radius=4)
        screen.blit(badge_surf, badge_surf.get_rect(center=badge_rect.center))

        # Black's captured pieces (white pieces taken)
        bx = self.x_offset + bot_label.get_width() + 60
        for p_name in b_captured:
            sym = PIECE_SYMBOLS.get(("white", p_name), "")
            sym_surf = self.mini_piece_font.render(sym, True, (220, 220, 220))
            screen.blit(sym_surf, (bx, self.top_bar_y + 2))
            bx += 14

        if diff < 0:
            diff_surf = self.badge_font.render(f"+{abs(diff)}", True, THEME["text_dim"])
            screen.blit(diff_surf, (bx + 4, self.top_bar_y + 6))

        # Bottom Bar: Human Player
        user_label = self.hud_font.render("👤 You (White)", True, THEME["text_main"])
        screen.blit(user_label, (self.x_offset, self.bot_bar_y + 6))

        # White's captured pieces (black pieces taken)
        wx = self.x_offset + user_label.get_width() + 16
        for p_name in w_captured:
            sym = PIECE_SYMBOLS.get(("black", p_name), "")
            sym_surf = self.mini_piece_font.render(sym, True, (160, 160, 160))
            screen.blit(sym_surf, (wx, self.bot_bar_y + 4))
            wx += 14

        if diff > 0:
            diff_surf = self.badge_font.render(f"+{diff}", True, THEME["text_dim"])
            screen.blit(diff_surf, (wx + 4, self.bot_bar_y + 8))

    def draw_lichess_panel(self, screen):
        """Render Lichess-style dark side panel with header, move table, and action buttons."""
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pygame.draw.rect(screen, THEME["panel_bg"], panel_rect, border_radius=10)
        pygame.draw.rect(screen, THEME["panel_border"], panel_rect, width=1, border_radius=10)

        # Header card
        header_h = 56
        header_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, header_h)
        pygame.draw.rect(screen, THEME["panel_card"], header_rect, border_top_left_radius=10, border_top_right_radius=10)
        pygame.draw.line(screen, THEME["panel_border"], (self.panel_x, self.panel_y + header_h), (self.panel_x + self.panel_width, self.panel_y + header_h), 1)

        title = self.title_font.render("Chess Bot · vs AI", True, THEME["text_main"])
        screen.blit(title, (self.panel_x + 14, self.panel_y + 10))

        # Status subtitle
        status_color = (130, 205, 75) if self.turn == self.player_color else (100, 175, 240)
        if self.game_over:
            status_color = (235, 180, 50)
        elif self.warning_text:
            status_color = (235, 75, 75)

        status_text = self.badge_font.render(self.game_status_text, True, status_color)
        screen.blit(status_text, (self.panel_x + 14, self.panel_y + 32))

        # Move list table headers
        table_y = self.panel_y + header_h + 8
        col_num_w = 42
        col_move_w = (self.panel_width - col_num_w - 24) // 2

        num_lbl = self.move_num_font.render("#", True, THEME["text_muted"])
        w_lbl = self.move_num_font.render("White", True, THEME["text_muted"])
        b_lbl = self.move_num_font.render("Black", True, THEME["text_muted"])

        screen.blit(num_lbl, (self.panel_x + 14, table_y))
        screen.blit(w_lbl, (self.panel_x + 14 + col_num_w, table_y))
        screen.blit(b_lbl, (self.panel_x + 14 + col_num_w + col_move_w, table_y))

        # Table rows
        row_y = table_y + 22
        row_h = 24
        max_visible_rows = (self.panel_height - header_h - 100) // row_h

        # Group moves into pairs (turns)
        moves = self.move_history
        turns = []
        for i in range(0, len(moves), 2):
            w_move = moves[i]
            b_move = moves[i + 1] if (i + 1) < len(moves) else ""
            turns.append((i // 2 + 1, w_move, b_move))

        # Auto-scroll so newest moves stay visible
        if len(turns) > max_visible_rows:
            visible_turns = turns[-max_visible_rows:]
        else:
            visible_turns = turns

        active_move_idx = len(moves) - 1

        for turn_num, w_m, b_m in visible_turns:
            is_odd = (turn_num % 2 == 1)
            row_rect = pygame.Rect(self.panel_x + 8, row_y, self.panel_width - 16, row_h)
            row_bg = THEME["move_row_odd"] if is_odd else THEME["move_row_even"]
            pygame.draw.rect(screen, row_bg, row_rect, border_radius=4)

            # Turn number
            num_surf = self.move_num_font.render(f"{turn_num}.", True, THEME["text_muted"])
            screen.blit(num_surf, (self.panel_x + 14, row_y + 3))

            # White move box
            w_rect = pygame.Rect(self.panel_x + 14 + col_num_w - 4, row_y + 1, col_move_w - 4, row_h - 2)
            is_w_active = ((turn_num - 1) * 2 == active_move_idx)
            if is_w_active:
                pygame.draw.rect(screen, THEME["move_active"], w_rect, border_radius=3)
            w_text = self.move_font.render(w_m, True, THEME["text_main"] if is_w_active else (210, 210, 210))
            screen.blit(w_text, (self.panel_x + 14 + col_num_w, row_y + 2))

            # Black move box
            if b_m:
                b_rect = pygame.Rect(self.panel_x + 14 + col_num_w + col_move_w - 4, row_y + 1, col_move_w - 4, row_h - 2)
                is_b_active = ((turn_num - 1) * 2 + 1 == active_move_idx)
                if is_b_active:
                    pygame.draw.rect(screen, THEME["move_active"], b_rect, border_radius=3)
                b_text = self.move_font.render(b_m, True, THEME["text_main"] if is_b_active else (210, 210, 210))
                screen.blit(b_text, (self.panel_x + 14 + col_num_w + col_move_w, row_y + 2))

            row_y += row_h

        # Action Buttons (Undo, Redo, Restart)
        mouse_pos = pygame.mouse.get_pos()

        # Undo button
        can_undo = len(self.move_stack) > 0 and not self.game_over
        u_hover = self.undo_btn_rect.collidepoint(mouse_pos) and can_undo
        u_bg = THEME["btn_hover"] if u_hover else THEME["btn_bg"]
        u_fg = THEME["text_main"] if can_undo else THEME["text_muted"]
        pygame.draw.rect(screen, u_bg, self.undo_btn_rect, border_radius=6)
        pygame.draw.rect(screen, THEME["btn_border"], self.undo_btn_rect, width=1, border_radius=6)
        u_label = self.btn_font.render("↶ Undo", True, u_fg)
        screen.blit(u_label, u_label.get_rect(center=self.undo_btn_rect.center))

        # Redo button
        can_redo = len(self.redo_stack) > 0 and not self.game_over
        r_hover = self.redo_btn_rect.collidepoint(mouse_pos) and can_redo
        r_bg = THEME["btn_hover"] if r_hover else THEME["btn_bg"]
        r_fg = THEME["text_main"] if can_redo else THEME["text_muted"]
        pygame.draw.rect(screen, r_bg, self.redo_btn_rect, border_radius=6)
        pygame.draw.rect(screen, THEME["btn_border"], self.redo_btn_rect, width=1, border_radius=6)
        r_label = self.btn_font.render("↷ Redo", True, r_fg)
        screen.blit(r_label, r_label.get_rect(center=self.redo_btn_rect.center))

        # Restart button
        rst_hover = self.restart_btn_rect.collidepoint(mouse_pos)
        rst_bg = THEME["btn_hover"] if rst_hover else THEME["btn_bg"]
        pygame.draw.rect(screen, rst_bg, self.restart_btn_rect, border_radius=6)
        pygame.draw.rect(screen, THEME["btn_border"], self.restart_btn_rect, width=1, border_radius=6)
        rst_label = self.btn_font.render("↻ New", True, THEME["text_main"])
        screen.blit(rst_label, rst_label.get_rect(center=self.restart_btn_rect.center))

    def draw_highlights(self, screen):
        """Highlight last move in Lichess olive, checked king in red, selected square, and legal moves."""
        # 1. Last move highlight (Lichess signature olive)
        if self.last_move is not None:
            (from_r, from_c), (to_r, to_c) = self.last_move
            for r, c in [(from_r, from_c), (to_r, to_c)]:
                highlight_surf = pygame.Surface((self.sq_size, self.sq_size), pygame.SRCALPHA)
                highlight_surf.fill(THEME["highlight_last"])
                screen.blit(highlight_surf, (self.x_offset + c * self.sq_size, self.y_offset + r * self.sq_size))

        # 2. King in check highlight
        if is_in_check(self.grid, self.pieces, self.turn):
            king = find_king(self.pieces, self.turn)
            if king is not None:
                kx = self.x_offset + king.col * self.sq_size
                ky = self.y_offset + king.row * self.sq_size
                king_surf = pygame.Surface((self.sq_size, self.sq_size), pygame.SRCALPHA)
                king_surf.fill((215, 45, 45, 140))
                screen.blit(king_surf, (kx, ky))
                pygame.draw.rect(screen, (235, 30, 30), (kx, ky, self.sq_size, self.sq_size), 3)

        # 3. Selected piece square highlight
        if self.selected_piece is not None:
            px = self.x_offset + self.selected_piece.col * self.sq_size
            py = self.y_offset + self.selected_piece.row * self.sq_size
            sel_surf = pygame.Surface((self.sq_size, self.sq_size), pygame.SRCALPHA)
            sel_surf.fill(THEME["highlight_selected"])
            screen.blit(sel_surf, (px, py))

        # 4. Legal destination square markers
        for r, c in self.valid_moves:
            target_piece = self.grid[r][c]
            is_ep = (self.selected_piece is not None and
                     self.selected_piece.__class__.__name__ == "Pawn" and
                     (r, c) == self.en_passant_target)

            marker_surface = pygame.Surface((self.sq_size, self.sq_size), pygame.SRCALPHA)
            if target_piece is None and not is_ep:
                # Quiet move: small subtle dark circle
                pygame.draw.circle(
                    marker_surface,
                    (20, 20, 20, 85),
                    (self.sq_size // 2, self.sq_size // 2),
                    max(4, self.sq_size // 6)
                )
            else:
                # Capture move: hollow ring around the square perimeter
                pygame.draw.circle(
                    marker_surface,
                    (20, 20, 20, 110),
                    (self.sq_size // 2, self.sq_size // 2),
                    max(8, self.sq_size // 2 - 4),
                    width=max(3, self.sq_size // 14)
                )
            screen.blit(marker_surface, (self.x_offset + c * self.sq_size, self.y_offset + r * self.sq_size))

    def draw_piece(self, screen, piece, pos=None):
        """Render high-contrast piece symbol centered with outline."""
        symbol = self.get_symbol(piece)
        if pos is not None:
            center_x, center_y = pos
        else:
            center_x = self.x_offset + piece.col * self.sq_size + self.sq_size // 2
            center_y = self.y_offset + piece.row * self.sq_size + self.sq_size // 2

        if piece.color == "white":
            fill_color = (255, 255, 255)
            outline_color = (40, 40, 40)
        else:
            fill_color = (28, 28, 28)
            outline_color = (225, 225, 225)

        # Smooth outline for crisp contrast on light and dark squares
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            outline_surf = self.piece_font.render(symbol, True, outline_color)
            outline_rect = outline_surf.get_rect(center=(center_x + dx, center_y + dy))
            screen.blit(outline_surf, outline_rect)

        # Center glyph
        text_surf = self.piece_font.render(symbol, True, fill_color)
        text_rect = text_surf.get_rect(center=(center_x, center_y))
        screen.blit(text_surf, text_rect)

    def draw_game_over_modal(self, screen):
        """Render centered game-over victory/stalemate card."""
        overlay = pygame.Surface((self.win_width, self.win_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        screen.blit(overlay, (0, 0))

        center_y = self.win_height // 2
        center_x = (self.x_offset + self.sq_size * 4)

        card_w = min(400, self.win_width - 40)
        card_h = 160
        card_rect = pygame.Rect(center_x - card_w // 2, center_y - card_h // 2, card_w, card_h)
        pygame.draw.rect(screen, (34, 32, 28), card_rect, border_radius=12)
        pygame.draw.rect(screen, (190, 150, 45), card_rect, width=2, border_radius=12)

        title_surf = self.modal_font.render(self.game_status_text, True, (255, 225, 100))
        screen.blit(title_surf, title_surf.get_rect(center=(center_x, center_y - 24)))

        sub_surf = self.sub_font.render("Click 'New' or Press 'R' to Restart", True, (210, 205, 195))
        screen.blit(sub_surf, sub_surf.get_rect(center=(center_x, center_y + 24)))

    def draw(self, screen):
        """Render background, player bars, chessboard, highlights, pieces, and Lichess panel."""
        screen.fill(THEME["bg"])

        self.draw_player_bars(screen)
        self.board.draw(screen)
        self.draw_highlights(screen)

        anim_piece = self.active_animation["piece"] if self.active_animation else None
        for piece in self.pieces:
            if piece is not anim_piece:
                self.draw_piece(screen, piece)

        if self.active_animation is not None:
            cur_pos = self.active_animation.get("current_pos", self.active_animation["start_pos"])
            self.draw_piece(screen, anim_piece, pos=cur_pos)

        self.draw_lichess_panel(screen)

        if self.game_over:
            self.draw_game_over_modal(screen)
