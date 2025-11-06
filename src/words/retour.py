import os
import numpy as np

os.environ["PATH"] += os.pathsep + 'C:/Users/HP/graphviz_bin'
from pprint import pprint

import pickle
# from graphviz import Source
from node import *
idx=None
if os.path.exists('data/test_index.dmp'):
    with open('data/test_index.dmp', "rb") as f:
        idx = pickle.load(f)
else:
    with open('src/words/data/test_index.dmp', "rb") as f:
        idx = pickle.load(f)
root = idx.root_node

def parcours_arbre_data_liste(node):
    fifo = [node]
    while len(fifo) > 0:
        c_node = fifo.pop()
        if c_node.data is not None:
            for w in c_node.data:
                yield w
        next = [c for c in c_node.children ]
        next.sort(reverse=True)
        for c in next:
            fifo.append(c_node.children[c])

def parcours_arbre_data_liste_filter(node,node_filter=lambda w:True,data_filter=lambda w: True):
    fifo = [node]
    while len(fifo) > 0:
        c_node = fifo.pop()
        if c_node.data is not None:
            for w in c_node.data:
                if data_filter(w):
                    yield w
        next = [c for c in c_node.children if node_filter(c_node.children[c])]
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
    """
    ArboComp (Arborescence Composer) - A class for analyzing and managing tokenized hierarchical data.
    
    This class tokenizes string values into component parts, tracks token usage patterns across 
    different positions, and provides analysis of token distribution. It's particularly useful 
    for analyzing linguistic patterns like grammatical categories that can be decomposed into 
    sub-components (e.g., "flex-verb" -> ["flex", "verb"]).
    
    The class maintains:
    - A vocabulary of unique tokens encountered
    - A list of original values that were tokenized
    - Statistics about token position patterns and usage
    """
    
    def __init__(self, words:set[str], tokenizer= lambda x:x.split('-'), joiner=lambda x: '-'.join(x)):
        """
        Initialize the ArboComp analyzer.
        
        Args:
            tokenizer (callable): Function to split a string into tokens. 
                                Default splits on '-' character.
            joiner (callable): Function to rejoin tokens back into a string.
                              Default joins with '-' character.
        """
        self.tokenizer = tokenizer  # Function to break strings into component tokens
        self.joiner = joiner        # Function to reconstruct strings from tokens
        self.tokens = []            # Master list of all unique tokens encountered
        self.values = []            # List of all original string values added
        self.values_max_token_count = 0          # Maximum number of tokens in any single value
        for n in words:
            self.add_tokens(n)

    def comp_tokens(self, value) -> list[int]:
        """
        Convert a string value to a list of token indices.
        
        Tokenizes the input value and returns the indices of each token 
        in the master tokens list. Updates max_depth if this value has 
        more tokens than previously seen.
        
        Args:
            value (str): The string value to tokenize and convert to indices
            
        Returns:
            list[int]: List of indices corresponding to each token in the value
            
        Example:
            If tokens = ["flex", "verb", "nom"] and value = "flex-verb",
            returns [0, 1]
        """
        tokens = self.tokenizer(value)
        ret = list()
        for t in tokens:
            ret.append(self.tokens.index(t))
        self.values_max_token_count = max(self.values_max_token_count, len(ret))
        return ret

    def add_tokens(self, value: str):
        """
        Add a new string value to the analyzer and extract its tokens.
        
        Tokenizes the input value and adds any new tokens to the master 
        tokens list. The value itself is added to the values list.
        
        Args:
            value (str): The string value to add and analyze
            
        Raises:
            AssertionError: If the value has already been added to prevent duplicates
            
        Example:
            add_tokens("flex-verb") will:
            1. Add "flex-verb" to self.values
            2. Add "flex" and "verb" to self.tokens (if not already present)
        """
        assert value not in self.values, f"la valeur {value} a déjà été ajoutée"
        self.values.append(value)
        tokens = self.tokenizer(value)
        # Extract and register each individual token
        for t in tokens:
            if t not in self.tokens:
                self.add_token(t)
    
    def add_token(self, t):
        """
        Add a single token to the master tokens list.
        
        Args:
            t (str): The token to add to the vocabulary
        """
        self.tokens.append(t)
    
    def decomp_token(self, value: list[int]) -> str:
        """
        Convert a list of token indices back to the original string representation.
        
        Takes a list of indices and reconstructs the original string by 
        looking up each token and joining them with the joiner function.
        
        Args:
            value (list[int]): List of token indices to convert back to string
            
        Returns:
            str: The reconstructed string value
            
        Example:
            If tokens = ["flex", "verb", "nom"] and value = [0, 1],
            returns "flex-verb"
        """
        ret = list()
        for v in value:
            ret.append(self.tokens[v])
        return self.joiner(ret)

    def analyze(self):
        """
        Perform comprehensive analysis of token usage patterns across all values.
        
        This method analyzes how tokens are distributed across positions and computes
        various statistics about token usage patterns. For each token, it tracks:
        
        - Position-specific counts (how often it appears at each position 0, 1, 2, ...)
        - INIT count: how often the token appears at the start of values
        - FIN count: how often the token appears at the end of values  
        - STATE bitmask: which positions the token can appear in (as a bit field)
        
        Returns:
            tuple: A tuple containing:
                - _counters (dict): Maps each token to a list containing:
                    [pos0_count, pos1_count, ..., posN_count, init_count, fin_count, state_bitmask]
                - token_by_état (dict): Maps each unique state bitmask to list of tokens with that state
                
        The state bitmask uses powers of 2 to encode positions:
        - Position 0: bit 0 (value 1)
        - Position 1: bit 1 (value 2) 
        - Position 2: bit 2 (value 4)
        - etc.
        
        Special derived sets computed internally:
        - finaux: tokens that ONLY appear at the end of values
        - initiaux: tokens that ONLY appear at the start of values
        """
        # Initialize counters for each token: [pos_counts..., init_count, fin_count, state_bitmask]
        counters = {}
        self.tokens.sort()
        self.values.sort()
        for tok in self.tokens:
            counters[tok] = [0] * (self.values_max_token_count + 1 + 1 + 1)
        
        # Define special indices in the counter arrays
        INIT = self.values_max_token_count      # Index for start-of-value count
        FIN = self.values_max_token_count + 1   # Index for end-of-value count  
        STATE = self.values_max_token_count + 2 # Index for position bitmask
        
        # Analyze each value and update token statistics
        for v in self.values:
            tokens = self.tokenizer(v)
            for i, token in enumerate(tokens):
                # Count occurrence at this position
                counters[token][i] += 1
                
                # Track if this token appears at the end of this value
                if i == len(tokens) - 1:
                    counters[token][FIN] += 1
                    
                # Track if this token appears at the start of this value
                if i == 0:
                    counters[token][INIT] += 1
                    
                # Update the state bitmask to include this position
                counters[token][STATE] = counters[token][STATE] | pow(2, i)
        
        # Compute derived statistics
        for k, v in counters.items():
            pass
            
        # Find tokens that appear ONLY at the end (fin_count equals total_count)
        finaux = list({k for k, v in counters.items() if v[FIN] == sum(v[:self.values_max_token_count])})

        # Find tokens that appear ONLY at the start (init_count equals total_count)
        initiaux = list({k for k, v in counters.items() if v[INIT] == sum(v[:self.values_max_token_count])})

        # Collect all unique state patterns (position bitmasks)
        états = set(v[STATE] for k, v in counters.items())
        
        # Group tokens by their state pattern
        token_by_état = {e: [k for k, v in counters.items() if v[STATE] == e] for e in états}

        # MAP token_state (1,2,3,6) TO token count for this state
        token_count_by_état = {counters[k][-1]:len([t for t in counters if counters[t][-1]==counters[k][-1]]) for k in counters}
        return counters, token_by_état,initiaux,finaux
    
    class arbo_state(object):
        def __init__(self, token, positions:list[int], start_of_value:int=0, end_of_value:int=0):
            self.token = token
            
            self.bitmask = sum(1 << p for p in positions)
            # self.start_of_value = start_of_value
            # self.end_of_value = end_of_value
            self.valid_tokens = set()
            self.position_counters={}
            self.start_counter = start_of_value
            self.end_counter = end_of_value

        def add_token(self, token:str):
            self.valid_tokens.add(token)
        
        def inc_counters(self,pos,at_start,at_end):
            if pos not in self.position_counters:
                self.position_counters[pos]=0
                self.bitmask |= (1 << pos)
            self.position_counters[pos]+=1
            if at_start:
                self.start_counter+=1
            if at_end:
                self.end_counter+=1
        
        def __repr__(self):
            return f"ArboState(token={self.token}, bitmask={self.bitmask}, start_count={self.start_counter}, end_count={self.end_counter}, positions={self.position_counters})"

    def analyze_new(self):
        """
        Perform comprehensive analysis of token usage patterns across all values.
        
        This method analyzes how tokens are distributed across positions and computes
        various statistics about token usage patterns. For each token, it tracks:
        
        - Position-specific counts (how often it appears at each position 0, 1, 2, ...)
        - INIT count: how often the token appears at the start of values
        - FIN count: how often the token appears at the end of values  
        - STATE bitmask: which positions the token can appear in (as a bit field)
        
        Returns:
            tuple: A tuple containing:
                - _counters (dict): Maps each token to a list containing:
                    [pos0_count, pos1_count, ..., posN_count, init_count, fin_count, state_bitmask]
                - token_by_état (dict): Maps each unique state bitmask to list of tokens with that state
                
        The state bitmask uses powers of 2 to encode positions:
        - Position 0: bit 0 (value 1)
        - Position 1: bit 1 (value 2) 
        - Position 2: bit 2 (value 4)
        - etc.
        
        Special derived sets computed internally:
        - finaux: tokens that ONLY appear at the end of values
        - initiaux: tokens that ONLY appear at the start of values
        """
        # Initialize counters for each token: [pos_counts..., init_count, fin_count, state_bitmask]
        self.tokens.sort()
        self.values.sort()

        counters_new = {tok:ArboComp.arbo_state(token=tok, positions=[], start_of_value=0, end_of_value=0) for tok in self.tokens}
        counters = {tok: [0] * (self.values_max_token_count + 1 + 1 + 1) for tok in self.tokens}
        # for tok in self.tokens:
        #     counters[tok] = [0] * (self.values_max_token_count + 1 + 1 + 1)
        #     counters_new[tok] = ArboComp.arbo_state(token=tok, positions=[], start_of_value=0, end_of_value=0)

        
        # Define special indices in the counter arrays
        INIT = self.values_max_token_count      # Index for start-of-value count
        FIN = self.values_max_token_count + 1   # Index for end-of-value count  
        GROUP = self.values_max_token_count + 2 # Index for position bitmask
        
        # Analyze each value and update token statistics
        for v in self.values:
            tokens = self.tokenizer(v)
            for i, token in enumerate(tokens):
                # Count occurrence at this position
                counters_new[token].inc_counters(pos=i, at_start=(i==0), at_end=(i==len(tokens)-1))
                
                counters[token][i] += 1
                # Track if this token appears at the end of this value
                if i == len(tokens) - 1:
                    counters[token][FIN] += 1
                    
                # Track if this token appears at the start of this value
                if i == 0:
                    counters[token][INIT] += 1
                    
                # Update the state bitmask to include this position
                counters[token][GROUP] = counters[token][GROUP] | pow(2, i)
        # counters = {tok:{k2:v2 for k2,v2 in v.items() if v2!=0} for tok,v in counters.items()}
        # Compute derived statistics
        for token, pos_counter in counters.items():
            assert (counters_new[token].position_counters == {i: pos_counter[i] for i in range(self.values_max_token_count) if pos_counter[i]!=0}), f"mismatch for token {token}"
            assert counters_new[token].start_counter == pos_counter[INIT], f"mismatch for token {token}"
            assert counters_new[token].end_counter == pos_counter[FIN], f"mismatch for token {token}"
            # assert counters_new[token].group_counter == pos_counter[GROUP], f"mismatch for token {token}"
            pass
            
        # # Find tokens that appear ONLY at the end (fin_count equals total_count)
        # finaux = list({k for k, v in counters.items() if v[FIN] == sum(v[:self.values_max_token_count])})

        # # Find tokens that appear ONLY at the start (init_count equals total_count)
        # initiaux = list({k for k, v in counters.items() if v[INIT] == sum(v[:self.values_max_token_count])})

        # Collect all unique state patterns (position bitmasks)
        groups = list(set(v[GROUP] for k, v in counters.items()))
        groups.sort()
        grp2tokens = [[k for k, v in counters.items() if v[GROUP] == e] for e in groups]
        del groups
        
        token2group = {t:gid for gid in range(len(grp2tokens)) for t in grp2tokens[gid]}
        
        # matrix = self.create_path_matrix(token2group, len(grp2tokens))
        # print(matrix)
        # toks = {t:set([tok for w in self.values for tok in self.tokenizer(w) if t!=tok and t in self.tokenizer(w)]) for t in self.tokens}
        # matrix = create_tokens_matrix(toks)
        value2groups = ((v,[token2group[t] for t in self.tokenizer(v)]) for v in self.values)
        collisions = {value:groups for value,groups in value2groups if not len(set(groups))==len(groups)}
        isolated = set()
        # plusieurs tokens à la meme position, impossible. Repartitionner
        while not len(collisions) == 0:
            value, grps = collisions.popitem()
            fault_grps = set([g for g in grps if grps.count(g)>1])
            if len(fault_grps)==1:
                #il faut isoler les tokens de value, donc len(tokens(value))-1 nouveaux groupes
                #NOTE on en garde un dans le groupe d'origine, ici le premier qui vient
                for i,tok in enumerate(self.tokenizer(value)):
                    if i==0:
                        continue
                    # new_groups.append([tok])
                    if token2group[tok] in fault_grps:
                        #créer un nouveau groupe
                        new_group_id = len(grp2tokens)
                        grp2tokens.append([tok])
                        grp2tokens[token2group[tok]].remove(tok)
                        token2group[tok] = new_group_id
                        isolated.add(tok)

            token2group = {t:gid for gid in range(len(grp2tokens)) for t in grp2tokens[gid]}
            value2groups = ((v,[token2group[t] for t in self.tokenizer(v)]) for v in self.values)
            collisions = {value:states for value,states in value2groups if not len(set(states))==len(states)}
            
        assert len(collisions) == 0

        for i,grp in enumerate(grp2tokens):
            print(f"grp {i} :  {len(grp2tokens[i])} tokens {(len(grp2tokens[i])+1).bit_length()} bits")
            print(f"{grp2tokens[i]}")
        
        group_paths = {word:tuple([token2group[tok] for tok in self.tokenizer(word)]) for word in self.values}
        unique_paths = set(group_paths[v] for v in self.values)
        path2tokens = {p:[ word for word, path in group_paths.items() if path==p] for p in unique_paths}
        # matrix = self.create_path_matrix(token2group, len(grp2tokens))
        # for token in isolated:
        #     gid = token2group[token]
        #     matrix[gid,gid]=1
        # print(matrix)
        # for       
        return grp2tokens
        

    def create_path_matrix(self,token2group, num_groups):
        group_paths = {word:tuple([token2group[tok] for tok in self.tokenizer(word)]) for word in self.values}
        unique_paths = set(group_paths[v] for v in self.values)
        matrix = np.zeros((num_groups, num_groups), dtype=int)
        for p in unique_paths:
            for gid in p:
                for gid2 in p:
                    matrix[gid,gid2] = 1
                    matrix[gid2,gid] = 1
        return matrix

def create_tokens_matrix(toks:dict[str,set[str]]):
    token_list = sorted(list(toks.keys()))
    matrix = np.zeros((len(toks), len(toks)), dtype=int)
    for t in toks:
        gid = token_list.index(t)
        for t2 in toks[t]:
            gid2 = token_list.index(t2)
            matrix[gid,gid2]=1
            matrix[gid2,gid]=1
    return matrix

# from pprint import pprint
# natures = {'pronom-rel', 'flex-verb', 'nom', 'flex-art-déf', 'var-typo', 'adj-dém', 'part', 'flex-art-indéf', 'flex-adj-pos', 'adj-indéf', 'prénom', 'nom-pr', 'pronom-pers', 'adj', 'adv', 'verb', 'art-part', 'flex-adj', 'flex-adj-indéf', 'onoma', 'adj-int', 'conj-coord', 'flex-adj-dém', 'adv-int', 'flex-nom', 'interj', 'symb', 'flex-pronom-dém', 'adv-rel', 'suf', 'pronom-dém', 'flex-pronom-rel', 'flex-pronom-pers', 'phr', 'flex-prép', 'lettre', 'adj-num', 'pronom-int', 'prép', 'flex-pronom-int', 'adj-rel', 'adj-pos', 'flex-adv', 'pronom', 'nom-fam', 'pronom-indéf', 'flex-pronom-indéf', 'art-indéf', 'flex-adj-int', 'art-déf', 'conj'}

# arbo = ArboComp()
# for n in natures:
#     arbo.add_tokens(n)

# for n in arbo.values:
#     print(n , arbo.comp_tokens(n))

# pprint(arbo.tokens)

# for n in arbo.values:
#     print(n , arbo.comp_tokens(n))

# counters, token_by_état,initiaux,finaux = arbo.analyze()

# solos=[x for x in initiaux if x in finaux]
# endings = [x for x in finaux if x not in solos]




# counters["indéf"][-1]==4+2 

datas = collect_and_count_attribute_values(root, 'nature')

# def flagiz(values: list[int]) -> int:
#     ret = 0
#     offset=0
#     for v in values:
#         l = v.bit_length()
#         ret = v<<offset | ret
#         offset+=l
#     return ret

# #NOTE fausse route
# def testo():
#     ret = {}
#     for nature in arbo.values:
#         h = nature.split('-')
#         current = []
#         for t in h:
#             for i,state in enumerate(token_by_état):
#                 if t in token_by_état[state]:
#                     current.append(token_by_état[state].index(t))
#                     break
#             ret[nature] = current
#     return ret

# #NOTE fausse route
# def testo2(token_by_état, ordre):
#     ret = {}
#     for nature in arbo.values:
#         h = nature.split('-')
#         current = []
#         i = 0
#         while i < len(h):
#             for j,o in enumerate(ordre):
#                 state = token_by_état[o]
#                 if h[i] in state:
#                     current.append(state.index(h[i]))
#                     i+=1
#                     break
#                 else:
#                     if j>i<len(h):
#                         current.append(-1)
#             ret[nature] = current
#     return ret



