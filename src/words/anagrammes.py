#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import string
import math
import cw
import node
import pickle
ref_str = "exit"


def check_anagramme(ref_string, test_string):
    """Check if test string is an anagramm of ref_string"""
    s1 = {}
    s2 = {}
    ref_string = ref_string.lower()
    test_string = test_string.lower()
    for c in ref_string:
        if not c in string.ascii_lowercase:
                continue
        if c in s1:
            s1[c] = s1[c] + 1
        else:
            s1[c] = 1
            s2[c] = 0
    for c in test_string:
        if not c in string.ascii_lowercase:
                continue
        if c in s2:
            s2[c] = s2[c] + 1
        else:
            s2[c] = 1
    if not s1 == s2:
        ret = {}
        for c in s1:
            if c in s2 and s1[c] != s2[c]:
                ret[c] = s1[c] - s2[c]
        for c in s2:
            if c not in s1:
                ret[c] = -s2[c]
        return ret
    return {}


# def first_check(filename):
#     canonical = {}
#     f = open(filename, "r")
#     for l in f:
#         #l = f.readline()
#         l = l[:-1]
#         canon = cw.getCanonical(l)
#         if canon in canonical:
#             canonical[canon] = canonical[canon] + 1
#         else:
#             canonical[canon] = 1
#     f.close()
#     return canonical


def init_dict(dico_txt="liste.de.mots.francais.frgut.utf8.txt"):
    canonical = {}
    f = io.open(dico_txt, "r", encoding="utf-8")
    c = 0
    for l in f:
        #l = f.readline()
        l = l[:-1]
        w = l
        canon = cw.getCanonical(l)
        if not (canon in canonical):
            canonical[canon] = [w]
        else:
            canonical[canon].append(w)
        c = c + 1
        if c % 1000 == 0:
            print (c)
    f.close()
    return canonical


def binomial_coeff(x, y):
    """Return binomial coefficient of x and y"""
    if y == x:
        return 1
    elif y == 1:
        return x
    elif y > x:
        return 0
    a = math.factorial(x)
    b = math.factorial(y)
    c = math.factorial(x - y)
    return a // (b * c)


def list_writeable_words(word, index):
    cws = index.rootNode.explore(cw.getCanonical(word))
    words = []
    for cw1 in cws:
        words += index.dico[cw1]
    return words


# def explore_sentence(sentence, chosen_words=[], max_rest=6):
#     cw_s = cw.getCanonical(sentence)
#     #constructiong cw for chosen words
#     chosen = ""
#     for w in chosen_words:
#         chosen = chosen + w
#     chosen = cw.getCanonical(chosen)
#     #removing chosen characters from sentence
#     cw_s = cw.difference(chosen, cw_s)
#     words = index.rootNode.explore(cw_s)
#     ana = {}
#     for w in words:
#         diff = cw.difference(w, cw_s)
#         anas = index.rootNode.explore(diff)
#         ana_w = []
#         for w2 in anas:
#             if len(sentence) - len(w) - len(w2) < max_rest:
#                 ana_w.append({'word': w2, 'rest': cw.difference(w2, diff)})
#         ana[w] = ana_w
#     return ana


# def search_anagram(cw_key, canonical_words):
#     anagrams = []
#     for cw1 in list(canonical_words.keys()):
#         if cw.can_write(cw1, cw_key):
#             r = cw.intersect(cw_key, cw1)
#             if r in canonical_words:
#                 anagrams.append(cw1)
#     return anagrams


def initDico():
    f = open('data/dico_mots.dmp', 'r')
    dico = pickle.load(f)
    f.close()
    return dico


def initTree():
    f = open('data/tree_v0.1.dmp', 'r')
    rootNode = pickle.load(f)
    f.close()
    return rootNode


dico_filename = "data/dico_mots.dmp"
root_filename = "data/tree_v0.1.dmp"
# index = node.Index(dico_filename, root_filename)


def word_value_classic(w):
    w = cw.sanitize_word(w)
    v = 0
    coeff = 1
    for i in range(0, len(w)):
        c = ord(w[-(i+1)]) - 96 # ord('a') + 1
        v += coeff * c
        coeff *= 26
    return v
