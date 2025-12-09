def solve_first(lines):
    pts = []
    for line in lines:
        s = line.strip()
        if s:
            x, y = map(int, s.split(","))
            pts.append((x, y))

    n = len(pts)
    best = 0
    for i in range(n):
        x1, y1 = pts[i]
        for j in range(i + 1, n):
            x2, y2 = pts[j]
            area = (abs(x1 - x2) + 1) * (abs(y1 - y2) + 1)
            best = max(best, area)
    return best



def solve_second(lines):
    # Parse polygon vertices
    poly = []
    for line in lines:
        s = line.strip()
        if s:
            x, y = map(int, s.split(","))
            poly.append((x, y))

    n = len(poly)

    # Pre-process edges for faster checking
    # Store as (coordinate, start, end)
    edges_h = [] # Horizontal edges: y, xmin, xmax
    edges_v = [] # Vertical edges:   x, ymin, ymax
    
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if y1 == y2:
            edges_h.append((y1, min(x1, x2), max(x1, x2)))
        else:
            edges_v.append((x1, min(y1, y2), max(y1, y2)))

    def is_valid_rect(xmin, xmax, ymin, ymax):
        # 1. Center Check (Point in Polygon)
        # We verify the geometric center is inside. 
        cx = (xmin + xmax) / 2
        cy = (ymin + ymax) / 2
        
        inside = False
        # Add epsilon to cy to avoid issues if center lies exactly on a horizontal integer line
        test_y = cy + 1e-9 
        
        for i in range(n):
            px1, py1 = poly[i]
            px2, py2 = poly[(i + 1) % n]
            
            # Standard Ray Casting
            if (py1 > test_y) != (py2 > test_y):
                x_int = px1 + (test_y - py1) * (px2 - px1) / (py2 - py1)
                if x_int > cx:
                    inside = not inside
        
        if not inside:
            return False

        # 2. Vertex Inside Check
        # If the polygon winds inside the rectangle, a vertex must be strictly inside
        for px, py in poly:
            if xmin < px < xmax and ymin < py < ymax:
                return False

        # 3. Edge Splitting Check
        # A polygon edge cannot cut the rectangle in half
        
        # Check horizontal edges splitting the rectangle
        for ey, ex1, ex2 in edges_h:
            # Splits if the edge Y is strictly between top/bottom
            # AND the edge spans the entire width of the rectangle
            if ymin < ey < ymax and ex1 <= xmin and ex2 >= xmax:
                return False

        # Check vertical edges splitting the rectangle
        for ex, ey1, ey2 in edges_v:
            # Splits if the edge X is strictly between left/right
            # AND the edge spans the entire height of the rectangle
            if xmin < ex < xmax and ey1 <= ymin and ey2 >= ymax:
                return False

        return True

    best = 0
    # Iterate all pairs of vertices to form candidate rectangles
    for i in range(n):
        x1, y1 = poly[i]
        for j in range(i + 1, n):
            x2, y2 = poly[j]

            xmin, xmax = min(x1, x2), max(x1, x2)
            ymin, ymax = min(y1, y2), max(y1, y2)
            
            current_area = (xmax - xmin + 1) * (ymax - ymin + 1)
            
            # Optimization: Don't run expensive checks if area isn't better
            if current_area <= best:
                continue

            if is_valid_rect(xmin, xmax, ymin, ymax):
                best = current_area

    return best

# ----------------------- RUN ----------------------------
with open("input.txt", "r") as f:
    lines = f.readlines()
print(solve_first(lines))
print(solve_second(lines))