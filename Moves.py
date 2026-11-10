"""
Move representation and algebraic notation utilities.
"""

# Map column indices (0-7) to file letters ('a'-'h')
FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
FILES_MAP = {f: i for i, f in enumerate(FILES)}


def square_to_algebraic(row, col):
    """Convert (row, col) coordinates to standard algebraic square notation (e.g., (7, 4) -> 'e1')."""
    file_letter = FILES[col]
    rank_number = 8 - row
    return f"{file_letter}{rank_number}"


def algebraic_to_square(coord):
    """Convert algebraic notation (e.g., 'e4') into (row, col) coordinates."""
    file_letter = coord[0].lower()
    rank_number = int(coord[1])
    col = FILES_MAP[file_letter]
    row = 8 - rank_number
    return row, col


def format_move(piece, start_row, start_col, end_row, end_col, is_capture=False):
    """Format a chess move into human-readable algebraic-style string."""
    piece_symbols = {
        "Pawn": "",
        "Knight": "N",
        "Bishop": "B",
        "Rook": "R",
        "Queen": "Q",
        "King": "K"
    }
    symbol = piece_symbols.get(piece.__class__.__name__, "")
    dest = square_to_algebraic(end_row, end_col)

    if piece.__class__.__name__ == "Pawn" and is_capture:
        start_file = FILES[start_col]
        return f"{start_file}x{dest}"

    capture_mark = "x" if is_capture else ""
    return f"{symbol}{capture_mark}{dest}"
