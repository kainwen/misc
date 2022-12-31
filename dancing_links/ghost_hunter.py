#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from collections import namedtuple
import sympy as sym
from sympy.solvers import solve
import sys


Block = namedtuple('Block', ['name', 'col', 'cells', 'light_cell_idx'])

x = sym.Symbol('x')
y = sym.Symbol('y')

BlockA = Block('A', 1,
               [(x, y), (x+1, y), (x+1, y+1)],
               [0])
BlockB = Block('B', 2,
               [(x, y), (x+1, y)],
               [1])
BlockC = Block('C', 3,
               [(x, y), (x+1, y), (x+1, y-1)],
               [1])
BlockD = Block('D', 4,
               [(x, y), (x+1, y), (x, y+1)],
               [1,2])
BlockE = Block('E', 5,
               [(x, y), (x+1, y), (x, y+1)],
               [1])
BlockF = Block('F', 6,
               [(x, y), (x+1, y)],
               [])

AllBlocks = [BlockA, BlockB, BlockC, BlockD, BlockE, BlockF]

def rotate90(p, times):
    (a, b) = p
    P = sym.Matrix([[0, -1], [1, 0]])
    m = sym.Matrix([[a], [b]])
    r = (P**times) * m
    return (r[0], r[1])

"""
Board

(4,1) (4,2), (4,3) (4,4)
(3,1) (3,2), (3,3) (3,4)
(2,1) (2,2), (2,3) (2,4)
(1,1) (1,2), (1,3) (1,4)

13 14 15 16
 9 10 11 12
 5  6  7  8
 1  2  3  4
"""

def solve_eq(exp, target):
    assert(len(exp.free_symbols) == 1)
    val = list(exp.free_symbols)[0]
    return (val, solve(exp-target, val)[0])

def get_cell_id(a, b):
    return (a-1)*4 + b

Row = namedtuple('Row', ['block_col', 'cell_ids', 'light_cell_ids'])

def try_put_block(Blk):
    r = []
    for t in range(0, 4):
        new_cells = [rotate90(p, t) for p in Blk.cells]
        for i in range(1, 5):
            for j in range(1, 5):
                base = new_cells[0]
                bind1 = solve_eq(base[0], i)
                bind2 = solve_eq(base[1], j)
                cells_val = [(e1.subs(*bind1).subs(*bind2),
                              e2.subs(*bind1).subs(*bind2))
                             for e1, e2 in new_cells]
                if sum(1 for p in cells_val if not (1<= p[0] <= 4 and 1 <= p[1] <= 4)) > 0:
                    continue
                new_light_cells = [new_cells[idx] for idx in Blk.light_cell_idx]
                new_cell_ids = [get_cell_id(*p) for p in cells_val]
                row = Row(Blk.col, new_cell_ids, [new_cell_ids[idx] for idx in Blk.light_cell_idx])
                r.append(row)
    return r

def load_game():
    line = sys.stdin.readline()
    ghost_pos = eval(line)
    ghost_cells = [get_cell_id(*p) for p in ghost_pos]
    ghost_cells.sort()
    return ghost_cells

def print_row(r, ghosts_cell_ids_set, ghosts_cell_id_to_id_map):
    block_cols = [0] * 6
    block_cols[r.block_col-1] = 1
    cell_cols = [0] * 16
    for id in r.cell_ids:
        cell_cols[id-1] = 1
    ghost_cols = [0] * 6
    lighted = False
    for id in r.light_cell_ids:
        if id in ghosts_cell_ids_set:
            ghost_cols[ghosts_cell_id_to_id_map[id]-1] = 1
            lighted = True
    if (not lighted) and (not r.block_col == 6):
        return None
        
    row_vector = block_cols + cell_cols + ghost_cols
    return row_vector

def print_matrix():
    ghosts = load_game()
    rows = []
    ghosts_cell_ids_set = set(ghosts)
    ghosts_cell_id_to_id_map = dict([(cell_id, i+1) for i, cell_id in enumerate(ghosts)])
    
    for blk in AllBlocks:
        rows.extend(try_put_block(blk))
    print(len(rows), 28)
    for r in rows:
        rr = print_row(r, ghosts_cell_ids_set, ghosts_cell_id_to_id_map)
        if rr is not None:
            print(" ".join(list(map(str, rr))))

print_matrix()        
