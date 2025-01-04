import matplotlib.pyplot as plt
import matplotlib
from fractions import Fraction
import random
import sys

fig = plt.figure()
ax = fig.add_subplot()
fig.subplots_adjust(top=0.85)

plt.gca().set_xlim([0, 4])
plt.gca().set_ylim([0, 5])
plt.gca().set_aspect('equal', adjustable='box')

half = Fraction(1, 2)
mid2pointid = dict()
pointid2mid = dict()

for i in range(4):
    for j in range(5):
        x = i + half
        y = j + half
        mid2pointid[(x,y)] = j*4 + i + 1
        pointid2mid[j*4 + i + 1] = (x,y)

names = ['曹操', '关羽', '张飞', '赵云', '马超', '黄忠', '兵', '空']
colors = ['b', 'g', 'k', 'c', 'm', 'y', 'r', 'w']

def plot(line):
    row = [int(i) for i in line.strip().split()]
    id_number = row.index(1)
    name = names[id_number]
    color = colors[id_number]
    for i, v in enumerate(row[8:]):
        if v == 1:
            p = i+1
            x, y = pointid2mid[p]
            ax.text(float(x), float(y), name, color=color,
                    family='Songti SC', ha='center', va='center')


gm_file = sys.argv[1]
solution_file = sys.argv[2]

with open(gm_file) as f:
    f.readline()
    mat = f.readlines()

with open(solution_file) as g:
    ss = g.readlines()

#s = random.choice(ss)
s = ss[100]
index = [int(k) for k in s.strip().split()]
for i in index:
    plot(mat[i])

ax.text(2, -0.4, '出           口', color='k',
        family='Songti SC', ha='center', va='center')    

plt.grid()
plt.savefig("a.png", dpi=400, bbox_inches='tight')
