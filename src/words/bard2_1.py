import pickle
import unicodedata
import numpy as np
from GDict import *


from words_tuple import word_info_t
from cw import iter_api_phoneme, iter_api_syllabes

# celle ci fonctionne mais trop lente 
# cause accès dict children
class Node[T]:
    def __init__(self, path='', data=None, parent=None):
        # self.children = SortedDictWithFallback(np.array([],dtype=np.dtype(str)),np.array([],dtype=np.dtype(str)))
        self.children:dict[str,T] = {}
        self.endOfString = False
        self.path = path
        self.data:list[T] = []
        if data is not None:
            self.data.append(data)

    def insert(self, data:T):
        new_key = self.get_key(data)
        closest = self.search(new_key, False) # le noeud le plus proche du point d'insertion
        if closest is False:
            closest=self
        i = len(closest.path)
        new_node = None
        # print(f"insert {word} found {current.path} reste {word[i:]}")

        #pour chaque clef-fils
        for key in closest.children:
            j = 0

            while j<len(key) and i+j<len(new_key) and key[j]==new_key[i+j]:  # comparer avec la clef de notre nouveau noeud
                j += 1

            ################
            if new_key == closest.path:
                closest.data.append(data)
                return closest
            if  (j==len(key) and i+j==len(new_key)): # exact match
                assert key[j-1] == new_key[i+j-1]
                # le noeud existe deja -> update data
                n = closest.children[key]
                n.data.append(data)
                return n

            if j==len(key) and i+j<len(new_key):
                # le nouveau mot est plus long que l'existant > prolonger
                new_node = type(self)(new_key,data)
                closest.children[key].children[new_key[i+J:]] = new_node
                return new_node

            if j<len(key) and i+j==len(new_key):
                # le nouveau mot est plus court que l'existant > noeud intermédiaire, insertion 
                interm = type(self)(new_key, data)
                interm.children[key[j:]]=closest.children[key]  
                del closest.children[key]
                return interm

            assert key[j]!=new_key[i+j] 
            # dernier cas : le fork
            # création noeud intermédiaire
            # par definition, on n'a pas de données à y stocker à cette heure
            interm = type(self)(new_key[:i+j])
            # print(f"{new_key[:i+j]}")
            # print(f"interm: {interm}")
            # on lui greffe ses fils
            interm.children[key[j:]] = closest.children[key]
            new_node = type(self)(new_key, data)
            interm.children[new_key[i+j:]] = new_node
            # on remplace la branche dans le noeud parent
            closest.children[key[:j]] = interm
            del closest.children[key]
            # print(f"{data} {new_node} {interm} SORTIE A")
            return new_node

        # arrivé ici, on n'a pas trouvé de piste concordante, 
        # il faut prolonger la branche en ajoutant un fils au noeud closest
        new_node = type(self)(new_key, data)
        # assert new_key[i:] not in closest.children
        closest.children[new_key[i:]] = new_node
        return new_node
        

    def search(self, key, exact=True):
        current = self
        i = 0
        while i < len(key):
            next=False
            for clef in current.children:
                j = 0
                # print(f"test {clef} {word[:i]}")
                while j<len(clef) and i+j<len(key) and clef[j]==key[i+j]:
                    j+=1
                if j == len(clef):
                    #continuer la recherche dans le prochain node
                    i += j
                    current = current.children[clef]
                    # print(f"ok {clef} {current.path}")
                    next=True
                    break
            if not next:
                return current if not exact or current.path==key else False
        return current if not exact or current.path==key else False

    def get_key(self, obj:T):
        return None

    def __repr__(self):
        return f"<{self.path} {len(self.data)}, {len(self.children)}>"

class Word_Ort_Node[word_info_t]:
    """
    classe-node stockant les mots-tuples selon leur orthographe, tout simplement
    """
    def get_key(self, obj:word_info_t):
        return obj.mot

#TODO: pas super optimisé tout ça
class APIPhonStr(str):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.phonemes = [x for x in iter_api_phoneme(value)]  # c'est ça qui est pas top

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index >= len(self.phonemes):
            raise StopIteration
        result = self.phonemes[self._index]
        self._index += 1
        return result

#TODO: idem pas super optimisé tout ça
class APISyllStr(str):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.phonemes = [x for x in iter_api_syllabes(value)]  # idem c'est ça qui est pas top

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index >= len(self.phonemes):
            raise StopIteration
        result = self.phonemes[self._index]
        self._index += 1
        return result  

#####autre version, qui marche pas; elle essaie d'utiliser dircetment le generator
#pour ne pas stocker toutes les valeurs d'un coup. Je pense c'est useless de toutes façons
class cStr(str):
    def __init__(self, value):
        super().__init__()
        self.value = value
    def chunkify(self):
        print("pas là !!!!")
        for x in self.value:
            yield x

class GranStr(cStr):
    def __iter__(self):
        self.chunks = self.chunkify()
        return self
    
    def __next__(self):
        return next(self.chunks)

class PhonStr(GranStr):
    def chunkify(self):
        for s in self.value.split("."):
            yield s

class SyllStr(GranStr):
    def chunkify(self):
        print("ici")
        length = len(self.value)
        i = 0
        while i < length:
            cat = unicodedata.category(self.value[i])
            # skip points
            if cat == 'Po':
                i += 1
                continue
            if not cat == 'Ll':
                # TODO: not sure if we shall pass here...
                yield self.value[i]
            else:
                # got an accented letter
                if i < length - 1 and unicodedata.category(self.value[i+1]) == 'Mn':
                    yield self.value[i:i+2]
                    i += 1
                else:
                    # got a "simple" letter
                    yield self.value[i]
            i += 1

#</useless>
########################################


class Word_API_Phoneme_Node[word_info_t]:
    """
    classe-node stockant des mots-tuples, selon leur phonemes
    ex: "be.ne.dik.sjɔ̃" -> ("b","e","n","e","d","i","k","s","j","ɔ̃")
    """
    def get_key(self, obj:word_info_t):
        return APIPhonStr(obj.api)

class Word_API_Phoneme_Node[word_info_t]:
    """
    classe-node stockant des mots-tuples, selon leur phonemes
    ex: "be.ne.dik.sjɔ̃" -> ("be","ne","dik","sjɔ̃")
    """
    def get_key(self, obj:word_info_t):
        return APISyllStr(obj.api)



# ci-dessous, dynamic class factory, pas forcément super utile, du coup ? 
# la version ci-dessus est bien


"""
la meme modifiée
"""

class DynamicClassFactory:
    def __init__(self, base_class):
        self.base_class = base_class
        self.created_classes = {}


    def create_subclass(self, custom_method, data_class):
        method_name = custom_method.__name__
        if method_name not in self.created_classes:
            class_name = f"DynamicSubClass_{method_name}"
            new_class = type(class_name, (self.base_class,), {"get_key": custom_method})
            self.created_classes[method_name] = new_class
        return self.created_classes[method_name]

# Créer une instance de la fabrique
factory = DynamicClassFactory(Node)

def get_identity_key(self, obj):
    return obj

def get_ort_key(self, obj):
    return obj.mot

def get_api_key(self, obj):
    return obj.api

StrTree = factory.create_subclass(get_identity_key, str)
OrtTree = factory.create_subclass(get_ort_key, word_info_t)
ApiTree = factory.create_subclass(get_api_key, word_info_t)

def test1():
    root = StrTree()
    def test_insert(word):
        n = root.insert(word)
        msg = f"{n} | {root.search(word)}"
        print(msg)
        # if n!= root.search(word):
        #     return n
        assert n == root.search(word)
        print(f"inséré: {word}")
    
    test_insert("banque") # premier insert - pousse D
    test_insert("banc") # fork A
    test_insert("banques") # pousse D
    test_insert("banquets") #fork A
    # test_insert("banquet") #split 
    return root

def test2(inc=500):
    f=open("data/gramm.dmp", "rb")
    gramm=pickle.load(f)
    f.close()

    # f=open("data/gnode_tree.dmp", "rb")
    # root=pickle.load(f)
    # f.close()
    root = OrtTree()
    # GNODE_DEBUG=True
    CNT=0
    print("debut")
    for x in gramm:
        for y in gramm[x]:
            CNT+=1
            if CNT%inc==0:
                print(f"{CNT} {y.mot}")
            # assert isinstance(y, str), f"{type(y)}"
            try:
                w = root.insert(y)
            except AssertionError as e:
                print(y)
                print(y.mot)
                raise e
            # w.data.append(y)
    return (gramm, root)
