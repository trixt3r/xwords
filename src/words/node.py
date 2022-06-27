

class Node(object):
    def __init__(self, cw=""):
        self.cw = cw
        self.data = None
        self.children = {}

    def child(self, w):
        if w not in self.children:
            return None
        return self.children[w]

    def addWord(self, cw):
        f = self.search(cw)
        return f._addWord(cw[len(f.cw):])

    def _addWord(self, cw):
        """Create nodes recursively"""
        if len(cw) == 0:
            return self
        if not cw[0] in self.children:
            path = []
            if len(self.cw) == 0:
                path = [cw[0]]
            else:
                path = self.cw + [cw[0]]
            self.children[cw[0]] = Node(path)
        # self.total_descendants += 1
        return self.children[cw[0]]._addWord(cw[1:])

    def search(self, cw):
        """Search for cw from this node
        Return False if cw can't write a word from here, else return the
        cw node"""
        if len(cw) == 0:
            return self
        if not cw[0] in self.children:
            return self
        return self.children[cw[0]].search(cw[1:])

    def __repr__(self):
        if self.data is not None:
            return "<%s %d %d>" % (self.cw, len(self.data), len(self.children))
        return "<%s %d %d>" % (self.cw, 0, len(self.children))


# class TreeVisitor(object):
#     def __init__(self, data_sort, children_sort):
#         pass
#
#     def visit(node):
#         fifo = [node]
#         while len(fifo) > 0:
#             c_node = fifo.pop()
#             if c_node.data is not None:
#                 data_keys = [k for k in c_node.data.keys()]
#                 data_keys.sort()
#                 for k in data_keys:
#                     yield k
#             next = [c for c in c_node.children]
#             next.sort(reverse=True)
#             for c in next:
#                 fifo.append(c_node.children[c])


def parcours_arbre_data(node):
    fifo = [node]
    while len(fifo) > 0:
        c_node = fifo.pop()
        if c_node.data is not None:
            data_keys = [k for k in c_node.data.keys()]
            data_keys.sort()
            for k in data_keys:
                yield k
        next = [c for c in c_node.children]
        next.sort(reverse=True)
        for c in next:
            fifo.append(c_node.children[c])
