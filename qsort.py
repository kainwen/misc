class Node:
    def __init__(self, data, next_node):
        self.data = data
        self.next_node = next_node

    def __str__(self):
        return "(%s, ->_)" % self.data

    def __repr__(self):
        return "(%s, ->_)" % self.data

def print_list(node):
    while node:
        print node.data,
        node = node.next_node
    print

def split(lst, split_point):
    l1 = lst.next_node
    curr = l1
    while True:
        if curr.next_node is split_point:
            curr.next_node = None
            lst.next_node = split_point
            return (l1, lst)
        else:
            curr = curr.next_node

def append_node(lst, node):
    while lst.next_node is not None:
        lst = lst.next_node
    lst.next_node = node
    node.next_node = None

def merge(l1, l2):
    curr = l1
    while curr.next_node:
        curr = curr.next_node
    curr.next_node = l2
    return l1

def qsort(head):
    assert head is not None
    if head.next_node is None:
        return head

    curr_node = head.next_node
    split_point = head.next_node

    cmp_data = head.data

    while curr_node:
        if curr_node.data < cmp_data:
            if curr_node is not split_point:
                curr_node.data, split_point.data = split_point.data, curr_node.data
            curr_node = curr_node.next_node
            split_point = split_point.next_node
        else:
            curr_node = curr_node.next_node

    if split_point is None:
        tail = head.next_node
        new_tail = qsort(tail)
        append_node(new_tail, head)
        return new_tail
    elif head.next_node is split_point:
        tail = head.next_node
        new_tail = qsort(tail)
        head.next_node = new_tail
        return head
    else:
        l1, l2 = split(head, split_point)
        new_l1, new_l2 = qsort(l1), qsort(l2)
        return merge(new_l1, new_l2)
