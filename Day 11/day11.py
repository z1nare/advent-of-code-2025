import sys
import functools

nodes = dict() # map node name -> list of connections
with open("input.txt") as f:
    for line in f:
        line = line.strip()
        if ':' in line:
            node, outputs = line.split(':', 1)
            nodes[node.strip()] = [o.strip() for o in outputs.split()]

@functools.cache # FTW
def count_routes(this_node, visited_dac, visited_fft):
    match this_node:
        case 'out': return 1 if (visited_dac and visited_fft) else 0
        case 'dac': visited_dac = True
        case 'fft': visited_fft = True
    return sum(count_routes(link, visited_dac, visited_fft) for link in nodes[this_node])

if 'you' in nodes:
    print(f'part1: {count_routes("you", True, True)}')

if 'svr' in nodes:
    print(f'part2: {count_routes("svr", False, False)}')