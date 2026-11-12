"""
Simple unit tests for Evaluation.py terms.
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import unittest
import pygame
pygame.init()

from gui.game import Game
from core.pieces import Pawn, Knight, Bishop, Rook, Queen, King
from engine.evaluation import (
    evaluate,
    material_score,
    pst_score,
    pawn_structure_score,
    king_safety_score,
    mobility_score,
    rook_placement_score,
    bishop_pair_score,
    compute_phase,
)


class TestEvaluation(unittest.TestCase):

    def setUp(self):
        self.game = Game()

    def test_initial_board_balance(self):
        """In the starting position, both sides must have identical scores."""
        self.assertEqual(material_score(self.game), 0)
        self.assertEqual(pst_score(self.game), 0)
        self.assertEqual(pawn_structure_score(self.game), 0)
        self.assertEqual(king_safety_score(self.game), 0)
        self.assertEqual(mobility_score(self.game), 0)
        self.assertEqual(rook_placement_score(self.game), 0)
        self.assertEqual(bishop_pair_score(self.game), 0)
        self.assertEqual(evaluate(self.game), 0)

    def test_material_score(self):
        """Removing Black's queen gives White a +900 material advantage."""
        # Find Black's Queen and remove it
        bq = next(p for p in self.game.pieces if p.color == "black" and p.__class__.__name__ == "Queen")
        self.game.pieces.remove(bq)
        self.game.grid[bq.row][bq.col] = None
        self.assertEqual(material_score(self.game), 900)

    def test_bishop_pair(self):
        """Removing one of Black's bishops gives White the bishop pair bonus."""
        bb = next(p for p in self.game.pieces if p.color == "black" and p.__class__.__name__ == "Bishop")
        self.game.pieces.remove(bb)
        self.game.grid[bb.row][bb.col] = None
        self.assertEqual(bishop_pair_score(self.game), 35)

    def test_doubled_pawn_penalty(self):
        """Placing two White pawns on the same file blocked by an enemy pawn applies doubled pawn penalty."""
        self.game.pieces = []
        self.game.grid = [[None for _ in range(8)] for _ in range(8)]

        p1 = Pawn("white", 4, 3)
        p2 = Pawn("white", 5, 3)
        bp = Pawn("black", 1, 3)
        self.game.pieces.extend([p1, p2, bp])
        self.game.grid[4][3] = p1
        self.game.grid[5][3] = p2
        self.game.grid[1][3] = bp

        score = pawn_structure_score(self.game)
        self.assertLess(score, 0)

    def test_mobility_score(self):
        """A centralized knight has more legal moves than a cornered knight."""
        self.game.pieces = []
        self.game.grid = [[None for _ in range(8)] for _ in range(8)]

        wn = Knight("white", 4, 4)
        bn = Knight("black", 0, 0)
        self.game.pieces.extend([wn, bn])
        self.game.grid[4][4] = wn
        self.game.grid[0][0] = bn

        # White knight in center has 8 moves, black knight in corner has 2
        score = mobility_score(self.game)
        self.assertGreater(score, 0)

    def test_endgame_king_centralization(self):
        """In endgame (phase 0), a centralized king scores higher than a cornered king."""
        self.game.pieces = []
        self.game.grid = [[None for _ in range(8)] for _ in range(8)]

        wk_center = King("white", 4, 4)
        bk_corner = King("black", 0, 0)
        self.game.pieces.extend([wk_center, bk_corner])
        self.game.grid[4][4] = wk_center
        self.game.grid[0][0] = bk_corner

        score = evaluate(self.game)
        self.assertGreater(score, 0)


if __name__ == "__main__":
    unittest.main()
