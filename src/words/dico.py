import pickle

from cw import getCanonicForm, can_write
from cw import iter_api_phoneme
# from words_tuple import word_info_t
from node import Node
from ResultSet import ResultSet


# not sure if it's the right way to do that
class WordMetaIndex(type):
    def __new__(metacls, class_name: str, class_bases: tuple, class_attrs: dict):
        def data_initializer(self, node):
            node.data = list()

        def set_data(self, node, data):
            node.data.append(data)

        def data_key_getter(self, data):
            return data.mot

        def key_tokenizer(self, key):
            for c in key:
                yield c

        def key_valider(self, key, *args, **kwargs):
            return getCanonicForm(key, *args, **kwargs)

        if "data_initializer" not in class_attrs:
            class_attrs["data_initializer"] = data_initializer
        if "set_data" not in class_attrs:
            class_attrs["set_data"] = set_data
        if "data_key_getter" not in class_attrs:
            class_attrs['data_key_getter'] = data_key_getter
        if "key_tokenizer" not in class_attrs:
            class_attrs['key_tokenizer'] = key_tokenizer
        if "key_valider" not in class_attrs:
            class_attrs['key_valider'] = key_valider
        if 'node_impl' not in class_attrs:
            class_attrs["node_impl"] = Node
        cls = type.__new__(metacls, class_name, class_bases, class_attrs)
        return cls


# idem, not sure it's the right way.It's possible that MetaClass isn't useful here.
class PhonemeMetaIndex(type):
    def __new__(metacls, class_name: str, class_bases: tuple, class_attrs: dict):
        def data_initializer(self, node):
            node.data = list()

        def set_data(self, node, data):
            node.data.append(data)

        def data_key_getter(self, data):
            return data.api

        def key_tokenizer(self, key):
            return iter_api_phoneme(key)

        def key_valider(self, key, *args, **kwargs):
            # il faut juste emplacer les "è" par des "é"
            # les o ouverts par des o fermés, etc
            # return getCanonicForm(key.replace('.', ''), *args, **kwargs)
            r = [c for c in self.key_tokenizer(key)]
            r.sort()
            return r

        if "data_initializer" not in class_attrs:
            class_attrs["data_initializer"] = data_initializer
        if "set_data" not in class_attrs:
            class_attrs["set_data"] = set_data
        if "data_key_getter" not in class_attrs:
            class_attrs['data_key_getter'] = data_key_getter
        if "key_tokenizer" not in class_attrs:
            class_attrs['key_tokenizer'] = key_tokenizer
        if "key_valider" not in class_attrs:
            class_attrs['key_valider'] = key_valider
        if 'node_impl' not in class_attrs:
            class_attrs["node_impl"] = Node
        cls = type.__new__(metacls, class_name, class_bases, class_attrs)
        return cls


class AbstractIndex():
    def __init__(self):
        self.root_node = self.node_impl()

    def addWord(self, data):
        w = self.data_key_getter(data)
        cw = self.key_valider(w)
        ri = self.root_node.addWord([c for c in cw])
        if ri.data is None:
            self.data_initializer(ri)
        self.set_data(ri, data)

    # def addVerb(self, verb):
    #     assert isinstance(verb, Verb_info), "verb param must be an instance of verb.Verb_info"
    #     wl = verb.get_words_list(as_str=False)
    #     del wl[wl.index(verb.infinitif)]
    #     # word_info_t(nature='flex-verb', api='a.bɛs', genre='abaisse', nbr='abaisser', lex=[], anto=[], hypo=[], syno=[], desinences=[], mot='')
    #
    #     self.addWord(verb.infinitif.ort, word_info_t(nature="verb", api=verb.infinitif.api, mot=verb.infinitif.ort) )
    #     for w in wl:
    #         self.addWord(w.ort, word_info_t(nature="flex-verb", nbr=verb.infinitif.ort, mot=w.ort, api=w.api))
    # """
    # search the precise node matching CW(w)
    # """

    def search(self, w, keep_accents=True):
        cw = self.key_valider(w, keep_accents)
        node = self.root_node.search(cw)
        return node

    """
    return all anagrams formable with "word"
    Args:
    word the word to search for
    keep_accents: boolean. If true, only the words matching exactly "word" param are returned
    exact_match: boolean. If true, only anagrams using all letters of "word" will be returned
    generics: list of tuples. Each tuple describes key items (letters/phonemes) that are considered as equivalent
    example: (e,é,è,ê,ë) is equivalent to do a search where all "e" letters are considered as unaccented.
    this is specially interesting when working with phonemes (o, ɔ)... Implies keep_accents=True
    """

    def search_anagrammes(self, word, keep_accents=False, exact_match=False, generics=[]):
        def create_accents_filter(word):
            return lambda x: can_write(self.key_valider(word, True), self.key_valider(x.mot, True))

        ret = []
        # TODO: check that each letter is present in only one tuple
        # all_generic_symbols = []
        # for t in generics:
        #     for letter in t:
        #         all_generics_symbols.append(letter)
        if exact_match:
            raise Exception("Exact match option probably broken.")
            n = self.search(self.key_valider(word), False)
            if len(word) != len(n.cw):
                n = []
            else:
                n = [n]
            rs = Index.ResultSet(n, word)
            if keep_accents:
                rs.filters.append(create_accents_filter(word))
            return rs

        fifo = [(self.root_node, self.key_valider(word))]
        while len(fifo) > 0:
            s = fifo.pop()
            cn = s[0]
            cw = s[1]
            for i in range(0, len(cw)):
                if i > 0 and cw[i-1] == cw[i]:
                    continue
                current_symbol = cw[i]
                child = cn.child(current_symbol)
                if child is not None:
                    ret.append(child)
                    # consule current symbol
                    to_find = cw[:i] + cw[i+1:]
                    if len(to_find) > 0:
                        fifo.append((child, to_find))
                    # print("%s %s" % (child.cw, to_find))
        return_list = []
        for x in ret:
            if x.data is not None:
                for wit in x.data:
                    return_list.append(wit)
        rs = ResultSet(return_list, request=word)
        if keep_accents:
            rs.accents(True)
        return rs


# alphabetic index class
class Index(AbstractIndex, metaclass=WordMetaIndex):
    def __init__(self):
        self.root_node = self.node_impl("")

    def search_anagrammes(self, word, keep_accents=False, exact_match=False):
        rs = super(Index, self).search_anagrammes(word, keep_accents, exact_match)
        if keep_accents:
            canonic_form = getCanonicForm(word, True)
            # print("canonic: %s" % canonic_form)
            return ResultSet([x for x in rs.items if can_write(canonic_form, getCanonicForm(x.mot, True))], rs.request)
        return rs


# phonetic index class
class PhonemeIndex(AbstractIndex, metaclass=PhonemeMetaIndex):
    def __init__(self):
        self.root_node = self.node_impl([])
    pass


class Dico(object):
    def __init__(self, dico):
        self.dico = dico
        pass

    def __iter__(self):
        self._dico_iter = iter(self.dico)
        self._dico_element = self.dico[next(self._dico_iter)]
        self._dico_element_iter = iter(self._dico_element)
        return self

    def __next__(self):
        for i in range(0, 2):
            try:
                return next(self._dico_element_iter)
            except StopIteration:
                self._dico_element = self.dico[next(self._dico_iter)]
                self._dico_element_iter = iter(self._dico_element)


def create_index():
    with open("data/gramm.dmp", "rb") as f:
        dictio = (pickle.load(f))
    idx = Index()
    for k in dictio:
        for w in dictio[k]:
            idx.addWord(w)
    return idx


def create_phoneme_index():
    with open("data/gramm.dmp", "rb") as f:
        dictio = (pickle.load(f))
    idx = PhonemeIndex()
    for k in dictio:
        for w in dictio[k]:
            idx.addWord(w)
    return idx
