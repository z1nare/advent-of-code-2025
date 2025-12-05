def solve_first(lines):
    ranges = []
    ids = []

    # Parse input
    reading_ranges = True
    for line in lines:
        line = line.strip()
        if line == "":
            reading_ranges = False
            continue

        if reading_ranges:
            a, b = map(int, line.split("-"))
            ranges.append((a, b))
        else:
            ids.append(int(line))

    # Count fresh IDs
    fresh = 0
    for x in ids:
        for a, b in ranges:
            if a <= x <= b:
                fresh += 1
                break

    return fresh


def solve_second(lines):
    ranges = []

    # Parse only the ranges (stop at blank line)
    for line in lines:
        line = line.strip()
        if line == "":
            break
        a, b = map(int, line.split("-"))
        ranges.append((a, b))

    # Sort ranges by their start
    ranges.sort()

    # Merge overlapping ranges
    merged = []
    cur_start, cur_end = ranges[0]

    for a, b in ranges[1:]:
        if a <= cur_end + 1:   # overlap or touching
            cur_end = max(cur_end, b)
        else:
            merged.append((cur_start, cur_end))
            cur_start, cur_end = a, b

    merged.append((cur_start, cur_end))

    # Count total covered IDs
    total = sum(b - a + 1 for a, b in merged)
    return total




with open("input.txt","r") as file:
    lines = file.readlines()


print(solve_first(lines))
print(solve_second(lines))