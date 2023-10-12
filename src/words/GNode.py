# from asyncio.proactor_events import _ProactorBaseWritePipeTransport
# from xml.dom.expatbuilder import parseFragment
import queue
import cw as cwapi
from IPAIter import IPAStr
# import unidecode
from words_tuple import word_info_t
# import build
GNODE_DEBUG = False

class GenericNode(object):
    """
    Je suis bien dan la merde pour reprendre ce code, car je ne l'ai pas documenté....
    Et ça fait plus d'un an que je n'y ai pas touché
    
    """
    data_init = dict

    def __init__(self, path="", data = None):
        self.path = path
        self.data = self.__class__.data_init()
        if data is not None:
            self.data[self.dk(data)] = data
        self.children = {}

    def child(self, w):
        if not isinstance(w, str):
            x = self
            for p in w:
                x = x.child(p)
            return x
        if w not in self.children:
            return None
        return self.children[w]

    def dk(self, x):
        return self.__class__.data_key(x)

    def nk(self, x):
        return self.__class__.node_key(x)

    def _setChild(self, path, child):
        if isinstance(path, list):
            path = "".join(path)
        assert child.path == self.path+path, f"error '{child.path}'/'{self.path+path}' trying to set child { path} of node {self.path} as {child.path}"
        self.children[path] = child

    def search(self, data_key):
        """Search from this node
        returns: the closest node from data_key
        ex: if node searched is "spare" but only word is "spear", then
        node with path "sp" is returned
        """
        c_node = self
        while len(data_key) > 0:
            not_found = True
            # print("search clé = %s in node %s" % (data_key, c_node))
            for p in c_node.children:
                # print('check %s %s %s' % (data_key, p, c_node.children[p].path))
                if data_key.startswith(p):
                    # print('ok')
                    c_node = c_node.children[p]
                    data_key = data_key[len(p):]
                    not_found = False
                    break
            if not_found:
                break
        return c_node

    def split(self, path, new_path):
        assert path.startswith(new_path), "erreur split {} {}".format(path, new_path)
        node = self.__class__(self.path + new_path, None)
        node._setChild(path[len(new_path):], self.child(path))
        self._setChild(new_path, node)
        del self.children[path]
        return node
    
    def addData(self,data):
        global GNODE_DEBUG
        dk = self.dk(data)
        nk = self.nk(dk)
        if GNODE_DEBUG is True:
            print("*#*#*#*#*# %s %s" %(dk, nk))
        parent_node = self.search(nk)
        target_node = None
        if parent_node.path != nk:
            #assert nk.startswith(parent_node.path), "erreur nk={} found_node.path={}".format(nk, parent_node.path)
            reste = nk[len(parent_node.path):]
            k = "" # la branche-fille où insérer nos données
            for n in parent_node.children:
                # print("### %s %s" % (n,reste))
                if n[0]==reste[0]:
                    k = n
                    break
            if k != "":  #  on doit créer un noeud intermédiaire
                # print("####################1")
                # need to split
                i = 0
                for i in range(0,min(len(k), len(reste))):
                    if k[i]!=reste[i]:
                        break
                    i += 1
                # print("common length: %d" % i)
                if i== len(k):
                    # on devrait pas arriver ici
                    # car le fils correspondant (parent_node.child(k))
                    # aurait du être la valeur de retour de la ligne:
                    # parent_node = self.search(nk), au début de l'algo.
                    # c'est pourquoi, on y passe jamais
                    # mais je laisse ça quand même, on ne sait jamais.
                    assert False, "erreur!!!"
                    pass
                else:
                    inter_node = parent_node.split(k, k[:i])
                    new_node = self.__class__(nk, data)  #  create new node
                    inter_node._setChild(nk[len(inter_node.path):], new_node)  #  insert new node
                    return new_node
            else:   
                # print("####################2")
                # on tombe ici quand arbre vide, ou bien suffixe à ajouter
                # sur le noeud trouvé
                new_node = self.__class__(nk, data)  #  create new node
                parent_node._setChild(nk[len(parent_node.path):], new_node)
                return new_node
        else:
            # print("####################3")
            target_node = parent_node

        if target_node.data is None:
            target_node.__class__.data_init()
        target_node.data[dk] = data
        return target_node

    def searchAnagram(self, sentence, keep_accents=True):
        canonic = self.__class__.node_key(sentence)
        ret = []
        fifo = [(self, canonic)]  # (node, path remainder)
        while len(fifo) > 0:
            s = fifo.pop()
            cn = s[0]  # curent node
            cw = s[1]  # path remainder to explore this branch
            # print("sAnag: start loop %s %s" % (str(cn), cw))
            for c in cn.children:
                # this child node can be reached
                if cwapi.can_write(cw, c):
                    child_node = cn.child(c)
                    remainder = cwapi.difference(c, cw)
                    # add node to resut list only if it contains data
                    if child_node.hasData:
                        ret.append(child_node)
                    # try to reach this child node's children
                    if len(remainder)>0:
                        fifo.append((child_node, remainder))
        return ret

    def count(self):
        x = 1
        for c in self.children:
            x += self.child(c).count()
        return x

    @property
    def hasData(self):
        if self.data is None or len(self.data)==0:
            return False
        return True

    @property
    def isleaf(self):
        return len(self.children) == 0

    def __repr__(self):
        return "<%s %d %d>" % (self.path, len(self.data), len(self.children))

    @classmethod
    def node_key(cls, n):
        return n

    @classmethod
    def data_key(cls, n):
        return n


class CWordNode(GenericNode):
    @classmethod
    def node_key(cls, n):
        return cwapi.getCanonicForm(n)

    @classmethod
    def data_key(cls, n):
        return n



# orthographe, data== {orth:[word_info_tuple,...]}
class WITNode(CWordNode):
    @classmethod
    def node_key(cls, n):
        return cwapi.getCanonicForm(n)

    @classmethod
    def data_key(cls, n):
        if not isinstance(n, list):
            n = [n]
        assert isinstance(n[0], word_info_t), "{}".format(n[0])
        assert len(set([x.mot for x in n])) == 1, "plusieurs mots différents"
        return n[0].mot

    # @classmethod
    # def key_tokenizer(cls, key):
    #     for c in key:
    #             yield c

    def search(self, data_key):
        # return super(self.__class__, self).search(self.__class__.node_key(data_key), exact_match)
        return super(WITNode, self).search(self.__class__.node_key(data_key))

    def search_child(self, path):
        if path in self.children:
            return path
        best = ""
        for c in self.children:
            i = 0
            while c[i] == path[i]:
                i += 1
            if i > len(best):
                best = c[:i]
        return best

    # def searchAnagram(self, sentence):
    #     canonic = self.__class__.node_key(sentence)
    #     ret = []
    #     fifo = [(self, canonic)]  # (node, path remainder)
    #     while len(fifo) > 0:
    #         s = fifo.pop()
    #         cn = s[0]  # curent node
    #         cw = s[1]  # path remainder to explore this branch
    #         print("sAnag: start loop %s %s" % (str(cn), cw))
    #         for c in cn.children:
    #             # this child node can be reached
    #             if cwapi.can_write(cw, c):
    #                 child_node = cn.child(c)
    #                 remainder = cwapi.difference(c, cw)
    #                 # add node to resut list only if it contains data
    #                 if child_node.hasData:
    #                     ret.append(child_node)
    #                 # try to reach this child node's children
    #                 if len(remainder)>0:
    #                     fifo.append((child_node, remainder))
    #     return ret        


class APINode(WITNode):
    @classmethod
    def node_key(cls, n):
        # print('trying to get node key from:')
        # print(n)
        r = [c for c in cwapi.iter_api_phoneme(n)]
        r.sort()
        return IPAStr("".join(r))
        # return "".join(r)

    @classmethod
    def data_key(cls, n):
        if not isinstance(n, list):
            n = [n]
        assert isinstance(n[0], word_info_t), "{}".format(n[0])
        if len(set([x.api for x in n])) > 1:
            print('ça va bugger')
            u=list(set([x.api for x in n]))
            print(", ".join(u))
        assert len(set([x.api for x in n])) == 1, "plusieurs mots différents"
        return n[0].api

    def addData(self,data):
        return super(APINode, self).addData(data)

counter=0

def count_cb(node):
    global counter
    counter+=1
    if counter%500==0:
        print("%s %d" % (node.path, counter))

def print_cb(node):
    print("%s" % node.path)
    counter += 1

def parcours_prefixe(root, callback):
    queue = [root]
    while len(queue)>0:
        node = queue.pop(0)
        callback(node)
        for c in node.children:
            queue.append(node.child(c))
    pass

def test_GNode():
    root = GenericNode()
    root.addData("bonjour")
    root.addData('bonshommes')
    return root


def parcours_largeur_yield(root, filter=None):
    """browse from node, yields each node who pass the filter.
    If a node doesn't pass the filter, its children aren't visited.
    If no filter given, all node are yield. """
    fifo = queue.Queue()
    fifo.put(root)
    if filter is None:
        filter = lambda x: True
    while not fifo.empty():
        node = fifo.get()
        if filter(node):
            yield node
            for n in node.children:
                fifo.put(node.child(n))

def parcours_largeur(root, method, node_filter=None):
    """Applies method on each node who pass filter"""
    for n in parcours_largeur_yield(root, node_filter):
        method(n)

def parcours_largeur_data(root, node_filter=None, data_filter=None):
    if data_filter is None:
        data_filter = lambda x: True
    def m(node):
        for x in node.data:
            data_list=node.data[x]
            for e in data_list:
                if data_filter(e):
                    yield e
    for node in parcours_largeur_yield(root, node_filter):
        for wit in m(node):
            yield wit

def m_test(wit):
    return wit.api.startswith('bi')

def len_filter(node):
    return len(node.path)<4

results = []
def mk_search_for_end(e):
    global results
    def m_search(n):
        for x in n.data:
            x=n.data[x]
            for y in x:
                if y.api.endswith(e):
                    return True
        return False
    return m_search

def mk_search_for_start(e):
    global results
    def m_search(n):
        for x in n.data:
            x=n.data[x]
            for y in x:
                if y.api.startswith(e):
                    results.append(y)
    return m_search

import pickle
def create_tree():
    f=open("data/gramm.dmp", "rb")
    gramm=pickle.load(f)
    f.close()
    root = WITNode()
    for x in gramm:
        root.addData(gramm[x])
    return (gramm, root)


#TODO: pas super simple de faire une classe générique
# pour l'orthographe ET la phonétique
# il va falloir aller ajouter une classe méthode "key_tokenizer"
# exactement comme dans la classe arbre originelle
def create_api_tree(gramm=None):
    if gramm is None:
        f=open("data/gramm.dmp", "rb")
        gramm=pickle.load(f)
        f.close()
    root = APINode()
    # GNODE_DEBUG=True
    for x in gramm:
        for y in gramm[x]:
            root.addData([y])
    return (gramm, root)

# ajouter dans l'ordre: bonjour, bonshommes, bons.
# le dernier bug

# tout est bugué là-dedans de toutes façons
# il faut se rendre à l'évidence: je suis dans l'incapacité
# d'accomplir cette tâche
# autrement dit, j'ai été profondément marqué, en mal,
# par l'expérience que j'ai vécue.

# gramm,root=create_tree()

f=open("data/gramm.dmp", "rb")
gramm=pickle.load(f)
f.close()

f=open("data/gnode_tree.dmp", "rb")
root=pickle.load(f)
f.close()

del gramm['à'][0]

root2=APINode()
root2.addData(gramm['banquier'])
gramm, root2 = create_api_tree(gramm)