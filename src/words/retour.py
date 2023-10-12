import os
os.environ["PATH"] += os.pathsep + 'C:/Users/HP/graphviz_bin'
from pprint import pprint

import pickle
from graphviz import Source
from node import *
idx=None
with open('data/test_index.dmp', "rb") as f:
    idx = pickle.load(f)

root = idx.root_node

def translate_range(value, from_min, from_max,to_min,to_max):
    # Figure out how 'wide' each range is
    leftSpan = from_max - from_min
    rightSpan = to_max - to_min
    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - from_min) / float(leftSpan)
    # Convert the 0-1 range into a value in the right range.
    return int(to_min + (valueScaled * rightSpan))

def generate_graphviz(node, fname="data/test_graph.txt", depth=4):
    fifo = [(node,'')]
    file = open(fname, "w")
    file.write("graph G {\n")
    file.write("\t\toverlap = false;\n")
    max_children=19
    max_words=15
    while len(fifo) > 0:
        c_node,path = fifo.pop()

        
        nb_children=len(c_node.children)
        nb_words=0
        if c_node.data is not None:
            nb_words = len(c_node.data)
        # if c_node.data is not None and len(c_node.data)>max_words:
        #     max_words = len(c_node.data)
        # if c_node.children is not None and len(c_node.children)>max_children:
        #     max_children = len(c_node.children)
        g_node_color = translate_range(nb_children,0,max_children,0,255) * 65536 +\
                        translate_range(nb_words,0,max_words,0,255)
        g_node_name = path
        if path=='':
            g_node_name = "root"
        # declare node
        ftd_color=hex(g_node_color)[2:]
        while len(ftd_color)<6:
            ftd_color+="0"
        file.write(f'\t\t"{g_node_name}" [color="#{ftd_color}"]\n')
        #declare transitions
        if depth!=-1 and len(path)<depth-1:
            file.write(f'\t\t"{g_node_name}" -- ')
            file.write('{')
            for c in c_node.children:
                child = c_node.children[c]
                file.write(f'{child.cw}; ')
            file.write('}')
            file.write("\n")

            next = [c for c in c_node.children]
            next.sort(reverse=True)
            for c in next:
                # print(f"path = {path}{c}")
                fifo.append((c_node.children[c],path+c))
    print(f"{max_children} {max_words}")
    file.write("}\n")
    file.close()
    return
graph_file="data/test_graph.txt"
# twopi -Tpng -O -Gsize=20,20 -Gdpi=1000 test_graph.txt
# s = Source.from_file(graph_file)
# s.view()



######################################################################################################
# LES GRAPHES N'ONT PAS DONNE GRAND CHOSE CAR ILS SONT BIEN TROP COMPLEXES ET GRAPHVIZ PLANTE
######################################################################################################

def parcours_arbre_data_liste(node):
    fifo = [node]
    while len(fifo) > 0:
        c_node = fifo.pop()
        if c_node.data is not None:
            for w in c_node.data:
                yield w
        next = [c for c in c_node.children]
        next.sort(reverse=True)
        for c in next:
            fifo.append(c_node.children[c])

def collect_attribute_values(node,attr):
    values = set()
    for w in parcours_arbre_data_liste(node):
        attr_value = w.__getattribute__(attr)
        try:
            values.add(attr_value)
        except TypeError as error:
            # assert not isinstance(attr_value, dict), f"ça commence à être trop compliqué comme structure"
            assert isinstance(attr_value,(set,list)), f"ça commence à être trop compliqué comme structure"
            for v in attr_value:
                values.add(v)
    return values

def collect_and_count_attribute_values(node,attr):
    values = dict()
    for w in parcours_arbre_data_liste(node):
        attr_value = w.__getattribute__(attr)
        try:
            if attr_value in values:
                values[attr_value]+=1
            else:
                values[attr_value]=1
        except TypeError as error:
            # assert not isinstance(attr_value, dict), f"ça commence à être trop compliqué comme structure"
            assert isinstance(attr_value,(set,list)), f"ça commence à être trop compliqué comme structure"
            for v in attr_value:
                if v in values:
                    values[v]+=1
                else:
                    values[v]=1
    return [(x,values[x]) for x in values]

def hierarchise_set(values, sep="-"):
    base_elts = set()
    max_depth = 0
    for v in values:
        elts = v.split(sep)
        max_depth=max(max_depth,len(elts))
        for e in elts:
            base_elts.add(e)
# 
    base_elts = list(base_elts)
    base_elts.sort()
# 
    # _classes = []
    # for i in range(0,max_depth):
    #     _classes.append(list())
    _classes = [[]]*max_depth
    # print(_classes)
#   
    # pr chq sbl, compter le nombre de fois où il apparaît à chaque position
    _counters= {}
    for e in base_elts:
        _counters[e]= [0]*max_depth
    for v in values:
        v_elts = v.split(sep)
        for i in range(0,len(v_elts)):
            _counters[v_elts[i]][i]+=1
    
    for v in values:
        v_elts = v.split(sep)
        new_value = sep.join([str(base_elts.index(x)) for x in v_elts])
        tab = _classes[len(v_elts)-1]
        tab.append(new_value)
# 
    return base_elts, _classes,_counters

def trad(mot, elts, classes, sep=" "):
    ret = ""
    word_elts = mot.split(sep)
    print(f"len = {len(word_elts)}")
    print(word_elts)
    return sep.join([elts[int(e)] for e in word_elts])


def search_for_lex(node, lex):
    for w in parcours_arbre_data_liste(node):
        if lex in w.lex:
            yield w


def search_with_filter(node, filter):
    for w in parcours_arbre_data_liste(node):
        if filter(w):
            yield w

from operator import itemgetter, attrgetter

def split_list(l, filter):
    y=[]
    n=[]
    for e in l:
        if filter(e):
            y.append(e)
        else:
            n.append(e)
    return y,n

class ArboComp(object):
    def __init__(self, tokenizer= lambda x:x.split('-'), joiner=lambda x: '-'.join(x)):
        self.tokenizer = tokenizer
        self.joiner = joiner
        self.tokens=[]
        self.values=set()
        self.max_depth=0

    def comp_tokens(self,value):
        self.values.add(value)
        tokens=self.tokenizer(value)
        ret=list()
        for t in tokens:
            if t not in self.tokens:
                self.add_token(t)
            ret.append(self.tokens.index(t))
        self.max_depth=max(self.max_depth,len(ret))
        return ret
    
    def add_tokens(self, value):
        self.comp_tokens(value)
    
    def add_token(self, t):
        self.tokens.append(t)
    
    def decomp_token(self,value):
        ret = list()
        for v in value:
            ret.append(self.tokens[v])
        return self.joiner(ret)

    def analyze(self):
        # pr chq sbl, compter le nombre de fois où il apparaît à chaque position
        _counters= {}
        self.tokens.sort()
        self.values.sort()
        for e in self.tokens:
            _counters[e]= [0] * (self.max_depth + 1 + 1 + 1)
        INIT = self.max_depth
        FIN = self.max_depth+1
        STATE = self.max_depth+2
        
        for v in self.values:
            v_elts = self.tokenizer(v)
            for i, elt in enumerate(v_elts):
                _counters[elt][i]+=1
                if i== len(v_elts)-1:
                    _counters[elt][FIN]+=1
                if i==0:
                    _counters[elt][INIT]+=1
                _counters[elt][STATE] = _counters[elt][STATE] | pow(2,i)
        for k,v in _counters.items():
            pass
        finaux = {k for k,v in _counters.items() if v[FIN]==sum(v[:self.max_depth])}
        initiaux = {k for k,v in _counters.items() if v[INIT]==sum(v[:self.max_depth])}
        états = set(v[STATE] for k,v in _counters.items())
        token_by_état = {e:[k for k,v in _counters.items() if v[STATE]==e] for e in états}
        return _counters, token_by_état

natures = {'pronom-rel', 'flex-verb', 'nom', 'flex-art-déf', 'var-typo', 'adj-dém', 'part', 'flex-art-indéf', 'flex-adj-pos', 'adj-indéf', 'prénom', 'nom-pr', 'pronom-pers', 'adj', 'adv', 'verb', 'art-part', 'flex-adj', 'flex-adj-indéf', 'onoma', 'adj-int', 'conj-coord', 'flex-adj-dém', 'adv-int', 'flex-nom', 'interj', 'symb', 'flex-pronom-dém', 'adv-rel', 'suf', 'pronom-dém', 'flex-pronom-rel', 'flex-pronom-pers', 'phr', 'flex-prép', 'lettre', 'adj-num', 'pronom-int', 'prép', 'flex-pronom-int', 'adj-rel', 'adj-pos', 'flex-adv', 'pronom', 'nom-fam', 'pronom-indéf', 'flex-pronom-indéf', 'art-indéf', 'flex-adj-int', 'art-déf', 'conj'}
arbo = ArboComp()
for n in natures:
    arbo.add_tokens(n)