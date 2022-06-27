#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Canonical words module

functions to handle canonic words"""

import pickle
import unicodedata
# from operator import itemgetter
# from operator import
from bisect import bisect_left

import unidecode

# from words_tuple import word_info_t


def binary_search(container, x, lo=0, hi=None):
    hi = hi if hi is not None else len(container)
    pos = bisect_left(container, x, lo, hi)
    return (pos if (not pos == hi) and container[pos] == x else -1)


def replace_generics(word, generics):
    if isinstance(generics, list):
        generics_dict = {}
        for g in generics:
            key = g[0].upper()
            generics_dict[key] = g
        generics = generics_dict

    generic_word = ""
    for char in word:
        found = False
        for g in generics:
            if char in generics[g]:
                generic_word += g
                found = True
                break
        if not found:
            generic_word += char
    return generic_word


def test_replace_generics():
    generics = {'E': ["e", "é", "è", "ê", "ë"]}
    words = ["fête", "en-tête", "parfaite"]
    for w in words:
        print('%s %s' % (w, replace_generics(w, generics)))


def sanitize_word(word, keep_accents=False):
    word = word.lower()
    if not keep_accents:
        word = unidecode.unidecode(word)
    word = word.replace(" ", "")
    word = word.replace("\t", "")
    word = word.replace("\n", "")
    word = word.replace("-", "")
    return word


def getCanonicForm(word, keep_accents=False, generics={}):
    """Return canonic version of word
    lower word, remove white spaces and diverse types of typographics signs,
    and sorts its letters;
    accented letters shall be keeped or not"""
    word = sanitize_word(word, keep_accents)
    if not len(generics) == 0:
        replace_generics(word, generics)
    s1 = {}
    for c in word:
        if c in s1:
            s1[c] = s1[c] + 1
        else:
            s1[c] = 1
    ret_string = ""
    keys = list(s1.keys())
    keys.sort()
    for c in keys:
        ret_string += (c * s1[c])
    return ret_string


def phon_getCanonicForm(word, keep_accents=False, generics={}):
    phonemes = [p for p in iter_api_phoneme(word)]
    phonemes.sort()
    return "".join(phonemes)


def can_write(cw1, cw2):
    """Return true if all characters of cw2 are in cw1
    cw1 and cw2 must be in canonic form """
    i = 0
    i_max = len(cw1)
    founds = 0
    for c in cw2:
        found = False
        while i < i_max:
            if cw1[i] == c:
                found = True
                founds += 1
                # print "found " + c
                break
            else:
                i += 1
        if founds == len(cw2):
            return True
        if not found:
            return False
        else:
            i += 1
        if i >= i_max:
            return False


def difference(cw1, cw2):
    """Return cw2 - cw1
    cw1 and cw2 must be canonic"""
    i = 0
    result = ""
    if cw1 == '':
        return cw2
    for c in cw1:
        if i >= len(cw2):
            raise IndexError("{} {}".format(cw2, c))
        while not cw2[i] == c:
            result += cw2[i]
            i += 1
            if i >= len(cw2):
                break
        i += 1
    while i < len(cw2):
        result += cw2[i]
        i += 1
    return result


def intersect(cw1, cw2):
    """Return all characters in cw1 AND cw2
    params must be canonic"""
    diff = ""
    for c in cw1:
        if c in cw2:
            # add c in returned string
            diff += c
            # delete c from cw2
            idx = cw2.index(c)
            cw2 = cw2[0:idx] + cw2[idx + 1:]
    return diff


# TODO: gestion des liaisons
def scan_sentence_for_api(words: str, gramm: dict):
    """search all words of given string in gramm
    """
    found = []
    not_found = []
    ambiguous = {}
    for w in words.split(" "):
        if w in gramm:
            if len(set(word.api for word in gramm[w])) == 1:
                found.append(gramm[w])
            else:
                ambiguous[w] = gramm[w]
        else:
            not_found.append(w)
    return (found, ambiguous, not_found)


def iter_api_syllabes(api):
    """Segments an api word in syllabes
    example: bonjour,  bɔ̃.ʒuʁ gives ("bɔ̃"","ʒuʁ")
    """
    for s in api.split("."):
        yield s


def iter_api_phoneme(api):
    """Segments an api word in phonemes
    example: bonjour,  bɔ̃.ʒuʁ gives ("b","ɔ̃","ʒ","u","ʁ")
    """
    length = len(api)
    i = 0
    while i < length:
        cat = unicodedata.category(api[i])
        # skip points
        if cat == 'Po':
            i += 1
            continue
        if not cat == 'Ll':
            # TODO: not sure if we shall pass here...
            yield api[i]
        else:
            # got an accented letter
            if i < length - 1 and unicodedata.category(api[i+1]) == 'Mn':
                yield api[i:i+2]
                i += 1
            else:
                # got a "simple" letter
                yield api[i]
        i += 1


def read_words_list(fname="data/words_list.dmp"):
    f = open(fname, "rb")
    wl = pickle.load(f)
    f.close()
    return wl


# nimp
def search_ascii_primes(t=[37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113], s=[251, 257, 263, 269]):
    ret = []
    for a in t:
        for b in t:
            if not b == a:
                for c in t:
                    if not c == b and not c == a and a + b + c in s:
                        u = [a, b, c]
                        u.sort()
                        ret.append((chr(u[0]), chr(u[1]), chr(u[2]), a + b + c))
    return set(ret)


# numerology is bullshit
def valeur_numerique(w):
    w = w.lower()
    w = unidecode.unidecode(w)
    s = 0
    for c in w:
        if c.isalpha():
            s += ord(c) - 96
    return s
