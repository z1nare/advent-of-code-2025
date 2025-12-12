import sys

def parse_input(lines):
    """Parses the input into shapes and region requirements."""
    lines = [ln.rstrip('\n') for ln in lines]
    shapes = []
    regions = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        # --- Parse Region Line (e.g. "12x5: 1 0 ...") ---
        if ':' in line:
            header, content = line.split(':', 1)
            if 'x' in header:
                try:
                    w_str, h_str = header.split('x')
                    W = int(w_str.strip())
                    H = int(h_str.strip())
                    counts = [int(tok) for tok in content.split()]
                    regions.append((W, H, counts))
                except ValueError:
                    pass
                i += 1
                continue

        # --- Parse Shape Header (e.g. "0:") ---
        if line.endswith(':') and line[:-1].strip().isdigit():
            i += 1
            shape_lines = []
            while i < len(lines):
                s = lines[i].rstrip()
                if s == "": break
                # Check if this line looks like a start of a new section
                if ':' in s:
                    head = s.split(':', 1)[0].strip()
                    if head.isdigit() or 'x' in head:
                        break
                
                if any(ch in '#.' for ch in s):
                    shape_lines.append(s)
                    i += 1
                else:
                    break
            
            # Convert text shape to coords
            coords = set()
            for r, row in enumerate(shape_lines):
                for c, ch in enumerate(row):
                    if ch == '#':
                        coords.add((c, r))
            
            # Normalize to (0,0)
            if coords:
                min_c = min(c for c, r in coords)
                min_r = min(r for c, r in coords)
                norm = frozenset((c - min_c, r - min_r) for c, r in coords)
                shapes.append(norm)
            else:
                shapes.append(frozenset())
            continue
        
        i += 1
    return shapes, regions

def get_variants(shape):
    """Generates all 8 unique orientations of a shape."""
    if not shape: return [shape]
    variants = set()
    coords = list(shape)
    for flip_x in (False, True):
        for flip_y in (False, True):
            for swap_xy in (False, True):
                trans = []
                for x, y in coords:
                    nx, ny = x, y
                    if flip_x: nx = -nx
                    if flip_y: ny = -ny
                    if swap_xy: nx, ny = ny, nx
                    trans.append((nx, ny))
                
                # Normalize
                min_x = min(x for x, y in trans)
                min_y = min(y for x, y in trans)
                norm = frozenset((x - min_x, y - min_y) for x, y in trans)
                variants.add(norm)
    return list(variants)

def generate_placements(W, H, shape):
    """
    Returns a list of integer bitmasks representing all valid positions 
    for the given shape (and its orientations) on a WxH grid.
    """
    variants = get_variants(shape)
    placements = [] # List of integer masks
    
    seen_masks = set()
    
    for var in variants:
        if not var: continue
        coords = list(var)
        max_x = max(c for c, r in coords)
        max_y = max(r for c, r in coords)
        
        if max_x >= W or max_y >= H:
            continue
            
        # Try every top-left position (ox, oy)
        for oy in range(H - max_y):
            for ox in range(W - max_x):
                mask = 0
                for c, r in coords:
                    # Map 2D (x,y) to 1D bit index
                    # Index = y * W + x
                    idx = (oy + r) * W + (ox + c)
                    mask |= (1 << idx)
                
                if mask not in seen_masks:
                    seen_masks.add(mask)
                    placements.append(mask)
    
    # Sort placements to ensure deterministic order (helps with canonical pruning)
    placements.sort()
    return placements

def solve_region_bitmask(W, H, shapes, counts):
    """
    Solves the packing problem using bitmasks and canonical ordering 
    to handle identical pieces efficiently.
    """
    # 1. Build the task list: which shapes do we need to place?
    #    We store them as a list of shape_indices, sorted.
    #    e.g. [0, 0, 1, 4, 4, 4]
    tasks = []
    total_area_needed = 0
    
    for s_idx, cnt in enumerate(counts):
        if s_idx < len(shapes) and cnt > 0:
            tasks.extend([s_idx] * cnt)
            total_area_needed += len(shapes[s_idx]) * cnt
            
    # Quick optimization: Area check
    if total_area_needed > W * H:
        return False
        
    # 2. Precompute bitmasks for every relevant shape
    #    cache[shape_idx] = [mask1, mask2, ...]
    relevant_shapes = set(tasks)
    placement_cache = {}
    
    for s_idx in relevant_shapes:
        masks = generate_placements(W, H, shapes[s_idx])
        if not masks:
            return False # Required shape fits nowhere
        placement_cache[s_idx] = masks

    # 3. Recursive Solver
    #    idx: current index in 'tasks' list we are trying to place
    #    board_mask: integer representing occupied cells
    #    last_placement_index: index in the 'masks' list of the PREVIOUS piece
    #                          (used to enforce order for identical pieces)
    
    # Optimization: Pre-calculate if the next task is the same as the current one
    # to avoid repeated lookups inside the hot loop.
    is_same_as_prev = [False] * len(tasks)
    for i in range(1, len(tasks)):
        if tasks[i] == tasks[i-1]:
            is_same_as_prev[i] = True

    def backtrack(task_idx, board_mask, last_placement_index):
        # Base Case: All pieces placed
        if task_idx == len(tasks):
            return True
        
        shape_idx = tasks[task_idx]
        masks = placement_cache[shape_idx]
        
        # Determine start index for loop
        # If this piece is the same type as the previous one, we must choose
        # a placement that comes strictly AFTER the previous placement 
        # (canonical ordering to remove N! symmetries)
        start_i = 0
        if is_same_as_prev[task_idx]:
            start_i = last_placement_index + 1
        
        # Try placements
        for i in range(start_i, len(masks)):
            m = masks[i]
            
            # Check collision: (board & mask) must be 0
            if (board_mask & m) == 0:
                # Place and recurse
                if backtrack(task_idx + 1, board_mask | m, i):
                    return True
        
        return False

    return backtrack(0, 0, -1)

def solve(lines):
    shapes, regions = parse_input(lines)
    count = 0
    print(f"Parsed {len(shapes)} shapes and {len(regions)} regions.")
    
    for i, (W, H, counts) in enumerate(regions):
        # Optional: Progress indicator for slow files
        # print(f"Solving region {i+1}/{len(regions)} ({W}x{H})...", file=sys.stderr)
        if solve_region_bitmask(W, H, shapes, counts):
            count += 1
            
    return count

if __name__ == "__main__":
    lines = []
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as f:
                lines = f.readlines()
        except IOError:
            print(f"Error reading file: {sys.argv[1]}")
            sys.exit(1)
    else:
        # Check if stdin has data
        if not sys.stdin.isatty():
            lines = sys.stdin.readlines()
        else:
            print("Usage: python day12.py input.txt")
            sys.exit(1)

    if lines:
        print(solve(lines))
    else:
        print("No input found.")