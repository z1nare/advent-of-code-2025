#!/usr/bin/env python3
from fractions import Fraction
from itertools import product
from math import prod
import sys
from typing import List, Tuple

# --- parsing ---
def parse_line(line: str):
    """Return (diagram, buttons_list, targets_list) or None for empty lines."""
    s = line.strip()
    if not s:
        return None
    # diagram between [ ]
    i1 = s.find('[')
    i2 = s.find(']', i1+1)
    diagram = s[i1+1:i2] if i1 != -1 and i2 != -1 else ""

    # buttons
    btns = []
    pos = i2 + 1 if i2 != -1 else 0
    while True:
        lpos = s.find('(', pos)
        if lpos == -1:
            break
        rpos = s.find(')', lpos+1)
        items = s[lpos+1:rpos].strip()
        if items == "":
            btns.append([])
        else:
            btns.append([int(x) for x in items.split(',')])
        pos = rpos + 1

    # targets inside { }
    bpos = s.find('{', pos)
    targets = []
    if bpos != -1:
        bclose = s.find('}', bpos+1)
        items = s[bpos+1:bclose].strip()
        if items != "":
            targets = [int(x) for x in items.split(',')]

    return diagram, btns, targets

# --- Gaussian elimination (exact with Fractions) to REF and pivots ---
def gaussian_elimination_ref(A: List[List[Fraction]], b: List[Fraction]) -> Tuple[List[List[Fraction]], List[int]]:
    """
    Convert augmented matrix [A|b] to row-echelon form (REF) using exact fractions.
    Returns (augmented_matrix_in_ref, pivot_cols_per_row) where pivot_cols[r] is column index or -1.
    """
    m = len(A)
    n = len(A[0]) if m>0 else 0
    # build augmented matrix
    M = [list(row) + [b_i] for row, b_i in zip(A, b)]
    pivot_cols = [-1]*m
    row = 0
    for col in range(n):
        # find pivot row
        sel = None
        for r in range(row, m):
            if M[r][col] != 0:
                sel = r
                break
        if sel is None:
            continue
        # swap
        M[row], M[sel] = M[sel], M[row]
        pivot_cols[row] = col
        # normalize pivot row (optional for REF; we don't need to divide)
        # eliminate below and optionally above to get reduced? We'll eliminate above too for easier back-sub.
        for r in range(m):
            if r != row and M[r][col] != 0:
                factor = M[r][col] / M[row][col]
                # row_r = row_r - factor * row_row
                for c in range(col, n+1):
                    M[r][c] -= factor * M[row][c]
        row += 1
        if row == m:
            break
    return M, pivot_cols

# --- Utilities ---
def build_matrix_from_buttons(targets: List[int], buttons: List[List[int]]) -> Tuple[List[List[Fraction]], List[Fraction]]:
    """
    Build integer matrix A (m x n) as Fractions and RHS b from buttons and targets.
    A[j][k] = how many increments button k adds to counter j in one press (usually 0 or 1).
    """
    m = len(targets)
    n = len(buttons)
    A = [[Fraction(0) for _ in range(n)] for __ in range(m)]
    for k, btn in enumerate(buttons):
        for idx in btn:
            if 0 <= idx < m:
                A[idx][k] += 1  # each press increments that counter by 1
    b = [Fraction(x) for x in targets]
    return A, b

def variable_upper_bounds(A: List[List[Fraction]], targets: List[int]) -> List[int]:
    """
    For each variable x_k, compute a safe upper bound:
      x_k <= min_{j: A[j][k] > 0} floor(target_j / A[j][k])
    If column is all zero, bound = 0 (variable has no effect).
    Add +1 margin if desired (user suggested +1) — we will not add margin here.
    """
    m = len(A)
    n = len(A[0]) if m>0 else 0
    bounds = [0]*n
    for k in range(n):
        ub = None
        for j in range(m):
            ak = A[j][k]
            if ak > 0:
                possible = int(targets[j] // int(ak)) if isinstance(targets[j], int) else int(targets[j] // ak)
                # but targets is given as int, A[j][k] is Fraction integer value
                # more robust: floor(target_j / A[j][k])
                possible = int((Fraction(targets[j]) / ak).numerator // (Fraction(targets[j]) / ak).denominator)
                if ub is None or possible < ub:
                    ub = possible
        bounds[k] = ub if ub is not None else 0
    # Ensure bounds are non-negative ints
    bounds = [max(0, int(x)) for x in bounds]
    return bounds

def solve_integer_min_sum(A_int: List[List[int]], b_int: List[int], max_free_product_cap=5_000_000) -> int:
    """
    Solve min sum x_k subject to A_int * x = b_int, x>=0 integer.
    Approach:
      - Use Fraction gaussian elimination on A/b to find pivots and free variables
      - Compute upper bounds for each variable
      - Enumerate all combinations of free variables within bounds (product of ranges)
      - For each combo, back-substitute pivots and check integer & bounds, track minimum sum
    Returns minimal sum (int) or raises RuntimeError if enumeration cap exceeded.
    """
    # Convert to Fractions
    A_frac = [[Fraction(v) for v in row] for row in A_int]
    b_frac = [Fraction(v) for v in b_int]

    # REF
    M_ref, piv_cols = gaussian_elimination_ref(A_frac, b_frac)
    m = len(M_ref)
    n = len(A_frac[0]) if m>0 else 0

    # Consistency check: any all-zero row with nonzero RHS -> no solution
    for r in range(m):
        all_zero = True
        for c in range(n):
            if M_ref[r][c] != 0:
                all_zero = False
                break
        if all_zero and M_ref[r][n] != 0:
            return 10**12  # no solution

    # identify pivot cols set and free cols list
    pivot_cols = set(c for c in piv_cols if c != -1)
    free_cols = [c for c in range(n) if c not in pivot_cols]

    # compute integer upper bounds per variable
    # Using simple heuristic: for each variable k, upper bound = min_j floor(b_j / A[j][k]) for A[j][k]>0
    bounds = [0]*n
    mA = len(A_int)
    for k in range(n):
        ub = None
        for j in range(mA):
            a_jk = A_int[j][k]
            if a_jk > 0:
                possible = b_int[j] // a_jk
                if ub is None or possible < ub:
                    ub = possible
        bounds[k] = ub if ub is not None else 0

    # If no free variables, just compute unique solution
    if not free_cols:
        # Solve pivot variables by back substitution
        x = [0]*n
        # Because we performed elimination eliminating all other rows, we can compute:
        # For each pivot row r with pivot column c: M_ref[r][c] * x_c + sum_{cc>c} M_ref[r][cc]*x_cc = M_ref[r][n]
        # free vars are none so x_cc = 0 for cc>c
        for r in range(m-1, -1, -1):
            c = piv_cols[r]
            if c == -1:
                continue
            rhs = M_ref[r][n]
            s = Fraction(0)
            for cc in range(c+1, n):
                s += M_ref[r][cc] * Fraction(x[cc])
            val = (rhs - s) / M_ref[r][c]
            if val.denominator != 1:
                return 10**12
            iv = int(val)
            if iv < 0 or iv > bounds[c]:
                return 10**12
            x[c] = iv
        return sum(x)

    # determine product of free ranges
    free_ranges = [range(bounds[c]+1) for c in free_cols]  # 0..bounds[c]
    total_combinations = prod(len(rng) for rng in free_ranges)
    if total_combinations > max_free_product_cap:
        raise RuntimeError(f"Free-variable search too big: {total_combinations} combinations (cap {max_free_product_cap})")

    best_sum = None

    # For stable back-substitution, build a mapping row->pivot column and ensure rows with pivot exist
    # We'll use piv_cols list as returned (length m, with -1 for non-pivot rows)
    for combo in product(*free_ranges):
        x = [0]*n
        # assign free vars
        for idx, c in enumerate(free_cols):
            x[c] = combo[idx]

        # back-substitute pivot vars
        valid = True
        # iterate rows from bottom to top
        for r in range(m-1, -1, -1):
            c = piv_cols[r]
            if c == -1:
                # if row has no pivot, check equality 0 = rhs
                # all coefficients should be zero in that row
                # if RHS != 0 then inconsistent; skip
                if M_ref[r][n] != 0:
                    valid = False
                    break
                continue
            # compute rhs - sum_{cc>c} M[r][cc]*x_cc
            rhs = M_ref[r][n]
            s = Fraction(0)
            for cc in range(c+1, n):
                s += M_ref[r][cc] * Fraction(x[cc])
            # compute variable value
            denom = M_ref[r][c]
            if denom == 0:
                # shouldn't happen
                valid = False
                break
            val = (rhs - s) / denom
            # must be integer and within bounds
            if val.denominator != 1:
                valid = False
                break
            iv = int(val)
            if iv < 0 or iv > bounds[c]:
                valid = False
                break
            x[c] = iv
        if not valid:
            continue

        # final verification: A_int * x == b_int
        ok = True
        for j in range(mA):
            ssum = 0
            for k in range(n):
                ssum += A_int[j][k] * x[k]
            if ssum != b_int[j]:
                ok = False
                break
        if not ok:
            continue

        ssum = sum(x)
        if best_sum is None or ssum < best_sum:
            best_sum = ssum

    return best_sum if best_sum is not None else 10**12

# --- top-level ---
def solve_joltage_for_line(buttons: List[List[int]], targets: List[int]) -> int:
    """
    Return minimal presses (sum of x) for this machine configuration.
    """
    if not targets:
        return 0
    # build integer matrix A and vector b
    m = len(targets)
    n = len(buttons)
    A_int = [[0]*n for _ in range(m)]
    for k, btn in enumerate(buttons):
        for idx in btn:
            if 0 <= idx < m:
                A_int[idx][k] += 1
    b_int = list(targets)

    # quick infeasibility: check each row j has at least one positive coefficient if b[j]>0
    for j in range(m):
        if b_int[j] > 0 and all(A_int[j][k] == 0 for k in range(n)):
            return 10**12

    # call solver with a reasonable cap
    return solve_integer_min_sum(A_int, b_int, max_free_product_cap=5_000_000)

# --- script entrypoint ---
def main(filename: str):
    total = 0
    with open(filename) as f:
        lines = f.readlines()
    machine_idx = 0
    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            continue
        diagram, buttons, targets = parsed
        machine_idx += 1
        try:
            mpress = solve_joltage_for_line(buttons, targets)
        except RuntimeError as e:
            print(f"Machine {machine_idx}: free-variable search too large; {e}")
            raise
        print(f"Machine {machine_idx}: min presses = {mpress}")
        total += mpress
    print("Total presses (sum over machines):", total)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python joltage_solver.py input.txt")
        sys.exit(1)
    main(sys.argv[1])
