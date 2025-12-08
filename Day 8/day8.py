def solve_first(lines):
    # Parse points
    points = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        x, y, z = map(int, s.split(","))
        points.append((x, y, z))
    n = len(points)
    if n == 0:
        return 0

    # Union-Find
    parent = list(range(n))
    size = [1] * n

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        if size[ra] < size[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        size[ra] += size[rb]
        return True

    # compute all pairwise squared distances
    dist_pairs = []
    for i in range(n):
        x1, y1, z1 = points[i]
        for j in range(i + 1, n):
            x2, y2, z2 = points[j]
            dx = x1 - x2
            dy = y1 - y2
            dz = z1 - z2
            d2 = dx * dx + dy * dy + dz * dz
            dist_pairs.append((d2, i, j))

    dist_pairs.sort(key=lambda x: x[0])

    # take the 1000 closest pairs (or all pairs if fewer)
    K = 1000
    for _, i, j in dist_pairs[:K]:
        union(i, j)

    # count component sizes
    comp = {}
    for i in range(n):
        r = find(i)
        comp[r] = comp.get(r, 0) + 1

    sizes = sorted(comp.values(), reverse=True)
    prod = 1
    for s in sizes[:3]:
        prod *= s
    return prod


def solve_second(lines):
    # Parse points
    points = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        x, y, z = map(int, s.split(","))
        points.append((x, y, z))
    n = len(points)
    if n <= 1:
        return 0

    # Union-Find
    parent = list(range(n))
    size = [1] * n

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        if size[ra] < size[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        size[ra] += size[rb]
        return True

    # compute all pairwise squared distances
    dist_pairs = []
    for i in range(n):
        x1, y1, z1 = points[i]
        for j in range(i + 1, n):
            x2, y2, z2 = points[j]
            dx = x1 - x2
            dy = y1 - y2
            dz = z1 - z2
            d2 = dx * dx + dy * dy + dz * dz
            dist_pairs.append((d2, i, j))

    dist_pairs.sort(key=lambda x: x[0])

    # initial component count
    components = n

    # iterate pairs in increasing distance; the moment union reduces components to 1,
    # return the product of X coordinates of that pair.
    for _, i, j in dist_pairs:
        if find(i) != find(j):
            unioned = union(i, j)
            if unioned:
                components -= 1
                if components == 1:
                    # multiply the X (index 0) coordinates of the two boxes
                    return points[i][0] * points[j][0]

    # If we never reached one component (shouldn't happen for reasonable inputs), return 0
    return 0


if __name__ == "__main__":
    with open("input.txt", "r") as file:
        lines = file.readlines()

    print(solve_first(lines))
    print(solve_second(lines))
