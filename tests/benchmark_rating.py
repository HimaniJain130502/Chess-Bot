"""
Rating benchmark tool for Chess-Bot.
Runs a calibrated suite of tactical and positional positions to estimate
the bot's approximate Elo rating.
"""

import os
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
        "weight_elo": 900,
    },
    {
        "id": 2,
        "name": "Scholar's Mate in 1",
        "fen": "r1bqkb1r/pppp1ppp/2n5/4p3/2B1n3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 0 4",
        "expected": [((5, 5), (1, 5))],
        "weight_elo": 1000,
    },
    {
        "id": 3,
        "name": "Hanging Knight Capture",
        "fen": "r1bqk1nr/pppp1ppp/2n5/8/4n3/2N5/PPPP1PPP/R1BQKB1R w KQkq - 0 1",
        "expected": [((5, 2), (4, 4))],
        "weight_elo": 1050,
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
        "name": "Royal Knight Fork",
        "fen": "r3k3/8/8/3N4/8/8/8/4K3 w - - 0 1",
        "expected": [((3, 3), (1, 2))],
        "weight_elo": 1200,
    },
    {
        "id": 6,
        "name": "Passed Pawn Advancement",
        "fen": "4k3/8/3P4/8/8/8/8/4K3 w - - 0 1",
        "expected": [((2, 3), (1, 3))],
        "weight_elo": 1300,
    },
    {
        "id": 7,
        "name": "Defend Checkmate Threat",
        "fen": "r1bqkb1r/pppp1ppp/2n5/4p3/2B5/5Q2/PPPP1PPP/RNB1K1NR b KQkq - 0 4",
        "expected": [((0, 3), (2, 5)), ((0, 3), (1, 4)), ((1, 3), (3, 3)), ((0, 6), (2, 7))],
        "weight_elo": 1350,
    },
    {
        "id": 8,
        "name": "Rook Skewer Check",
        "fen": "4q3/4k3/8/8/8/8/8/R5K1 w - - 0 1",
        "expected": [((7, 0), (7, 4))],
        "weight_elo": 1400,
    },
    {
        "id": 9,
        "name": "Long-Range Queen Mate",
        "fen": "6k1/5ppp/8/8/8/8/1Q6/4K3 w - - 0 1",
        "expected": [((6, 1), (0, 1))],
        "weight_elo": 1450,
    },
    {
        "id": 10,
        "name": "Endgame King Centralization",
        "fen": "8/8/8/4k3/8/8/4K3/8 w - - 0 1",
        "expected": [((6, 4), (5, 4)), ((6, 4), (5, 3))],
        "weight_elo": 1500,
    },
]


def estimate_rating():
    """Run benchmark suite and compute estimated Elo performance."""
    game = Game()
    solved = 0
    total = len(BENCHMARK_SUITE)
    total_time = 0.0

    print("Running Chess-Bot Rating Benchmark...")
    print(f"Total benchmark positions: {total}\n")

    for item in BENCHMARK_SUITE:
        load_fen(game, item["fen"])
        t0 = time.time()
        best_move = find_best_move(game, depth=3, time_limit_ms=800)
        elapsed = time.time() - t0
        total_time += elapsed

        if best_move is None:
            passed = False
            move_coords = None
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
    # Baseline estimation: 800 (base) + 800 * solve_pct
    approx_elo = int(800 + solve_pct * 800)

    if approx_elo < 1000:
        tier = "Novice / Casual"
    elif approx_elo < 1200:
        tier = "Beginner Club Player"
    elif approx_elo < 1450:
        tier = "Intermediate Club Player"
    elif approx_elo < 1650:
        tier = "Advanced Club Player"
    else:
        tier = "Expert Candidate"

    avg_time = total_time / total if total > 0 else 0.0

    print("\nBenchmark Results Summary")
    print(f"Solved: {solved}/{total} ({solve_pct * 100:.1f}%)")
    print(f"Average Search Time: {avg_time:.3f}s per move")
    print(f"Estimated Bot Rating: ~{approx_elo} Elo (+-75)")
    print(f"Player Strength Tier: {tier}")


if __name__ == "__main__":
    estimate_rating()
