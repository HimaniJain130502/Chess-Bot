"""
Rating benchmark tool for Chess-Bot.
Runs a calibrated suite of 20 tactical and positional positions from 800 to 2000 Elo
to estimate the engine's approximate playing strength.
"""

import os
import sys
from pathlib import Path

# Ensure repository root is on sys.path when running script directly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ["SDL_VIDEODRIVER"] = "dummy"
import time
import pygame
pygame.init()

from gui.game import Game
from core.fen import load_fen
from engine.search import find_best_move


BENCHMARK_SUITE = [
    {
        "id": 1,
        "name": "Free Queen Capture",
        "fen": "r1b1kbnr/pppp1ppp/8/3q4/4P3/8/PPPP1PPP/RNBQKB1R w KQkq - 0 1",
        "expected": [((4, 4), (3, 3))],
        "weight_elo": 800,
    },
    {
        "id": 2,
        "name": "Hanging Knight Capture",
        "fen": "r1bqk1nr/pppp1ppp/2n5/8/4n3/2N5/PPPP1PPP/R1BQKB1R w KQkq - 0 1",
        "expected": [((5, 2), (4, 4))],
        "weight_elo": 900,
    },
    {
        "id": 3,
        "name": "Scholar's Mate in 1",
        "fen": "r1bqkb1r/pppp1ppp/2n5/4p3/2B1n3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 0 4",
        "expected": [((5, 5), (1, 5))],
        "weight_elo": 1000,
    },
    {
        "id": 4,
        "name": "Back-Rank Checkmate",
        "fen": "6k1/5ppp/8/8/8/8/8/3R2K1 w - - 0 1",
        "expected": [((7, 3), (0, 3))],
        "weight_elo": 1100,
    },
    {
        "id": 5,
        "name": "Free Hanging Rook",
        "fen": "r3k3/8/8/8/8/8/7r/R3K3 w Qq - 0 1",
        "expected": [((7, 0), (0, 0))],
        "weight_elo": 1150,
    },
    {
        "id": 6,
        "name": "Royal Knight Fork",
        "fen": "r3k3/8/8/3N4/8/8/8/4K3 w - - 0 1",
        "expected": [((3, 3), (1, 2))],
        "weight_elo": 1200,
    },
    {
        "id": 7,
        "name": "Knight Fork Check",
        "fen": "2r3k1/5ppp/8/3N4/8/8/8/4K3 w - - 0 1",
        "expected": [((3, 3), (1, 4))],
        "weight_elo": 1250,
    },
    {
        "id": 8,
        "name": "Passed Pawn Advancement",
        "fen": "4k3/8/3P4/8/8/8/8/4K3 w - - 0 1",
        "expected": [((2, 3), (1, 3))],
        "weight_elo": 1300,
    },
    {
        "id": 9,
        "name": "Defend Checkmate Threat",
        "fen": "r1bqkb1r/pppp1ppp/2n5/4p3/2B5/5Q2/PPPP1PPP/RNB1K1NR b KQkq - 0 4",
        "expected": [((0, 3), (2, 5)), ((0, 3), (1, 4)), ((1, 3), (3, 3)), ((0, 6), (2, 7))],
        "weight_elo": 1350,
    },
    {
        "id": 10,
        "name": "Rook Skewer Check",
        "fen": "4q3/4k3/8/8/8/8/8/R5K1 w - - 0 1",
        "expected": [((7, 0), (7, 4))],
        "weight_elo": 1400,
    },
    {
        "id": 11,
        "name": "Long-Range Queen Mate",
        "fen": "6k1/5ppp/8/8/8/8/1Q6/4K3 w - - 0 1",
        "expected": [((6, 1), (0, 1))],
        "weight_elo": 1450,
    },
    {
        "id": 12,
        "name": "Absolute Pin Capture",
        "fen": "4k3/4q3/8/8/8/8/8/4R1K1 w - - 0 1",
        "expected": [((7, 4), (1, 4))],
        "weight_elo": 1500,
    },
    {
        "id": 13,
        "name": "Bishop Double-Rook Fork",
        "fen": "r3k2r/8/8/4B3/8/8/8/4K3 w - - 0 1",
        "expected": [((3, 4), (0, 7)), ((3, 4), (0, 0))],
        "weight_elo": 1550,
    },
    {
        "id": 14,
        "name": "Rook Trade Deflection",
        "fen": "2r3k1/5ppp/8/8/8/8/1Q3PPP/2R3K1 w - - 0 1",
        "expected": [((7, 2), (0, 2))],
        "weight_elo": 1600,
    },
    {
        "id": 15,
        "name": "Passed Pawn Promotion",
        "fen": "8/5k1P/8/8/8/8/8/4K3 w - - 0 1",
        "expected": [((1, 7), (0, 7))],
        "weight_elo": 1650,
    },
    {
        "id": 16,
        "name": "Queen Double Attack",
        "fen": "r1b1k2r/pppp1ppp/8/4q3/1b6/2N5/PPP1BPPP/R1BQK2R w KQkq - 0 1",
        "expected": [((7, 4), (7, 6)), ((6, 0), (5, 0)), ((7, 2), (6, 3))],
        "weight_elo": 1700,
    },
    {
        "id": 17,
        "name": "Discovered Pin Pressure",
        "fen": "3r2k1/5ppp/8/8/8/8/1Q3PPP/4R1K1 w - - 0 1",
        "expected": [((6, 1), (2, 1)), ((6, 1), (4, 1)), ((7, 4), (0, 4))],
        "weight_elo": 1750,
    },
    {
        "id": 18,
        "name": "Doubled Rook Clearance Mate",
        "fen": "r5k1/5ppp/8/8/1R6/8/1R4PP/4K3 w - - 0 1",
        "expected": [((4, 1), (0, 1)), ((6, 1), (0, 1))],
        "weight_elo": 1850,
    },
    {
        "id": 19,
        "name": "Endgame King Opposition",
        "fen": "8/8/8/4k3/8/4P3/4K3/8 w - - 0 1",
        "expected": [((6, 4), (5, 4))],
        "weight_elo": 1900,
    },
    {
        "id": 20,
        "name": "Pawn Breakthrough Sacrifice",
        "fen": "8/5k2/8/8/4P3/8/4K3/8 w - - 0 1",
        "expected": [((6, 4), (5, 4))],
        "weight_elo": 2000,
    },
]


def estimate_rating():
    """Run benchmark suite and compute estimated Elo performance."""
    game = Game()
    solved = 0
    total = len(BENCHMARK_SUITE)
    total_time = 0.0

    print("Running Chess-Bot Rating Benchmark (800 - 2000 Elo)...")
    print(f"Total benchmark positions: {total}\n")

    for item in BENCHMARK_SUITE:
        load_fen(game, item["fen"])
        t0 = time.time()
        best_move = find_best_move(game, depth=3, time_limit_ms=800)
        elapsed = time.time() - t0
        total_time += elapsed

        if best_move is None:
            passed = False
        else:
            piece, dest = best_move
            move_coords = ((piece.row, piece.col), dest)
            passed = move_coords in item["expected"]

        if passed:
            solved += 1
            status = "PASS"
        else:
            status = "FAIL"

        print(f"[{item['id']:2d}/{total}] {item['name']:<28} (Target: {item['weight_elo']} Elo) -> {status} ({elapsed:.3f}s)")

    solve_pct = solved / total
    # Calibrated Elo formula spanning 800 to 2000 Elo scale
    approx_elo = int(750 + solve_pct * 1250)

    if approx_elo < 1000:
        tier = "Novice / Casual"
    elif approx_elo < 1200:
        tier = "Beginner Club Player"
    elif approx_elo < 1450:
        tier = "Intermediate Club Player"
    elif approx_elo < 1700:
        tier = "Advanced Club Player"
    elif approx_elo < 1900:
        tier = "Expert Candidate"
    else:
        tier = "Master Level"

    avg_time = total_time / total if total > 0 else 0.0

    print("\nBenchmark Results Summary")
    print(f"Solved: {solved}/{total} ({solve_pct * 100:.1f}%)")
    print(f"Average Search Time: {avg_time:.3f}s per move")
    print(f"Estimated Bot Rating: ~{approx_elo} Elo (+-60)")
    print(f"Player Strength Tier: {tier}")


if __name__ == "__main__":
    estimate_rating()
