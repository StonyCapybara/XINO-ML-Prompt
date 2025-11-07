# paste this in place of your previous version

from typing import List, Tuple, Optional
from copy import deepcopy
from math import inf

# --- El-Tetris weights (canonical) ---
WEIGHTS = {
    "landing_height": -4.500158825082766,
    "rows_eliminated":  3.4181268101392694,
    "row_transitions": -3.2178882868487753,
    "col_transitions": -9.348695305445199,
    "holes": -7.899265427351652,
    "well_sums": -3.3855972247263626,
}

# ----------------- Grid helpers -----------------
def copy_grid(grid):
    return [row[:] for row in grid]

def collides(grid, cells: List[Tuple[int,int]]) -> bool:
    for row, col in cells:
        newrow = row+1
        if newrow >= 19:
            return True
        if grid[newrow][col] != 0 and grid[newrow][col] != grid[row][col]:
            return True
    return False

def place_piece(grid: List[List[int]], cells: List[Tuple[int,int]], val: int = 1) -> Optional[List[List[int]]]:
    """
    Return a new grid with piece placed, or None if placement invalid (out-of-bounds or overlap).
    """
    g = copy_grid(grid)
    n_rows = len(g)
    n_cols = len(g[0])

    for r, c in cells:
        if r < 0 or r >= n_rows or c < 0 or c >= n_cols:
            return None
        if g[r][c] != 0:
            return None

    for r, c in cells:
        g[r][c] = val
    return g

def clear_full_lines(grid: List[List[int]]) -> Tuple[List[List[int]], List[int]]:
    """
    Remove full rows from `grid` and return (new_grid, cleared_rows).
    - grid: list of rows (top row first). 0 == empty, !=0 == filled.
    - new_grid: same shape as input (padded with empty rows on top).
    - cleared_rows: list of original row indices (0-based, top=0) that were cleared.
    """
    if not grid:
        return [], []

    n_rows = len(grid)
    n_cols = len(grid[0])

    new_rows: List[List[int]] = []
    cleared_rows: List[int] = []

    # Single pass: collect non-full rows and record full row indices
    for i, row in enumerate(grid):
        if all(cell != 0 for cell in row):
            cleared_rows.append(i)
        else:
            # copy row to avoid aliasing original grid rows
            new_rows.append(row.copy())

    if cleared_rows:
        # prepend the same number of empty rows at the top
        empty_rows = [[0] * n_cols for _ in range(len(cleared_rows))]
        new_grid = empty_rows + new_rows
    else:
        # no change, but return copies (defensive)
        new_grid = [row.copy() for row in grid]

    return new_grid, cleared_rows

# --------------- Feature calculators ----------------
def landing_height_avg(placed_cells):
    if not placed_cells:
        return 0.0
    return sum(r for r, _ in placed_cells) / len(placed_cells)

def rows_eliminated_feature(placed_cells, cleared_rows):
    e = len(cleared_rows)
    if e == 0:
        return 0
    cleared_set = set(cleared_rows)
    b = sum(1 for r, _ in placed_cells if r in cleared_set)
    return e * b

def row_transitions(grid):
    transitions = 0
    for row in grid:
        prev = 0
        for cell in row:
            curr = 1 if cell != 0 else 0
            if curr != prev:
                transitions += 1
            prev = curr
        if prev == 1:
            transitions += 1
    return transitions

def column_transitions(grid):
    transitions = 0
    n_rows = len(grid)
    n_cols = len(grid[0])

    for c in range(n_cols):
        prev = 0
        for r in range(n_rows):
            curr = 1 if grid[r][c] != 0 else 0
            if curr != prev:
                transitions += 1
            prev = curr
        if prev == 1:
            transitions += 1

    return transitions

def holes(grid):
    count = 0
    n_rows = len(grid)
    n_cols = len(grid[0])

    for c in range(n_cols):
        filled_seen = False
        for r in range(n_rows):
            if grid[r][c] != 0:
                filled_seen = True
            elif grid[r][c] == 0 and filled_seen:
                count += 1
    return count

def well_sums(grid):
    if not grid or not grid[0]:
        return 0

    n_rows = len(grid)
    n_cols = len(grid[0])
    total = 0

    for c in range(n_cols):
        well_depth = 0
        for r in range(n_rows):
            cell_empty = (grid[r][c] == 0)
            left_filled = (c == 0) or (grid[r][c - 1] != 0)
            right_filled = (c == n_cols - 1) or (grid[r][c + 1] != 0)

            if cell_empty and left_filled and right_filled:
                well_depth += 1
                total += well_depth
            else:
                well_depth = 0

    return total

def evaluate_eltetris(grid_after, placed_cells, cleared_rows):
    fh = landing_height_avg(placed_cells)
    f2 = rows_eliminated_feature(placed_cells, cleared_rows)
    f3 = row_transitions(grid_after)
    f4 = column_transitions(grid_after)
    f5 = holes(grid_after)
    f6 = well_sums(grid_after)
    score = (WEIGHTS["landing_height"] * fh
             + WEIGHTS["rows_eliminated"] * f2
             + WEIGHTS["row_transitions"] * f3
             + WEIGHTS["col_transitions"] * f4
             + WEIGHTS["holes"] * f5
             + WEIGHTS["well_sums"] * f6)
    print(score)
    return score

# ------------- Piece rotation helpers -------------
def normalize_cells(cells: List[Tuple[int,int]]) -> List[Tuple[int,int]]:
    if not cells:
        return []
    min_r = min(r for r, _ in cells)
    min_c = min(c for _, c in cells)
    return sorted(((r - min_r, c - min_c) for r, c in cells))

def rotate90_cells(cells: List[Tuple[int,int]]) -> List[Tuple[int,int]]:
    rotated = [(c, -r) for r, c in cells]
    min_r = min(r for r, _ in rotated)
    min_c = min(c for _, c in rotated)
    return sorted(((r - min_r, c - min_c) for r, c in rotated))

def generate_rotations_from_cells(cells: List[Tuple[int,int]]) -> List[List[Tuple[int,int]]]:
    rots = []
    cur = normalize_cells(cells)
    for _ in range(4):
        if cur not in rots:
            rots.append(cur)
        cur = rotate90_cells(cur)
    return rots

def ensure_relative_shape(cells: List[Tuple[int,int]]) -> List[Tuple[int,int]]:
    """If cells appear absolute (large row indices), convert to relative by shifting min row/col to 0."""
    if not cells:
        return []
    min_r = min(r for r, _ in cells)
    min_c = min(c for _, c in cells)
    return sorted(((r - min_r, c - min_c) for r, c in cells))

# -------------- Placement enumeration & simulation ----------------
def enumerate_final_placements(grid, piece, rotations = None):
    n_rows = len(grid)
    n_cols = len(grid[0])

    # build rotations only if not provided
    if rotations is None:
        if "rotations" in piece and piece["rotations"]:
            rotations = [normalize_cells(rot) for rot in piece["rotations"]]
        else:
            base_cells = piece.get("cells", [])
            base_cells = ensure_relative_shape(base_cells)
            rotations = generate_rotations_from_cells(base_cells)

    placements = []
    for rot_idx, rot in enumerate(rotations):
        max_r = max(r for r, _ in rot)
        max_c = max(c for _, c in rot)
        min_x = 0
        max_x = n_cols - (max_c + 1)
        for x in range(min_x, max_x + 1):
            drop = 0
            while True:
                test_cells = [(r + drop + 1, c + x) for r, c in rot]
                if collides(grid, test_cells):
                    break
                drop += 1
                if drop > n_rows:
                    break
            placed_cells = [(r + drop, c + x) for r, c in rot]
            if collides(grid, placed_cells):
                continue
            new_grid = place_piece(grid, placed_cells, val=1)
            new_grid, cleared_rows = clear_full_lines(new_grid)
            score = evaluate_eltetris(new_grid, placed_cells, cleared_rows)
            placements.append((rot_idx, rot, x, placed_cells, new_grid, cleared_rows, score))
    return placements

# -------------- Action planner ----------------
def compute_first_action(obs, target_rot_idx, target_x, rotations):
    piece = obs["current_piece"]
    curr_rot_idx = None
    curr_x = None

    if "rotation" in piece:
        curr_rot_idx = piece["rotation"]
    if "x" in piece:
        curr_x = piece["x"]

    if curr_x is None and "cells" in piece:
        cells = piece["cells"]
        try:
            curr_x = min(c for r, c in cells)
        except Exception:
            curr_x = None

    if curr_rot_idx is None and "cells" in piece:
        cur_cells = piece["cells"]
        try:
            rel = ensure_relative_shape(cur_cells)
            for i, rot in enumerate(rotations):
                if rel == rot:
                    curr_rot_idx = i
                    break
        except Exception:
            curr_rot_idx = None

    if curr_x is None or curr_rot_idx is None:
        return ' '

    if curr_rot_idx != target_rot_idx:
        return 'w'
    if curr_x > target_x:
        return 'a'
    if curr_x < target_x:
        return 'd'
    return ' '

# ----------------- Main Bot class --------------------
class Bot:
    def __init__(self) -> None:
        # any initialization/state goes here
        pass

    def decide(self, obs: dict):
        grid = obs["grid"]
        piece = obs["current_piece"]

        # compute rotations once and pass them through
        if "rotations" in piece and piece["rotations"]:
            rotations = [normalize_cells(rot) for rot in piece["rotations"]]
        else:
            base_cells = piece.get("cells", [])
            base_cells = ensure_relative_shape(base_cells)
            rotations = generate_rotations_from_cells(base_cells)

        placements = enumerate_final_placements(grid, piece, rotations)
        if not placements:
            return None

        best = max(placements, key=lambda t: t[-1])
        best_rot_idx, best_rot, best_x, _, _, _, _ = best

        action = compute_first_action(obs, best_rot_idx, best_x, rotations)
        return action
        # print(collides(grid, piece["cells"]))