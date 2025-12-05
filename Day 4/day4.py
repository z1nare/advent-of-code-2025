from collections import deque
def solve_first(inpt):
    # Part 1 from before — count accessible rolls
    grid = [list(line.strip()) for line in inpt]
    R, C = len(grid), len(grid[0])
    count_accessible = 0

    for r in range(R):
        for c in range(C):
            if grid[r][c] != '@':
                continue
            adj = 0
            for dr, dc in DIRS:
                nr, nc = r+dr, c+dc
                if 0 <= nr < R and 0 <= nc < C:
                    if grid[nr][nc] == '@':
                        adj += 1
            if adj < 4:
                count_accessible += 1

    return count_accessible


DIRS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

def solve_second(lines):
    g = [list(r.strip()) for r in lines]
    R, C = len(g), len(g[0])

    # adjacency count
    adj = [[sum(0 <= r+dr < R and 0 <= c+dc < C and g[r+dr][c+dc] == "@"
                for dr,dc in DIRS)
            for c in range(C)] for r in range(R)]

    q = deque((r,c) for r in range(R) for c in range(C)
              if g[r][c]=="@" and adj[r][c] < 4)

    removed = 0
    inq = set(q)

    while q:
        r,c = q.popleft()
        if g[r][c] != "@": continue
        g[r][c] = "."
        removed += 1

        for dr,dc in DIRS:
            nr,nc = r+dr, c+dc
            if 0<=nr<R and 0<=nc<C and g[nr][nc]=="@":
                adj[nr][nc] -= 1
                if adj[nr][nc] < 4 and (nr,nc) not in inq:
                    q.append((nr,nc))
                    inq.add((nr,nc))

    return removed





with open("input.txt","r") as file:
    lines = file.readlines()


print(solve_first(lines))
print(solve_second(lines))