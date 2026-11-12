"""
Application entry point supporting scalable resizable window, fullscreen toggle, Undo, and Redo.
"""
import sys
import pygame
from gui.game import Game


def main():
    """Initialize scalable Pygame display, run event loop, and manage Player vs AI game turns."""
    pygame.init()
    width = 980
    height = 700

    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("Chess Bot - Player vs Computer")
    clock = pygame.time.Clock()

    game = Game(win_width=width, win_height=height)
    running = True

    # AI thinking pacing timer
    ai_thinking_start = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # Handle window scaling / resizing
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                game.on_resize(event.w, event.h)
            elif event.type == pygame.KEYDOWN:
                # F11 toggles Fullscreen mode
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                    info = pygame.display.Info()
                    game.on_resize(info.current_w, info.current_h)
                # Press 'R' to restart match
                elif event.key == pygame.K_r:
                    game.reset_game()
                    ai_thinking_start = None
                # Press 'U' or 'Ctrl+Z' to undo move
                elif event.key == pygame.K_u or (event.key == pygame.K_z and (event.mod & pygame.KMOD_CTRL)):
                    game.undo_turn()
                    ai_thinking_start = None
                # Press 'Y' or 'Ctrl+Y' to redo move
                elif event.key == pygame.K_y or (event.key == pygame.K_y and (event.mod & pygame.KMOD_CTRL)):
                    game.redo_turn()
                    ai_thinking_start = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_click(event.pos)

        # Progress any active piece slide animation
        game.update_animation()

        # Dynamic window caption matching game warnings
        if game.warning_text:
            pygame.display.set_caption(f"Chess Bot - {game.warning_text}")
        else:
            pygame.display.set_caption(f"Chess Bot - {game.game_status_text}")

        # Render current frame
        game.draw(screen)
        pygame.display.update()

        # Handle computer AI turn with a natural thinking delay and smooth animation
        if game.turn == game.ai_color and not game.game_over and game.active_animation is None:
            if ai_thinking_start is None:
                ai_thinking_start = pygame.time.get_ticks()

            # Natural 450ms thinking delay so the player can observe the board state
            if pygame.time.get_ticks() - ai_thinking_start >= 450:
                game.make_ai_move()
                ai_thinking_start = None
        else:
            ai_thinking_start = None

        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
