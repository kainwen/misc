import sys
import random

gm_file = sys.argv[1]
solution_file = sys.argv[2]

with open(gm_file) as f:
    f.readline()
    mat = f.readlines()

with open(solution_file) as g:
    ss = g.readlines()

for i in range(10):
    s = random.choice(ss)
    index = [int(k) for k in s.strip().split()]
    n = sum([int("".join(mat[idx].strip().split()))
             for idx in index])
    st = set(str(n))
    assert(len(st) == 1 and n%10 == 1)
