
import pickle

from node import Index, Node, NodeL, CNodeL
import cw as cwapi
import random
from words_tuple import word_t


def create_test_data_set(dico, count=1000):
    words = {}
    keys = [x for x in dico.keys()]
    while(len(words) < count):
        k = keys[random.randrange(0, len(keys))]
        words[k] = dico[k]
    return words


def create_index(dico, data_initializer=list):
    index = Index(data_initializer)
    for w in dico:
        index.addWord(w, dico[w])
    return index


def create_tree_with_anagrammes(cls=CNodeL):
    root = cls()
    wl = ["marié", "mare", "marie", "aimer", "rami", 'ramie', 'mari', "ami", "épilogue", "bouffon"]
    for w in wl:
        n = root.addWord(w)
        if n.data is None:
            n.data = []
        n.data.append(w)
    return root


def load_data(fname):
    f = open(fname, "rb")
    d = pickle.load(f)
    return d


def test_mem(acc):
    import time
    start = time.time()
    root = NodeL()  # 10.3% mem, environ 27,2s
    if acc is True:
        root = Node()  # 10.6% mem, environ 16,6s
    f = open("data/words_unaccented.dmp", "rb")
    wl = pickle.load(f)
    f.close()
    for w in wl:
        try:
            w = w.lower()
            root.addWord(w)
        except Exception:
            print("error at word %s" % w)
            return
    end = time.time()
    t = end - start
    print("time: %f" % t)
    return root


def update_remainings(wlist, remainings):
    for w in wlist:
        i = cwapi.binary_search(remainings, w)
        if i != -1:
            del remainings[i]


def test_contrep():
    pisser = word_t("pisser","pi.se")
    gliser = word_t("glisser", "ɡli.se")
    piscine = word_t("piscine", "pi.sin")
    glycine = word_t("glycine", "ɡli.sin")
