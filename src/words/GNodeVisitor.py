from GNode import *

class GNodeVisitor:
    def search(self, node, method):
        self.results = []
        def m(n):
            if method(n):
                self.results.append(n)
        parcours_largeur(node,m)
    pass