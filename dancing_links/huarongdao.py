#-*- coding: utf-8 -*-

from collections import namedtuple
from fractions import Fraction
import itertools


Block = namedtuple('Block', ['id', 'name', 'width', 'height'])

CaoCao = Block(1, 'CaoCao', 2, 2)
GuanYu = Block(2, 'GuanYu', 2, 1)
ZhangFei = Block(3, 'ZhangFei', 1, 2)
ZhaoYun = Block(4, 'ZhaoYun', 1, 2)
MaChao = Block(5, 'MaChao', 1, 2)
HuangZhong = Block(6, 'HuangZhong', 1, 2)


half = Fraction(1, 2)
mid2pointid = dict()

for i in range(4):
    for j in range(5):
        x = i + half
        y = j + half
        mid2pointid[(x,y)] = j*4 + i + 1

def try_block(block):
    r = []
    for x in range(0, 5):
        if x + block.width > 4: continue
        for y in range(0, 6):
            if y + block.height > 5: continue
            row = [0] * 28
            row[block.id-1] = 1
            for i in range(block.width):
                for j in range(block.height):
                    key = (x + i + half, y + j + half)
                    pointid = mid2pointid[key]
                    row[pointid+7] = 1
            r.append(row)
    return r


rows = []
for b in [CaoCao, GuanYu, ZhangFei, ZhaoYun, MaChao, HuangZhong]:
    rows.extend(try_block(b))

#Zu's ID = 7
#Empty's ID = 8
def handle_special(id_number, size):
    r = []
    for comb in itertools.combinations(range(1, 21), size):
        row = [0] * 28
        row[id_number-1] = 1
        for k in comb:
            row[k+7] = 1
        r.append(row)
    return r

rows.extend(handle_special(7, 4))
rows.extend(handle_special(8, 2))

print(len(rows), 28)
for r in rows:
    print(" ".join([str(i) for i in r]))
