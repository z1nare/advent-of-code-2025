invalid_sum = 0

with open("input.txt", "r") as file:
    for line in file:
        line = line.strip()
        if not line:
            continue
        for span in line.split(","):
            span = span.strip()
            if not span:
                continue
            lower_s, upper_s = span.split("-")
            lower = int(lower_s)
            upper = int(upper_s)

            for num in range(lower, upper + 1):
                s = str(num)
                n = len(s)
                found = False
                for i in range(1, n):          # chunk size
                    if n % i != 0:
                        continue
                    repetitions = n // i
                    if repetitions < 2:
                        continue
                    if s == s[:i] * repetitions:
                        invalid_sum += num
                        found = True
                        break                    # <--- important: count each number once
                # end inner for i
            # end for num
        # end for span
    # end for line

print(invalid_sum)
