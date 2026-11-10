"""
Board representation and visual rendering with responsive scaling and coordinate labels.
"""
import pygame


class Board:
    """Manages 8x8 chessboard geometry, colors, responsive scaling, and visual rendering."""

    def __init__(self, sq_size=80, x_offset=0, y_offset=60):
        """Initialize board dimensions, square colors, coordinate font, and spatial offsets."""
        self.rows = 8
        self.cols = 8
        self.sq_size = sq_size
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.width = self.cols * self.sq_size
        self.height = self.rows * self.sq_size

        # Classic tournament board colors (warm cream and walnut brown)
        self.light_square = (240, 217, 181)
        self.dark_square = (181, 136, 99)

        # Coordinate label colors contrasting with squares
        self.light_coord_color = (181, 136, 99)
        self.dark_coord_color = (240, 217, 181)

        self.update_fonts()

    def update_fonts(self):
        """Update coordinate font size dynamically based on current square size."""
        font_size = max(11, int(self.sq_size * 0.18))
        self.coord_font = pygame.font.SysFont("Arial", font_size, bold=True)

    def set_geometry(self, sq_size, x_offset, y_offset):
        """Recalculate board pixel dimensions and offset positions on window resize."""
        self.sq_size = sq_size
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.width = self.cols * self.sq_size
        self.height = self.rows * self.sq_size
        self.update_fonts()

    def draw_squares(self, screen):
        """Draw alternating light and dark squares across the 8x8 board."""
        for row in range(self.rows):
            for col in range(self.cols):
                color = self.light_square if (row + col) % 2 == 0 else self.dark_square
                rect = (
                    self.x_offset + col * self.sq_size,
                    self.y_offset + row * self.sq_size,
                    self.sq_size,
                    self.sq_size
                )
                pygame.draw.rect(screen, color, rect)

    def draw_coordinates(self, screen):
        """Draw file letters (a-h) and rank numbers (1-8) along the board margins."""
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

        for row in range(self.rows):
            for col in range(self.cols):
                is_light = (row + col) % 2 == 0
                font_color = self.light_coord_color if is_light else self.dark_coord_color

                # Rank numbers (8 to 1) on column 0
                if col == 0:
                    rank_text = str(8 - row)
                    label = self.coord_font.render(rank_text, True, font_color)
                    screen.blit(
                        label,
                        (self.x_offset + col * self.sq_size + 4, self.y_offset + row * self.sq_size + 4)
                    )

                # File letters (a to h) on row 7
                if row == 7:
                    file_text = files[col]
                    label = self.coord_font.render(file_text, True, font_color)
                    screen.blit(
                        label,
                        (
                            self.x_offset + (col + 1) * self.sq_size - label.get_width() - 4,
                            self.y_offset + (row + 1) * self.sq_size - label.get_height() - 4
                        )
                    )

    def draw(self, screen):
        """Render complete chessboard with squares and coordinates."""
        self.draw_squares(screen)
        self.draw_coordinates(screen)
