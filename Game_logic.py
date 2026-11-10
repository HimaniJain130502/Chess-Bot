"""
Game state evaluation, legal move validation, and check/checkmate detection.
"""


def is_in_bounds(row, col):
    """Check if given coordinates lie within standard 8x8 boundaries."""
    return 0 <= row < 8 and 0 <= col < 8


def get_piece_at(grid, row, col):
    """Retrieve piece object at target grid position, or None if square is empty."""
    if is_in_bounds(row, col):
        return grid[row][col]
    return None


def find_king(pieces, color):
    """Locate and return King piece of specified color from active pieces."""
    for piece in pieces:
        if piece is not None and piece.__class__.__name__ == "King" and piece.color == color:
            return piece
    return None


def is_square_attacked(grid, pieces, target_row, target_col, attacking_color):
    """Determine whether target square is attacked by any opposing piece."""
    for piece in pieces:
        if piece is not None and piece.color == attacking_color:
            attack_squares = piece.get_attack_squares(grid)
            if (target_row, target_col) in attack_squares:
                return True
    return False


def is_in_check(grid, pieces, color):
    """Verify if King of specified color is currently placed in check."""
    king = find_king(pieces, color)
    if king is None:
        return False
    opponent_color = "black" if color == "white" else "white"
    return is_square_attacked(grid, pieces, king.row, king.col, opponent_color)


def get_castling_moves(game, king):
    """Calculate valid kingside and queenside castling moves for king."""
    castling_moves = []
    if not king.first_move:
        return castling_moves

    opponent = "black" if king.color == "white" else "white"
    # King cannot castle out of check
    if is_square_attacked(game.grid, game.pieces, king.row, king.col, opponent):
        return castling_moves

    row = king.row

    # Kingside castling (col 4 -> col 6, rook at col 7)
    rook_ks = game.grid[row][7]
    if rook_ks is not None and rook_ks.__class__.__name__ == "Rook" and rook_ks.first_move:
        if game.grid[row][5] is None and game.grid[row][6] is None:
            if not is_square_attacked(game.grid, game.pieces, row, 5, opponent) and \
               not is_square_attacked(game.grid, game.pieces, row, 6, opponent):
                castling_moves.append((row, 6))

    # Queenside castling (col 4 -> col 2, rook at col 0)
    rook_qs = game.grid[row][0]
    if rook_qs is not None and rook_qs.__class__.__name__ == "Rook" and rook_qs.first_move:
        if game.grid[row][1] is None and game.grid[row][2] is None and game.grid[row][3] is None:
            if not is_square_attacked(game.grid, game.pieces, row, 3, opponent) and \
               not is_square_attacked(game.grid, game.pieces, row, 2, opponent):
                castling_moves.append((row, 2))

    return castling_moves


def get_legal_moves(game, piece):
    """Return strictly legal moves for piece ensuring king is not left in check."""
    if piece is None:
        return []

    pseudo_moves = piece.get_possible_moves(game.grid, game.en_passant_target)
    legal_moves = []

    for tr, tc in pseudo_moves:
        orig_row, orig_col = piece.row, piece.col
        captured_piece = game.grid[tr][tc]

        # Handle en passant capture simulation
        ep_captured = None
        is_en_passant = (piece.__class__.__name__ == "Pawn" and
                         game.en_passant_target is not None and
                         (tr, tc) == game.en_passant_target and
                         captured_piece is None)
        if is_en_passant:
            ep_captured = game.grid[orig_row][tc]
            game.grid[orig_row][tc] = None
            if ep_captured is not None and ep_captured in game.pieces:
                game.pieces.remove(ep_captured)

        # Apply move to grid
        game.grid[orig_row][orig_col] = None
        game.grid[tr][tc] = piece
        piece.row, piece.col = tr, tc
        if captured_piece is not None and captured_piece in game.pieces:
            game.pieces.remove(captured_piece)

        # Check if own king is safe
        if not is_in_check(game.grid, game.pieces, piece.color):
            legal_moves.append((tr, tc))

        # Revert simulated move
        piece.row, piece.col = orig_row, orig_col
        game.grid[orig_row][orig_col] = piece
        game.grid[tr][tc] = captured_piece
        if captured_piece is not None and captured_piece not in game.pieces:
            game.pieces.append(captured_piece)

        # Revert en passant capture simulation
        if is_en_passant and ep_captured is not None:
            game.grid[orig_row][tc] = ep_captured
            if ep_captured not in game.pieces:
                game.pieces.append(ep_captured)

    # Append castling moves for king
    if piece.__class__.__name__ == "King":
        legal_moves.extend(get_castling_moves(game, piece))

    return legal_moves


def get_all_legal_moves(game, color):
    """Collect all strictly legal moves for all pieces of specified color."""
    all_moves = []
    for piece in list(game.pieces):
        if piece is not None and piece.color == color:
            moves = get_legal_moves(game, piece)
            for m in moves:
                all_moves.append((piece, m))
    return all_moves


def is_checkmate(game, color):
    """Verify if player of specified color has no legal moves while in check."""
    return is_in_check(game.grid, game.pieces, color) and len(get_all_legal_moves(game, color)) == 0


def is_stalemate(game, color):
    """Verify if player of specified color has no legal moves while not in check."""
    return not is_in_check(game.grid, game.pieces, color) and len(get_all_legal_moves(game, color)) == 0
