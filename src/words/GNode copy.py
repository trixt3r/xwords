from asyncio.proactor_events import _ProactorBaseWritePipeTransport
from xml.dom.expatbuilder import parseFragment
import cw as cwapi
# import unidecode
from words_tuple import word_info_t
# import build
GNODE_DEBUG = False

class GenericNode(object):
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

    # def addData(self, data):
    #     dk = self.dk(data)
    #     nk = self.nk(dk)
    #     c_node = self.search(nk, False)
    #     if c_node.path == nk:
    #         c_node.data[dk] = data
    #         return c_node
    #     elif nk.startswith(c_node.path):
    #         print('c_node: %s' % c_node.path)
    #         print('%s %s' % (nk[len(c_node.path):], c_node.children))
    #         best_len, best_path = GenericNode.trouver_meilleur_chemin(nk[len(c_node.path):], c_node.children, before=True)
    #         print('best_len: %d  best_path: %s' % (best_len, best_path))
    #         if best_len > 0:
    #             i_node = self.__class__(c_node.path + best_path[:best_len])
    #             i_node._setChild(c_node.path + best_path[best_len:], c_node.children[best_path])
    #             del c_node.children[best_path]
    #             if best_len + len(c_node.path) < len(nk):
    #                 new_node = self.__class__(nk, data)
    #                 print("$$$$$ %d %d %s %s" % (len(c_node.path), best_len, nk, i_node.path))
    #                 i_node._setChild(nk[len(i_node.path):], new_node)
    #             else:
    #                 i_node.data[nk] = data
    #                 new_node = i_node
    #             c_node._setChild(best_path[:best_len], i_node)
    #             return new_node
    #         else:
    #             new_node = self.__class__(nk, data)
    #             c_node._setChild(nk[len(c_node.path):], new_node)
    #             return new_node
    #     else:
    #         raise Exception("FOK")



    ## cette version ne semble pas utile
    # def addData2(self, data):
    #     dk = self.dk(data)
    #     nk = self.nk(dk)
    #     c_node = self.search(nk, False)
    #     path = nk[len(c_node.path):]
    #
    #     if len(path) == 0:  # le node trouvé est le bon
    #         assert(nk == c_node.path), "error trying to add {} data in {} node".format(nk, c_node)
    #         assert dk not in c_node.data, "node {} data already got {} key".format(c_node.path, dk)
    #         c_node.data[dk] = data  # mettre implement à jour les données et renvoyer le node
    #         return c_node
    #
    #     best_len, best_path = GenericNode.trouver_meilleur_chemin(path, [p for p in c_node.children.keys()], before=False)
    #     print("current: %s" % c_node.path)
    #     print("to add:  %s" % nk)
    #     print("found: %s %d (%s)" % (best_path, best_len, best_path[:best_len]))
    #     # créer le nouveau node
    #     new_node = None
    #     if best_len == 0:
    #         new_node = c_node.__class__(c_node.path + path)
    #         new_node.data[dk] = data
    #         c_node._setChild(path, new_node)
    #     else:
    #         # ÇA MERDE ENCORE
    #         # +"À" + "ABAISSÉE" + "ABAISSÉES" >> DISPARITION DE NOEUDS
    #
    #         # intercaller node intermédiaire
    #         i_node = c_node.__class__(c_node.path + best_path[:best_len])
    #         c_node._setChild(best_path[:best_len], i_node)
    #         i_node._setChild(best_path[best_len:], c_node.child(best_path))
    #         print("cut: ex:%s i_node: %s new_node: %s" % (best_path, best_path[:best_len], best_path[best_len:]))
    #         # celui ci est lié à i_node à présent, on l'enlève de la liste des enfants du node courant
    #         del c_node.children[best_path]
    #         print("aaaaaaaaaaaaaaa %d %d" % (best_len, len(nk)))
    #         if best_len == len(nk):
    #             i_node.data[dk] = data
    #             new_node = i_node  # pas un nouveau noeud mais c'est lui qui est mis à jour et doit etre renvoyé
    #             pass
    #         else: # insérer le nouveau node
    #             new_node = c_node.__class__(c_node.path + path)
    #             new_node.data[dk] = data
    #             i_node._setChild(dk[best_len:], new_node)
    #
    #     return new_node

    ##cette méthode, ça al'air d'être un peu n'importe quoi.
    # à refaire une fois qu'on aura compris ce que c'est sensé renvoyer
    # où c'est appelé
    # et surtout être malin;
    # def trouver_meilleur_chemin(path, paths, before=True):
    #     best_len = 0
    #     best_path = ""
    #     for p in paths:
    #         print("%s, %s" % (path, p))
    #         c_best_len = 0
    #         for i in range(0, len(path)):
    #             c_best_len = i
    #             if i < len(p) and path[i] == p[i]:
    #                 continue
    #             else:  # la concordance s'arrête ici
    #                 if i == 0:  # aucun carctère concordant
    #                     print("*1")
    #                     break
    #                 elif i <= len(p) and best_len < i:  # meilleur nouveau chemin
    #                     print("*2")
    #                     best_len = i 
    #                     best_path = p
    #                     break
    #                 elif best_len > 0 and best_len == i:
    #                     raise Exception("2 clés avec la même concordance path= {} old = {} found = {}".format(path, best_path, p))
    #                 else:
    #                     # on sort de la boucle car la concordance s'est arrêtée et
    #                     # et ce chemin n'est pas le meilleur
    #                     print("4")
    #                     break
    #         if c_best_len == len(path) - 1 and path[c_best_len-1] == p[c_best_len-1]:
    #             print("6a %d %d" % (best_len, c_best_len))
    #             if best_len < c_best_len and not before:
    #                 # nouveau meilleur chemin trouvé
    #                 # il est plus long que le chemin cherché,
    #                 # il faudra splitter pour insérer
    #                 print("6b")
    #                 best_path = p
    #                 best_len = c_best_len + 1
    #             else:
    #                 print("ouhouh %d %d %s" % (best_len, c_best_len, before))
    #         else:
    #             print("7")
    #             print("i = %d path %s p %s" % (c_best_len, path[c_best_len - 1], p[c_best_len - 1]))

    #     return (best_len, best_path)

    def _setChild(self, path, child):
        if isinstance(path, list):
            path = "".join(path)
        assert child.path == self.path+path, "error '{}'/'{}' trying to set child {} of node {} as {}".format(child.path, self.path+path, path, self.path, child.path)
        self.children[path] = child

    def search(self, data_key, exact_match=True):
        """Search from this node
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
            # TODO j'ai ajouté le dernier AND dans ce test,
            # mais j'ai comme l'impression que ça va me jouer des tours
            # il faut trouver un meilleur test, peut-être
        if exact_match and c_node.path != data_key and data_key!='':
            return None
        return c_node

    def split(self, path, new_path):
        assert path.startswith(new_path), "erreur split {} {}".format(path, new_path)
        node = self.__class__(self.path + new_path, None)
        node._setChild(path[len(new_path):], self.child(path))
        self._setChild(new_path, node)
        del self.children[path]
        return node
    
    def addData(self,data):
        dk = self.dk(data)
        nk = self.nk(dk)
        if GNODE_DEBUG is True:
            print("*#*#*#*#*# %s %s" %(dk, nk))
        parent_node = self.search(nk, False)
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
            if k != "":
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

    def search(self, data_key, exact_match=True):
        return super(WITNode, self).search(self.__class__.node_key(data_key), exact_match)

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

    def searchAnagram(self, sentence):
        canonic = self.__class__.node_key(sentence)
        ret = []
        fifo = [(self, canonic)]  # (node, path remainder)
        while len(fifo) > 0:
            s = fifo.pop()
            cn = s[0]  # curent node
            cw = s[1]  # path remainder to explore this branch
            print("sAnag: start loop %s %s" % (str(cn), cw))
            for c in cn.children:
                # this child node can be reached
                if cwapi.can_write(cw, c):
                    child_node = cn.child(c)
                    remainder = cwapi.difference(c, cw)
                    # add node to resut list only if it contains data
                    if len(child_node.data)>0:
                        ret.append(child_node)
                    # try to reach this child node's children
                    if len(remainder)>0:
                        fifo.append((child_node, remainder))
        return ret        


class APINode(WITNode):
    @classmethod
    def node_key(cls, n):
        r = [c for c in cwapi.iter_api_phoneme(n)]
        r.sort()
        return r

    @classmethod
    def data_key(cls, n):
        if not isinstance(n, list):
            n = [n]
        assert isinstance(n[0], word_info_t), "{}".format(n[0])
        if not(len(set([x.api for x in n]))==1):
            print(n)
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

def parcours_infixe(root, method):
    pass

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
    GNODE_DEBUG=True
    for x in gramm:
        root.addData(gramm[x])
    return (gramm, root)

# ajouter dans l'ordre: bonjour, bonshommes, bons.
# le dernier bug

# tout est bugué là-dedans de toutes façons
# il faut se rendre à l'évidence: je suis dans l'incapacité
# d'accomplir cette tâche
# autrement dit, j'ai été profondément marqué, en mal,
# par l'expérience que j'ai vécue.

gramm,root=create_tree()
del gramm['à'][0]
gramm, root2 = create_api_tree(gramm)