#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle
import cw as cwapi


class Occurences(object):
    def __init__(self):
        self.start = []
        self.end = []
        self.all = []

    def __repr__(self):
        return "%7d %7d %7d" % (len(self.start), len(self.all), len(self.end))


class SyllabeNode(object):
    chunks = {}

    def __init__(self, txt):
        self.txt=txt
        self.occ = Occurences()
        SyllabeNode.chunks[txt] = self

    def get(txt):
        if txt not in SyllabeNode.chunks:
            SyllabeNode.chunks[txt] = SyllabeNode(txt)
        return SyllabeNode.chunks[txt]

    def filter(f_test):
        for e in SyllabeNode.chunks:
            if f_test(e):
                yield SyllabeNode.chunks[e]

    def addWord(word):
        w_chunks = cwapi.syllabes(word)
        for c in w_chunks:
            SyllabeNode.get(c).occ.all.append(word)
        SyllabeNode.get(w_chunks[0]).occ.start.append(word)
        SyllabeNode.get(w_chunks[-1]).occ.end.append(word)
        return w_chunks

    def __repr__(self):
        return "<%7s> (%s)" % (self.txt, self.occ)


class Node(object):

    def __init__(self, cw=""):
        self.cw = cw
        self.children = {}
        self.complete_word = False
        self.tag = set()
        self.phonetics = {}

    def addWord(self, cw):
        f = self.search(cw)
        return f._addWord(cw[len(f.cw):])

    def _addWord(self, cw):
        """Create nodes recursively"""
        if cw == '':
            self.complete_word = True
            SyllabeNode.addWord(self.cw)
            return self
        if not cw[0] in self.children:
            self.children[cw[0]] = Node(self.cw+cw[0])
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

    def search_dispersed(self, cw):
        found = []
        if cw == '':
            return self.all_words()
        for c in self.children:
            found += self.children[c].search_dispersed(cwapi.difference(c, cw))
        return found

    def is_real_word(self):
        return self.complete_word
        # return not(self.cw == "")

    def all_words(self):
        found = []
        if self.is_real_word():
            found.append(self.cw)
        for c in self.children:
            found += self.children[c].all_words()
        return found

    # def explore(self, cw):
    #     """Return a list of all real words writeable from self
    #     with only cw characters."""
    #     i = 0
    #     found = []
    #     #if self.cw
    #     if self.is_real_word():
    #         found.append(self.cw)
    #     while i < len(cw):
    #         #for each character in cw
    #         c = cw[i]
    #         if c in self.children:
    #             #recursion on cw[i + 1] and not on intersect(cw,c)
    #             #cause our tree is sorted: cw[i -1] cannot be encountered
    #             #in self.children[c] children cause each child is >= c
    #             found = found + self.children[c].explore(cw[i + 1:])
    #         while i < len(cw) and cw[i] == c:
    #             i += 1
    #     return found

    def explore_f(self, cb, complete_word=True):
        if self.complete_word:
            cb(self)
        for c in self.children:
            self.children[c].explore_f(cb, complete_word)

    def explore4(self, cw):
        """Return a list of all real words writeable from self
        with only cw characters."""
        i = 0
        found = []
        # if self.cw
        if self.is_real_word():
            found.append(self.cw)
        while i < len(cw):
            # for each character in cw
            c = cw[i]
            if c in self.children:
                # recursion on cw[i + 1] and not on intersect(cw,c)
                # cause our tree is sorted: cw[i -1] cannot be encountered
                # in self.children[c] children cause each child is >= c
                fin = cw[i+1:]
                # if not fin == '':
                found = found + self.children[c].explore3(cw[:i]+fin)
            while i < len(cw) and cw[i] == c:
                i += 1
        return found

    def explore3(self, cw):
        """Return a list of all real words writeable from self
        with cw characters."""
        i = 0
        found = []
        # if self.cw
        if self.is_real_word():
            found.append(self.cw)
        while i < len(cw):
            # for each character in cw
            cs = [cw[i]]
            if cs[0] == "e":
                cs = ["e", "é", "è", "ê", "ë"]
            elif cs[0] == "a":
                cs = ["a", "à", "â", "ä"]
            elif cs[0] == "i":
                cs = ["i", "î", "ï"]
            elif cs[0] == "o":
                cs = ["o", "ô", "ö"]
            elif cs[0] == "u":
                cs = ["u", "û", "ü"]
            elif cs[0] == "y":
                cs = ["y", "ÿ"]
            elif cs[0] == "c":
                cs = ["c", "ç"]
            for c in cs:
                if c in self.children:
                    # recursion on cw[i + 1] and not on intersect(cw,c)
                    # cause our tree is sorted: cw[i -1] cannot be encountered
                    # in self.children[c] children cause each child is >= c
                    found = found + self.children[c].explore3(cw[:i]+cw[i + 1:])

            while i < len(cw) and cw[i] == cs[0]:
                i += 1
        return found

    # QUE FAIT EXACTEMENT CETTE FONCTION ?
    # REPONSE: ELLE FAIT DE LA MERDE
    # IL FAUT LA FAIRE TOURNER A LA MAIN POUR COMPRENDRE
    # JE SUIS DEVENU LE NIVEAU 0 DU PROGRAMMEUR
    # YA UNE GROSSE COUILLE DANS LE PATE C'EST NUL
    def search_redondant_branch(self, cw, offset, path):
        # we already found the first letters, we must find next letters
        # in direct children
        if offset > 0:
            if cw[offset] in list(self.children.keys()):
                return self.children[cw[offset]].\
                    search_redondant_branch(cw, offset + 1, path + cw[offset])
                print("*" + path)
            else:
                return 0
        if offset == 0:
            x = 0
            found = {}
            for c in list(self.children.keys()):
                if c < cw[0]:
                    x = self.children[c].\
                        search_redondant_branch(cw, 0, path + c)
                    pass
                elif c == cw[0]:
                    x = self.children[c].\
                        search_redondant_branch(cw, 1, path + c)
                    print(path)
                    pass
                elif c > cw[0]:
                    break
                if not x == 0:
                    found[c] = x
            return found
        if offset == len(cw) - 1:
            print("#" + path)
            return self

    # def search_redondant_branch2(self, cw, offset):
        #found = {}
        #if offset == len(cw) - 1:
            #found[''] = self
            #return found
        ##ça c'est bon, chercher dans les child <= cw[0]
        #if offset == 0:
            #for c in list(self.children.keys()):
                #if c > cw[offset]:
                    #break
                #x = ''
                #if c == cw[offset]:
                    #x = self.children[c].search_redondant_branch(cw,
                    #offset + 1)
                    #found[c] = x
                #if c < cw[0]:
                    #x = self.children[c].search_redondant_branch(cw, offset)
                    #found[c] = x
                ##if x != '':
                    ###found[c] = x
                    ##found[c] = self
        #else:
            #if cw[offset] in self.children:
                #x = self.children[cw[offset]].\
                    #search_redondant_branch(cw, offset + 1)
                #if x != '':
                    #found[cw[offset]] = x
        #return found
    def __repr__(self):
        if not self.complete_word:
            return "<-[%s]- %d>" % (self.cw, len(self.children))
        return "<%s %d>" % (self.cw, len(self.children))


# class WordNode(Node):
#     words = []
#     def word(w):
#         idx = bisect.bisect_left(WordNode.words,w)
#         if not words[idx]==w:
#             return -1


class RootNode(Node):
    def __init__(self):
        super(RootNode, self).__init__()
        self.node = Node()

    def addWord(self, cw):
        x = self.node.addWord(cw)
        x.complete_word = True

    def search(self, cw):
        return self.node.search(cw)

    def explore(self, cw):
        return self.node.explore(cw)

    def explore2(self, cw):
        return self.node.explore2(cw)

    def explore3(self, cw):
        return self.node.explore3(cw)

    def search_redondant_branch(self, cw):
        return self.node.search_redondant_branch(cw, 0, "")

    def search_redondant_branch2(self, cw):
        found = {}
        for c in list(self.node.children.keys()):
            if c < cw[0]:
                found[c] = self.node.children[c].search_redondant_branch(cw, 0,
                    "")
                pass
            elif c == cw[0]:
                found[c] = self.node.children[c].search_redondant_branch(cw, 1,
                     " ")
                pass
            elif c > cw[0]:
                break
        return found
        #return self.node.search_redondant_branch(cw, 0)

    def explore_f(self, cb, complete_word=True):
        self.node.explore_f(cb, complete_word)


def loadTree(filename):
    f = open(filename, "rb")
    rootNode = pickle.load(f)
    f.close()
    return rootNode


def init_index(dico):
    root = RootNode()
    i = 0
    for k in dico:
        for w in dico[k]:
            root.addWord(w)
            i += 1
            if i % 1000 == 0:
                print(i)
    return root


class Index:
    def __init__(self, dico_filename='', root_filename=''):

        if not dico_filename == '':
            f = open(dico_filename, 'rb')
            self.dico = pickle.load(f)
            f.close()
            print("dico ok")
        else:
            dico_filename = False
        if not dico_filename == '':
            self.rootNode = loadTree(root_filename)
            print("tree ok")
        else:
            self.rootNode = False

        if SyllabeNode.chunks == {}:
            f = open("data/syllabes.dmp", "rb")
            SyllabeNode.chunks = pickle.load(f)
            f.close()


class MetaNode(object):

    def __init__(self):
        self.node = ''
        self.prev = ""
        self.next = ""
