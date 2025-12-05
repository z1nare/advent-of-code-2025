def solve_first(lines):
    total = 0

    for s in lines:
        s = s.strip()
        n = len(s)

        # Precompute max digit to the right for every position
        max_right = ["0"] * n
        current_max = "0"
        for i in range(n-1, -1, -1):
            max_right[i] = current_max
            if s[i] > current_max:
                current_max = s[i]

        best = 0
        for i in range(n-1):  # last digit can't be the tens digit
            tens = int(s[i])
            units = int(max_right[i])
            best = max(best, tens * 10 + units)

        total += best

    return total

def best_12_digit_joltage(s):
    s = s.strip()
    n = len(s)
    k = 12

    result = []
    start = 0

    while len(result) < k:
        need = k - len(result)
        end = n - need

        # Find the maximum digit in s[start:end+1]
        window = s[start:end+1]
        best_digit = max(window)
        idx = window.index(best_digit) + start

        result.append(best_digit)
        start = idx + 1

    return int("".join(result))


def solve_second(lines):
    total = 0
    for s in lines:
        if s.strip():
            total += best_12_digit_joltage(s)
    return total



with open("input.txt","r") as file:
    lines = file.readlines()


print(solve_first(lines))
print(solve_second(lines))