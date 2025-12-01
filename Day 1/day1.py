count = 0
pos = 50
TICK = 100 
with open("input.txt","r") as file:
    for line in file:
        line = line.strip()
        if not line:
            continue
        direction = line[0]
        steps = int(line[1:])
        delta = 1 if direction == "R" else -1

        for _ in range(steps):
            pos = (pos + delta) % TICK
            if pos == 0:
                count += 1
print(count)