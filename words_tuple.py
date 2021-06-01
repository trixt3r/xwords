from collections import namedtuple

# import unicodedata

word_info_t = namedtuple("word_info_t", ["nature", "api", "genre", "nbr", "lex", "anto", "hypo", "syno", "desinences", "mot"], defaults=["", "", "", [], [], [], [], [], ""])
desinences_t = namedtuple("desinences_t", ['ms', 'mp', 'fs', 'fp', 'rad'], defaults=['', '', '', '', ''])
word_t = namedtuple("word_t", ["ort", "api"])


# a terme pour remplacer word_info_t
# class Lemme(object):
#     __slots__ = ["morphemes", "phonemes", 'nature', 'extra']
#
#     def __init__(self, morphemes, phonemes=None, nature=None, extra=None):
#         self.morphemes = morphemes
#         self.phonemes = phonemes
#         self.nature = nature
#         self.extra = extra


def is_article(w: word_info_t):
    return "art" in w.nature


def is_nom(w: word_info_t):
    if 'nom' not in w.nature:
        return False
    if 'pronom' in w.nature:
        return False
    if w.nature == "onoma":
        return False
    return True


def is_pronom(w: word_info_t):
    return 'pronom' in w.nature


def reform_desinences(des, cas=None, info=None):
    if cas is None:
        ret = {}
        if info == "api":
            return [des.__getattribute__(cas).api for cas in ['ms', 'mp', 'fs', 'fp']]
        for cas in ['ms', 'mp', 'fs', 'fp']:
            ret[cas] = reform_desinences(des, cas)
        if info is None:
            return ret
        if info == "ort":
            return [x.ort for x in ret.values()]
        raise Exception("'info' arg unknown:{} must be one of 'ort' or 'api' or None value")

    if des.rad != '':
        return word_t(ort=des.rad+des.__getattribute__(cas).ort[1:], api=des.__getattribute__(cas).api)
        # raise Exception("adjectif à radical. not implemented")
    if cas == 'ms':
        return des.ms
    assert des.__getattribute__(cas).ort[0] == '+', 'not implemented'
    if info is None:
        return word_t(ort=des.ms.ort+des.__getattribute__(cas).ort[1:], api=des.__getattribute__(cas).api)
    if info == "ort":
        return des.ms.ort+des.__getattribute__(cas).ort[1:]
    if info == "api":
        return des.__getatribute__(cas).api
    raise Exception("'info' arg unknown:{} must be one of 'ort' or 'api' or None value")


class Word(object):
    def __init__(self, word, api):
        self.w = word
        self.p = api

    @property
    def syllabes(self):
        for x in self.p.split("."):
            yield x
    @property
    def phonemes(self):
        for x in self.p:
            if not x == ".":
                yield x

class flex_adj:
    def __init__(self, wi_adj, cas):
        assert isinstance(wi_adj, word_info_t), 'wi_adj must be an instance of word_info_t'
        assert cas in ['ms', 'mp', 'fs', 'fp'], "unknown case: {} must be one of: 'fs', 'fp', 'ms', 'mp'".format(cas)
        self.adj = wi_adj
        self.cas = cas

    def as_str(self):
        return reform_desinences(self.adj.desinences, self.cas).ort

    def __repr__(self):
        return '<adj:{}:{}>'.format(self.adj.mot, self.cas)


def patch_word_info_t(wit, word):
    ret = word_info_t(nature=wit.nature, api=wit.api, genre=wit.genre, nbr=wit.nbr, lex=wit.lex, anto= wit.anto, hypo=wit.hypo, syno=wit.syno, desinences=wit.desinences, mot=word)
    return ret


def fusion_word_info_t(w1, w2):
    for attr in ["nature", "api", "genre", "nbr", "mot"]:
        assert w2.__getattribute__(attr) == "" or w1.__getattribute__(attr) == w2.__getattribute__(attr), "probleme attributs {} {}".format(str(w1), str(w2))
    for d in ["ms", "mp", "fs", "fp"]:
        assert (w1.desinences == [] and w2.desinences == []) or w1.desinences.__getattribute__(d) == w2.desinences.__getattribute__(d), "probleme desinences {} {}".format(str(w1), str(w2))
    return word_info_t(w1.nature, w1.api, w1.genre, w1.nbr, list(set([x for x in w1.lex]+[x for x in w2.lex])), list(set(w1.anto + w2.anto)), list(set(w1.hypo+w2.hypo)), list(set(w1.syno+w2.syno)), w1.desinences, w1.mot)
