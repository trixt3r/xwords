import pickle

import node
from dico import Dico
from sortedlist import SortedList


def test_node(node_impl, wit_fname):
    idx = node.Index(data_initializer=dict, node_impl=node_impl)
    with open(wit_fname, "rb") as f:
        wit_list = pickle.load(f)
    for w in wit_list:
        idx.addWord(w.mot, w)
    return idx


def test_Dico_iter():
    dico = Dico({"bonjour": ["hello", 'salut'], "au revoir": ["bye bye", "ciao"]})
    for x in dico:
        print(x)


def test_SortedList():
    with open("data/gramm.dmp", "rb") as f:
        dico = Dico(pickle.load(f))
    l1 = SortedList(sort_key=lambda x: (x.mot, x.nature))
    for x in dico:
        l1.append(x)
    print(l1[12145])
    print(l1[12146])
