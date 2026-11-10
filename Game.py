"""
Game controller managing board state, Player vs Computer turns, animations, scalable HUD, undo, and redo logic.
"""
import pygame
from Board import Board
from Pieces import Pawn, Rook, Knight, Bishop, Queen, King
from Game_logic import get_legal_moves, is_in_check, is_checkmate, is_stalemate, find_king
from Moves import format_move
from Minimax_Alpha_Beta_Logic import find_best_move

# Unicode chess piece characters by color and class name
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


class Game:
    """Coordinates chess rules, active pieces, user input, AI turns, scalable GUI, undo, and redo."""

    def __init__(self, win_width=640, win_height=700):
        """Initialize board, player colors, piece layout, fonts, undo/redo stacks, and responsive sizing."""
        self.win_width = win_width
        self.win_height = win_height
        self.hud_height = 60

        # Calculate responsive square size and centering offsets
        available_size = min(self.win_width, self.win_height - self.hud_height)
        self.sq_size = max(40, available_size // 8)
        self.x_offset = (self.win_width - self.sq_size * 8) // 2
        self.y_offset = self.hud_height + (self.win_height - self.hud_height - self.sq_size * 8) // 2

        self.board = Board(sq_size=self.sq_size, x_offset=self.x_offset, y_offset=self.y_offset)

        # Player vs Computer settings
        self.player_color = "white"
        self.ai_color = "black"

        # Game state tracking
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

        # Smooth animation tracking
        self.active_animation = None

        # HUD button rectangles
        self.update_button_positions()

        # Load fonts
        self.update_fonts()
        self.setup_pieces()

    def update_button_positions(self):
        """Update positions of Undo, Redo, and control buttons based on current window width."""
        btn_y = 14
        btn_h = 32
        self.undo_btn_rect = pygame.Rect(self.win_width - 180, btn_y, 76, btn_h)
        self.redo_btn_rect = pygame.Rect(self.win_width - 96, btn_y, 76, btn_h)

    def update_fonts(self):
        """Update piece and HUD font sizes dynamically based on responsive square size."""
        font_path = pygame.font.match_font("segoeuisymbol")
        piece_size = max(24, int(self.sq_size * 0.65))
        if font_path:
            self.piece_font = pygame.font.Font(font_path, piece_size)
        else:
            self.piece_font = pygame.font.SysFont("Arial", piece_size)

        self.hud_font = pygame.font.SysFont("Segoe UI", 15, bold=True)
        self.btn_font = pygame.font.SysFont("Segoe UI", 14, bold=True)
        self.warning_font = pygame.font.SysFont("Segoe UI", 16, bold=True)
        self.modal_font = pygame.font.SysFont("Segoe UI", max(18, int(self.sq_size * 0.32)), bold=True)
        self.sub_font = pygame.font.SysFont("Segoe UI", max(12, int(self.sq_size * 0.19)))

    def on_resize(self, new_width, new_height):
        """Recalculate layout geometry, board scale, button positions, and fonts upon window resize."""
        self.win_width = max(360, new_width)
        self.win_height = max(420, new_height)

        available_size = min(self.win_width, self.win_height - self.hud_height)
        self.sq_size = max(40, available_size // 8)
        self.x_offset = (self.win_width - self.sq_size * 8) // 2
        self.y_offset = self.hud_height + (self.win_height - self.hud_height - self.sq_size * 8) // 2

        self.board.set_geometry(self.sq_size, self.x_offset, self.y_offset)
        self.update_button_positions()
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
        self.setup_pieces()

    def setup_pieces(self):
        """Populate initial 32 chess pieces on the board grid."""
        back_rank = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        # Black pieces (rows 0 and 1)
        for col, piece_cls in enumerate(back_rank):
            piece = piece_cls("black", 0, col)
            self.pieces.append(piece)
            self.grid[0][col] = piece

        for col in range(8):
            pawn = Pawn("black", 1, col)
            self.pieces.append(pawn)
            self.grid[1][col] = pawn

        # White pieces (rows 6 and 7)
        for col in range(8):
            pawn = Pawn("white", 6, col)
            self.pieces.append(pawn)
            self.grid[6][col] = pawn

        for col, piece_cls in enumerate(back_rank):
            piece = piece_cls("white", 7, col)
            self.pieces.append(piece)
            self.grid[7][col] = piece

    def get_symbol(self, piece):
        """Return Unicode symbol corresponding to piece color and type."""
        return PIECE_SYMBOLS.get((piece.color, piece.__class__.__name__), "?")

    def handle_click(self, mouse_pos):
        """Process player mouse click for undo/redo buttons, selecting pieces, or executing moves."""
        if self.active_animation is not None:
            return

        # Check Undo button
        if self.undo_btn_rect.collidepoint(mouse_pos):
            self.undo_turn()
            return

        # Check Redo button
        if self.redo_btn_rect.collidepoint(mouse_pos):
            self.redo_turn()
            return

        if self.game_over:
            return

        # Player can only move during their own turn
        if self.turn != self.player_color:
            return

        x, y = mouse_pos
        col = (x - self.x_offset) // self.sq_size
        row = (y - self.y_offset) // self.sq_size

        if not (0 <= row < 8 and 0 <= col < 8):
            return

        clicked_piece = self.grid[row][col]

        # Case 1: Clicked friendly player piece -> select and calculate legal moves
        if clicked_piece is not None and clicked_piece.color == self.turn:
            self.selected_piece = clicked_piece
            self.valid_moves = get_legal_moves(self, clicked_piece)
            return

        # Case 2: Destination clicked with a piece already selected
        if self.selected_piece is not None:
            if (row, col) in self.valid_moves:
                self.redo_stack.clear()  # Clear redo stack on new player move
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
            "duration": 220
        }

    def update_animation(self):
        """Update active move animation and finalize move upon completion."""
        if self.active_animation is None:
            return

        now = pygame.time.get_ticks()
        elapsed = now - self.active_animation["start_time"]
        t = min(1.0, elapsed / self.active_animation["duration"])

        # Cubic ease-out
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
        prev_status = self.game_status_text
        prev_warning = self.warning_text

        # Special Move 1: En passant capture
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

        # Special Move 2: Castling rook repositioning
        castled_rook_info = None
        if piece.__class__.__name__ == "King" and abs(target_col - orig_col) == 2:
            if target_col == 6:  # Kingside
                rook = self.grid[orig_row][7]
                if rook is not None:
                    self.grid[orig_row][7] = None
                    self.grid[orig_row][5] = rook
                    rook.move(orig_row, 5)
                    rook.first_move = False
                    castled_rook_info = (rook, orig_row, 7)
            elif target_col == 2:  # Queenside
                rook = self.grid[orig_row][0]
                if rook is not None:
                    self.grid[orig_row][0] = None
                    self.grid[orig_row][3] = rook
                    rook.move(orig_row, 3)
                    rook.first_move = False
                    castled_rook_info = (rook, orig_row, 0)

        # Move piece on grid
        self.grid[orig_row][orig_col] = None
        self.grid[target_row][target_col] = piece
        piece.move(target_row, target_col)
        piece.first_move = False

        # Special Move 3: Pawn promotion
        promoted_queen = None
        if piece.__class__.__name__ == "Pawn":
            promotion_rank = 0 if piece.color == "white" else 7
            if target_row == promotion_rank:
                promoted_queen = Queen(piece.color, target_row, target_col)
                promoted_queen.first_move = False
                self.pieces.remove(piece)
                self.pieces.append(promoted_queen)
                self.grid[target_row][target_col] = promoted_queen

        # Update en passant target for next turn
        if piece.__class__.__name__ == "Pawn" and abs(target_row - orig_row) == 2:
            self.en_passant_target = ((orig_row + target_row) // 2, orig_col)
        else:
            self.en_passant_target = None

        # Log move and update last move highlight
        acting_piece = promoted_queen if promoted_queen else piece
        move_str = format_move(acting_piece, orig_row, orig_col, target_row, target_col, is_capture)
        self.move_history.append(move_str)
        self.last_move = ((orig_row, orig_col), (target_row, target_col))

        # Push to undo stack
        self.move_stack.append({
            "piece": piece,
            "orig_pos": (orig_row, orig_col),
            "target_pos": (target_row, target_col),
            "orig_first_move": orig_first_move,
            "captured": target_piece,
            "ep_captured": (ep_captured, orig_row, target_col) if ep_captured else None,
            "castled_rook": castled_rook_info,
            "promoted_queen": promoted_queen,
            "prev_en_passant": prev_en_passant,
            "prev_status": prev_status,
            "prev_warning": prev_warning,
            "prev_last_move": self.last_move,
            "move_str": move_str
        })

        # Switch active player turn
        next_turn = "black" if self.turn == "white" else "white"
        self.turn = next_turn

        # Update check and checkmate status and warnings
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
                self.warning_text = "⚠️ CHECK! Your King is in danger!"
                self.game_status_text = "You are in Check!"
            else:
                self.warning_text = "⚠️ CHECK! Computer King in danger!"
                self.game_status_text = "Computer is in Check!"
        else:
            self.warning_text = ""
            if self.turn == self.player_color:
                self.game_status_text = "Your Turn (White)"
            else:
                self.game_status_text = "Computer is thinking..."

    def move_piece(self, piece, target_row, target_col):
        """Direct execution alias to execute_move for backwards compatibility."""
        self.execute_move(piece, target_row, target_col)

    def undo_single_move(self):
        """Revert the most recent move from undo stack and store it on redo stack."""
        if not self.move_stack:
            return False

        record = self.move_stack.pop()
        piece = record["piece"]
        orig_row, orig_col = record["orig_pos"]
        tr, tc = record["target_pos"]
        captured = record["captured"]

        # Push to redo stack
        self.redo_stack.append({
            "piece": piece,
            "orig_pos": (orig_row, orig_col),
            "target_pos": (tr, tc),
        })

        # Revert promotion if applicable
        if record["promoted_queen"] is not None:
            self.pieces.remove(record["promoted_queen"])
            self.pieces.append(piece)

        # Restore piece position on grid
        self.grid[tr][tc] = None
        self.grid[orig_row][orig_col] = piece
        piece.row, piece.col = orig_row, orig_col
        piece.first_move = record["orig_first_move"]

        # Restore normal captured piece
        if captured is not None:
            self.grid[tr][tc] = captured
            if captured not in self.pieces:
                self.pieces.append(captured)

        # Restore en passant captured piece
        if record["ep_captured"] is not None:
            ep_piece, ep_r, ep_c = record["ep_captured"]
            self.grid[ep_r][ep_c] = ep_piece
            if ep_piece not in self.pieces:
                self.pieces.append(ep_piece)

        # Restore castled rook
        if record["castled_rook"] is not None:
            rook, r_orig_r, r_orig_c = record["castled_rook"]
            self.grid[rook.row][rook.col] = None
            self.grid[r_orig_r][r_orig_c] = rook
            rook.row, rook.col = r_orig_r, r_orig_c
            rook.first_move = True

        # Restore board and game variables
        self.en_passant_target = record["prev_en_passant"]
        self.game_status_text = record["prev_status"]
        self.warning_text = record["prev_warning"]
        self.last_move = record["prev_last_move"]
        self.game_over = False

        if self.move_history:
            self.move_history.pop()

        self.turn = piece.color
        self.selected_piece = None
        self.valid_moves = []
        return True

    def undo_turn(self):
        """Undo moves back to the player's previous turn in Player vs Computer mode."""
        if self.active_animation is not None:
            return

        if not self.move_stack:
            return

        # If it's Player's turn, undo both the Computer's move and the Player's move
        if self.turn == self.player_color and len(self.move_stack) >= 2:
            self.undo_single_move()
            self.undo_single_move()
        else:
            self.undo_single_move()

        # Update last move highlight from the top of the stack
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
        if self.active_animation is not None:
            return

        if not self.redo_stack:
            return

        # Redo Player move then Computer move
        if len(self.redo_stack) >= 2:
            self.redo_single_move()
            self.redo_single_move()
        else:
            self.redo_single_move()

    def make_ai_move(self):
        """Calculate and initiate animated AI move using Minimax."""
        if self.game_over or self.turn != self.ai_color or self.active_animation is not None:
            return

        best_move = find_best_move(self, depth=2)
        if best_move is not None:
            piece, (target_row, target_col) = best_move
            self.start_move(piece, target_row, target_col)
        else:
            if is_in_check(self.grid, self.pieces, self.ai_color):
                self.game_over = True
                self.game_status_text = "Checkmate! You win!"
                self.warning_text = "CHECKMATE! You won!"
            else:
                self.game_over = True
                self.game_status_text = "Stalemate! Draw."
                self.warning_text = "STALEMATE! Draw."

    def draw_hud(self, screen):
        """Draw responsive top header bar with player mode, status, Undo, and Redo buttons."""
        hud_rect = pygame.Rect(0, 0, self.win_width, self.hud_height)
        pygame.draw.rect(screen, (30, 34, 42), hud_rect)
        pygame.draw.line(screen, (55, 62, 75), (0, self.hud_height - 1), (self.win_width, self.hud_height - 1), 2)

        # Left label: Mode and active turn
        mode_text = self.hud_font.render("👤 You vs 🤖 AI", True, (210, 215, 225))
        screen.blit(mode_text, (12, 18))

        # Status text
        status_color = (110, 220, 110) if self.turn == self.player_color else (100, 180, 255)
        status_surf = self.hud_font.render(self.game_status_text, True, status_color)
        screen.blit(status_surf, (155, 18))

        # Interactive Undo Button
        mouse_pos = pygame.mouse.get_pos()
        undo_hover = self.undo_btn_rect.collidepoint(mouse_pos) and len(self.move_stack) > 0
        undo_bg = (60, 72, 90) if undo_hover else (42, 50, 62)
        undo_fg = (240, 245, 255) if len(self.move_stack) > 0 else (120, 130, 145)
        pygame.draw.rect(screen, undo_bg, self.undo_btn_rect, border_radius=6)
        pygame.draw.rect(screen, (90, 110, 135), self.undo_btn_rect, width=1, border_radius=6)
        undo_label = self.btn_font.render("↶ Undo", True, undo_fg)
        screen.blit(undo_label, undo_label.get_rect(center=self.undo_btn_rect.center))

        # Interactive Redo Button
        redo_hover = self.redo_btn_rect.collidepoint(mouse_pos) and len(self.redo_stack) > 0
        redo_bg = (60, 72, 90) if redo_hover else (42, 50, 62)
        redo_fg = (240, 245, 255) if len(self.redo_stack) > 0 else (120, 130, 145)
        pygame.draw.rect(screen, redo_bg, self.redo_btn_rect, border_radius=6)
        pygame.draw.rect(screen, (90, 110, 135), self.redo_btn_rect, width=1, border_radius=6)
        redo_label = self.btn_font.render("↷ Redo", True, redo_fg)
        screen.blit(redo_label, redo_label.get_rect(center=self.redo_btn_rect.center))

        # Warning badge when in check
        if self.warning_text and not self.game_over:
            badge_color = (195, 35, 35) if "CHECK" in self.warning_text else (205, 150, 25)
            badge_surface = self.warning_font.render(self.warning_text, True, (255, 255, 255))
            badge_rect = badge_surface.get_rect(right=self.undo_btn_rect.left - 12, centery=self.hud_height // 2)

            box = badge_rect.inflate(14, 8)
            pygame.draw.rect(screen, badge_color, box, border_radius=6)
            pygame.draw.rect(screen, (255, 220, 100), box, width=2, border_radius=6)
            screen.blit(badge_surface, badge_rect)

    def draw_highlights(self, screen):
        """Highlight last move, checked king alert, selected piece, and valid destinations."""
        # 1. Highlight source and target squares of the last move in soft amber
        if self.last_move is not None:
            (from_r, from_c), (to_r, to_c) = self.last_move
            for r, c in [(from_r, from_c), (to_r, to_c)]:
                highlight_surf = pygame.Surface((self.sq_size, self.sq_size), pygame.SRCALPHA)
                highlight_surf.fill((205, 210, 106, 110))
                screen.blit(highlight_surf, (self.x_offset + c * self.sq_size, self.y_offset + r * self.sq_size))

        # 2. Highlight King in red if currently in check
        if is_in_check(self.grid, self.pieces, self.turn):
            king = find_king(self.pieces, self.turn)
            if king is not None:
                kx = self.x_offset + king.col * self.sq_size
                ky = self.y_offset + king.row * self.sq_size
                king_surface = pygame.Surface((self.sq_size, self.sq_size), pygame.SRCALPHA)
                king_surface.fill((235, 45, 45, 140))
                screen.blit(king_surface, (kx, ky))
                pygame.draw.rect(screen, (255, 30, 30), (kx, ky, self.sq_size, self.sq_size), 4)

        # 3. Highlight currently selected piece square
        if self.selected_piece is not None:
            px = self.x_offset + self.selected_piece.col * self.sq_size
            py = self.y_offset + self.selected_piece.row * self.sq_size
            sel_surface = pygame.Surface((self.sq_size, self.sq_size), pygame.SRCALPHA)
            sel_surface.fill((255, 235, 59, 130))
            screen.blit(sel_surface, (px, py))
            pygame.draw.rect(screen, (245, 200, 30), (px, py, self.sq_size, self.sq_size), 3)

        # 4. Draw markers for all legal destination squares
        for r, c in self.valid_moves:
            target_piece = self.grid[r][c]
            is_ep = (self.selected_piece is not None and
                     self.selected_piece.__class__.__name__ == "Pawn" and
                     (r, c) == self.en_passant_target)

            marker_surface = pygame.Surface((self.sq_size, self.sq_size), pygame.SRCALPHA)
            if target_piece is None and not is_ep:
                # Dot for quiet move
                pygame.draw.circle(
                    marker_surface,
                    (50, 50, 50, 110),
                    (self.sq_size // 2, self.sq_size // 2),
                    max(3, self.sq_size // 6)
                )
            else:
                # Ring for capture destination
                pygame.draw.circle(
                    marker_surface,
                    (215, 45, 45, 175),
                    (self.sq_size // 2, self.sq_size // 2),
                    max(6, self.sq_size // 2 - 4),
                    width=max(2, self.sq_size // 20)
                )
            screen.blit(marker_surface, (self.x_offset + c * self.sq_size, self.y_offset + r * self.sq_size))

    def draw_piece(self, screen, piece, pos=None):
        """Render piece symbol centered at given position or in its grid square."""
        symbol = self.get_symbol(piece)
        if pos is not None:
            center_x, center_y = pos
        else:
            center_x = self.x_offset + piece.col * self.sq_size + self.sq_size // 2
            center_y = self.y_offset + piece.row * self.sq_size + self.sq_size // 2

        if piece.color == "white":
            fill_color = (255, 255, 255)
            outline_color = (30, 30, 30)
        else:
            fill_color = (25, 25, 25)
            outline_color = (220, 220, 220)

        # Outline for high contrast on all squares
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            outline_surface = self.piece_font.render(symbol, True, outline_color)
            outline_rect = outline_surface.get_rect(center=(center_x + dx, center_y + dy))
            screen.blit(outline_surface, outline_rect)

        # Primary glyph
        text_surface = self.piece_font.render(symbol, True, fill_color)
        text_rect = text_surface.get_rect(center=(center_x, center_y))
        screen.blit(text_surface, text_rect)

    def draw_game_over_modal(self, screen):
        """Render centered game-over victory/stalemate card with restart and undo options."""
        overlay = pygame.Surface((self.win_width, self.win_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        center_y = self.win_height // 2
        center_x = self.win_width // 2

        card_w = min(420, self.win_width - 40)
        card_h = 170
        card_rect = pygame.Rect(center_x - card_w // 2, center_y - card_h // 2, card_w, card_h)
        pygame.draw.rect(screen, (32, 36, 45), card_rect, border_radius=12)
        pygame.draw.rect(screen, (225, 185, 55), card_rect, width=3, border_radius=12)

        title_surf = self.modal_font.render(self.game_status_text, True, (255, 220, 90))
        title_rect = title_surf.get_rect(center=(center_x, center_y - 28))
        screen.blit(title_surf, title_rect)

        sub_surf = self.sub_font.render("Press 'R' to Restart  |  'U' to Undo Move", True, (200, 205, 215))
        sub_rect = sub_surf.get_rect(center=(center_x, center_y + 25))
        screen.blit(sub_surf, sub_rect)

    def draw(self, screen):
        """Render responsive HUD, chessboard, highlights, pieces, move animation, and modals."""
        # Fill window background
        screen.fill((22, 25, 31))

        self.draw_hud(screen)
        self.board.draw(screen)
        self.draw_highlights(screen)

        # Draw stationary pieces (excluding the one currently animating)
        anim_piece = self.active_animation["piece"] if self.active_animation else None
        for piece in self.pieces:
            if piece is not anim_piece:
                self.draw_piece(screen, piece)

        # Draw the animating piece at its interpolated coordinates
        if self.active_animation is not None:
            cur_pos = self.active_animation.get("current_pos", self.active_animation["start_pos"])
            self.draw_piece(screen, anim_piece, pos=cur_pos)

        if self.game_over:
            self.draw_game_over_modal(screen)
