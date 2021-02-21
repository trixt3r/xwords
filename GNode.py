import cw as cwapi
# import unidecode
from words_tuple import word_info_t
import build


class GenericNode(object):
    data_init = dict

    def __init__(self, path="", data = None):
        self.path = path
        self.data = self.__class__.data_init()
        if data is not None:
            self.data[self.dk(data)] = data
        self.children = {}

    def child(self, w):
        if w not in self.children:
            return None
        return self.children[w]

    def dk(self, x):
        return self.__class__.data_key(x)

    def nk(self, x):
        return self.__class__.node_key(x)

    def addData(self, data):
        dk = self.dk(data)
        nk = self.nk(dk)
        c_node = self.search(nk, False)
        if c_node.path == nk:
            c_node.data[dk] = data
            return c_node
        elif nk.startswith(c_node.path):
            best_len, best_path = GenericNode.trouver_meilleur_chemin(nk[len(c_node.path):], c_node.children, before=False)
            if best_len > 0:
                i_node = self.__class__(c_node.path + best_path[:best_len])
                i_node._setChild(c_node.path + best_path[best_len:], c_node.children[best_path])
                del c_node.children[best_path]
                if best_len + len(c_node.path) < len(nk):
                    new_node = self.__class__(nk, data)
                    print("$$$$$ %d %d %s %s" % (len(c_node.path), best_len, nk, i_node.path))
                    i_node._setChild(nk[len(i_node.path):], new_node)
                else:
                    i_node.data[nk] = data
                    new_node = i_node
                c_node._setChild(best_path[:best_len], i_node)
                return new_node
            else:
                new_node = self.__class__(nk, data)
                c_node._setChild(nk[len(c_node.path):], new_node)
                return new_node
        else:
            raise Exception("FOK")


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

    def trouver_meilleur_chemin(path, paths, before=True):
        best_len = 0
        best_path = ""
        for p in paths:
            print("%s, %s" % (path, p))
            c_best_len = 0
            for i in range(0, len(path)):
                c_best_len = i
                if i < len(p) and path[i] == p[i]:
                    continue
                else:  # la concordance s'arrête ici
                    if i == 0:  # aucun carctère concordant
                        print("1")
                        break
                    elif i <= len(p) and best_len < i+1:  # meilleur nouveau chemin
                        print("2")
                        best_len = i + 1
                        best_path = p
                        break
                    elif best_len > 0 and best_len == i:
                        raise Exception("2 clés avec la même concordance path= {} old = {} found = {}".format(path, best_path, p))
                    else:
                        # on sort de la boucle car la concordance s'est arrêtée et
                        # et ce chemin n'est pas le meilleur
                        print("4")
                        break
            if c_best_len == len(path) - 1 and path[c_best_len-1] == p[c_best_len-1]:
                print("6a")
                if best_len < c_best_len and not before:
                    # nouveau meilleur chemin trouvé
                    # il est plus long que le chemin cherché,
                    # il faudra splitter pour insérer
                    print("6b")
                    best_path = p
                    best_len = c_best_len + 1
                else:
                    print("ouhouh %d %d %s" % (best_len, c_best_len, before))
            else:
                print("7")
                print("i = %d path %s p %s" % (c_best_len, path[c_best_len - 1], p[c_best_len - 1]))

        return (best_len, best_path)

    def _setChild(self, path, child):
        assert(child.path == self.path+path), "error trying to set child {} of node {} as {}".format(path, self.path, child.path)
        self.children[path] = child

    def search(self, data_key, exact_match=True):
        """Search from this node
        """
        c_node = self
        while len(data_key) > 0:
            not_found = True
            print("search clé = %s in node %s" % (data_key, c_node))
            for p in c_node.children:
                if data_key.startswith(c_node.children[p].path):
                    c_node = c_node.children[p]
                    data_key = data_key[:len(c_node.path)]
                    not_found = False
                    break
            if not_found:
                break
        if exact_match and c_node.path != data_key:
            return None
        return c_node

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
        assert(isinstance(n[0], word_info_t))
        assert(len(set([x.mot for x in n])) == 1)
        return n[0].mot


def test_GNode():
    idx = build.createIndex()
    root = WITNode()
    rs = idx.search_anagrammes("reconstitutionnel")
    for x in rs:
        root.addData(x)
