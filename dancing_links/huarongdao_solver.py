# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib
from fractions import Fraction
from copy import deepcopy
import pickle, sys
import networkx as nx


class HuarongDao:

    ADJ_INFO = [
        None,          #0, place holder
        [2,5],         #1
        [1,3,6],       #2
        [2,4,7],       #3
        [3,8],         #4
        [1,6,9],       #5
        [2,5,7,10],    #6
        [3,6,8,11],    #7
        [4,7,12],      #8
        [5,10,13],     #9
        [6,9,11,14],   #10
        [7,10,12,15],  #11
        [8,11,16],     #12
        [9,14,17],     #13
        [10,13,15,18], #14
        [11,14,16,19], #15
        [12,15,20],    #16
        [13,18],       #17
        [14,17,19],    #18
        [15,18,20],    #19
        [16,19]        #20
    ]

    NAMES = ['曹操', '关羽', '张飞', '赵云', '马超', '黄忠', '兵', '空']

    
    def __init__(self, gm_file, all_file):
        self.gm_file = gm_file
        self.all_file = all_file
        self.state_built = False

    def build_states(self):
        # each state is
        if self.state_built:
            return
        
        with open(self.gm_file) as f:
            f.readline()
            mat = [list(map(int, line.strip().split()))
                   for line in f]
        self.state_keys = []
        self.boards = []
        self.boards_rev_index = []
        self.keys_to_state = dict()
        self.board_to_state = dict()
        with open(self.all_file) as g:
            for i, line in enumerate(g):
                keys = tuple(sorted(list(map(int, line.strip().split()))))
                self.state_keys.append(keys)
                self.keys_to_state[keys] = i
                board = []
                board_rev_index = dict()
                for k in keys:
                    pos = []
                    bits = mat[k]
                    assert(bits.index(1) == len(board))
                    for j, b in enumerate(bits[8:]):
                        if b == 1:
                            pos.append(j+1)
                            board_rev_index[j+1] = len(board)
                    board.append(pos)
                self.boards.append(board)
                self.boards_rev_index.append(board_rev_index)
                self.board_to_state[tuple([tuple(lst) for lst in board])] = i
        self.state_built = True

    def dump_objs(self):
        assert(self.state_built)
        with open("boards", "wb") as f:
            pickle.dump(self.boards, f)
        with open("boards_rev_index", "wb") as f:
            pickle.dump(self.boards_rev_index, f)
        with open("keys_to_state", "wb") as f:
            pickle.dump(self.keys_to_state, f)
        with open("board_to_state", "wb") as f:
            pickle.dump(self.board_to_state, f)

    def load_objs(self):
        with open("boards", "rb") as f:
            self.boards = pickle.load(f)
        with open("boards_rev_index", "rb") as f:
            self.boards_rev_index = pickle.load(f)
        with open("keys_to_state", "rb") as f:
            self.keys_to_state = pickle.load(f)
        with open("board_to_state", "rb") as f:
            self.board_to_state = pickle.load(f)
        self.state_built = True

    def draw(self, state_id, fn):
        assert(self.state_built)
        fig = plt.figure()
        ax = fig.add_subplot()
        fig.subplots_adjust(top=0.85)
        plt.gca().set_xlim([0, 4])
        plt.gca().set_ylim([0, 5])
        plt.gca().set_aspect('equal', adjustable='box')

        half = Fraction(1, 2)
        one_over_ten = Fraction(1, 10)
        mid2pointid = dict()
        pointid2mid = dict()
        
        for i in range(4):
            for j in range(5):
                x = i + half
                y = j + half
                mid2pointid[(x,y)] = j*4 + i + 1
                pointid2mid[j*4 + i + 1] = (x,y)
                ax.text(float(i+one_over_ten), float(j+one_over_ten),
                        str(j*4 + i + 1), color='k', ha='center', va='center')

        colors = ['b', 'g', 'k', 'c', 'm', 'y', 'r', 'w']
        board = self.boards[state_id]
        for i, (name, pos) in enumerate(zip(self.NAMES, board)):
            color = colors[i]
            for p in pos:
                x, y = pointid2mid[p]
                ax.text(float(x), float(y), name, color=color,
                        family='Songti SC', ha='center', va='center')
           
        plt.grid()
        plt.savefig(fn, dpi=400, bbox_inches='tight')
        plt.cla()
        plt.clf()
        plt.close()

    def next_state(self, state_id):
        board = self.boards[state_id]
        board_rev_index = self.boards_rev_index[state_id]
        empty_pos = board[-1]
        new_state_ids = []
        for ep in empty_pos:
            adjs = self.ADJ_INFO[ep]
            for p in adjs:
                role_id = board_rev_index[p]
                if role_id == len(board) - 1: #empty
                    continue
                role_pos = board[role_id]
                new_state_id = self.move(role_id, p, ep, board, board_rev_index)
                if new_state_id:
                    if p - ep == 1:
                        action = "left"
                    elif p - ep == 4:
                        action = "down"
                    elif ep - p == 1:
                        action = "right"
                    else:
                        action = "up"
                    label = "move %s at %s %s one step" % (self.NAMES[role_id], p, action)
                    self.edge_labels[(state_id, new_state_id)] = label
                    new_state_ids.append(new_state_id)
        return new_state_ids

    def move(self, role_id, role_pos, empty_pos, board, board_rev_index):
        if role_id == len(board) - 2:
            #兵
            return self.move_bing(role_pos, empty_pos, board)
        else:
            old_pos = board[role_id]
            delta = empty_pos - role_pos
            new_pos = [p+delta for p in old_pos]
            for p in new_pos:
                if ((p <= 0 or p > 20) or
                    (board_rev_index[p] != role_id and
                     board_rev_index[p] != len(board) - 1)):
                    return None
            bd = deepcopy(board)
            bd[role_id] = new_pos
            bd[-1] = []
            st = set()
            for x in bd:
                for p in x:
                    st.add(p)
            es = list(set(range(1,21)) - st)
            es.sort()
            bd[-1] = es
            return self.board_to_state[tuple([tuple(lst) for lst in bd])]

    def move_bing(self, role_pos, empty_pos, board):
        bd = deepcopy(board)
        old_empty = bd[-1]
        old_bing = bd[-2]

        old_bing.remove(role_pos)
        old_bing.append(empty_pos)
        old_empty.remove(empty_pos)
        old_empty.append(role_pos)

        old_bing.sort()
        old_empty.sort()

        return self.board_to_state[tuple([tuple(lst) for lst in bd])]

    def create_and_dump_fsm(self):
        assert(self.state_built)
        self.edge_labels = dict()
        fsm = []
        for i in range(len(self.boards)):
            states = self.next_state(i)
            fsm.append(tuple(states))
        with open("fsm", "wb") as f:
            pickle.dump(fsm, f)
        with open("edge_labels", "wb") as f:
            pickle.dump(self.edge_labels, f)

    def load_fsm(self):
        with open("fsm", "rb") as f:
            self.fsm = pickle.load(f)
        with open("edge_labels", "rb") as f:
            self.edge_labels = pickle.load(f)

    def load_game(self):
        #print("please input a game:")
        line = sys.stdin.readline()
        bd = eval(line)
        state_id = self.board_to_state[tuple([tuple(lst) for lst in bd])]
        return state_id

    def get_all_finish_state_ids(self):
        return [i
                for i, board in enumerate(self.boards)
                if board[0] == [2,3,6,7]]

    def build_graph(self):
        assert(self.state_built)
        self.load_fsm()
        G = nx.DiGraph()
        for i in range(len(self.boards)):
            G.add_node(i)
        for i,t in enumerate(self.fsm):
            for j in t:
                G.add_weighted_edges_from([(i, j, 1)])
        return G

    def solve(self):
        start_state = self.load_game()
        if self.boards[start_state][0] == [2,3,6,7]:
            return [start_state]
        
        G = self.build_graph()        
        for i, board in enumerate(self.boards):
            if board[0] == [2,3,6,7]:
                try:
                    nodes = nx.dijkstra_path(G, start_state, i)
                    return nodes
                except nx.NetworkXNoPath:
                    continue

h = HuarongDao("gm2", "all2")
h.load_objs()
path = h.solve()
states = []
if path is not None:
    for i, st in enumerate(path):
        h.draw(st, "%s.%s.png" % (i, st))
        states.append(st)
        if h.boards[st][0] == [2,3,6,7]:
            break

for i in range(len(states) - 1):
    start = states[i]
    end = states[i+1]
    label = h.edge_labels[(start,end)]
    print(label)
