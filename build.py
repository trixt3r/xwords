
import pickle
import random
from collections import defaultdict
import os
here = os.path.dirname(__file__)

from node import Index, Node
import cw as cwapi
from words_tuple import word_t, word_info_t, fusion_word_info_t
from verb import init_verb_class
import GNode


def loadGramm(file="data/gramm.dmp"):
    with open(os.path.join(here,file), "rb") as f:
        return pickle.load(f)


def createIndex(gramm=None):
    if gramm is None:
        gramm = loadGramm()
    idx = Index(dict)
    for w in gramm:
        idx.addWord(w, gramm[w])
    return idx


def add_dumy_words(index, wlist):
    i = 0
    for w in wlist:
        n = index.search(w)
        if (len(n.cw) < len(w)) or (n.data is not None and w not in n.data):
            index.addWord(w, word_info_t(nature="*", api="*", genre="*", nbr="*", mot=w))
        i += 1
        if i % 100 == 0:
            print("%d/%d : %s" % (i, len(wlist), w))


def createIndex2():
    with open("data/liste_asseptisee.dmp", "rb")as f:
        wlist = pickle.load(f)
        idx = Index(dict)
        for w in wlist:
            idx.addWord(w, w)
        return idx


def create_test_data_set(dico, count=1000):
    words = {}
    keys = [x for x in dico.keys()]
    while(len(words) < count):
        k = keys[random.randrange(0, len(keys))]
        words[k] = dico[k]
    return words


def get_anagram_test_list():
    return ["marié", "mare", "marie", "aimer", "rami", 'ramie', 'mari', "ami", "épilogue", "bouffon"]


def get_anagram_test_dico():
    li = get_anagram_test_list()
    dic = {}
    for w in li:
        dic[w] = w
    return dic


def create_index(dico, data_initializer=list):
    init_verb_class()
    index = Index(data_initializer)
    for w in dico:
        index.addWord(w, dico[w])
    return index


def create_tree_with_anagrammes():
    root = Node()
    wl = get_anagram_test_list()
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


# fusionne les mots ayant la même nature et la même orthographe
def compress_gramm(gramm):
    new_gramm = {}
    for w in gramm:
        new_ = defaultdict(list)
        for f in gramm[w]:
            new_[f.nature].append(f)
            for nat in new_:
                flex = new_[nat][0]
                errors = []
                for i in range(1, len(new_[nat])):
                    try:
                        flex = fusion_word_info_t(flex, new_[nat][i])
                    except AssertionError:
                        errors.append(new_[nat][i])
                new_[nat] = [flex] + errors
        new_list = []
        new_ = [x for x in new_.values()]
        for wl in new_:
            new_list += wl
        new_gramm[w] = new_list
    return new_gramm


def track_gnode_insert_bug(gramm, words):
    wit_root = GNode.WITNode()
    for w in words:
        try:
            wit_root.addData(gramm[w])
        except Exception as e:
            print("Exception: e" % e)
            pass
    return wit_root


def track_incomplete_words(words):
    incomplete = []
    for w in words:
        for f in w:
            if f.nature is None or f.nature == "":
                incomplete.append(f)
                continue
            if f.mot is None or f.mot == "" or f.api is None or f.api == "":
                incomplete.append(f)
                continue
            if f.nature != "flex-verb":
                if f.nbr not in ["P", "S"] or f.genre not in ["M", "F"]:
                    incomplete.append(f)
                    continue
    return incomplete


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
