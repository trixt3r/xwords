import pickle

from cw import getCanonicForm, can_write
from cw import iter_api_phoneme
from words_tuple import word_info_t
from node import Node

from sortedlist import SortedList


class WSortedList(SortedList):
    def __init__(self):
        super(WSortedList, self).__init__(None)

    def sort_key(self, x):
        return x.mot


# parcours récursif: si data est un dictionnaire de dictionnaires de dctionnaires...
# cette fonction renvoit les éléments "feuilles"
def explore_to_words(data):
    if isinstance(data, list):
        for w in data:
            yield w
        return
    for k in data.keys():
        for k in explore_to_words(data[k]):
            yield k


class ResultSet(object):
    def __init__(self, items, request=None):
        # self.items = SortedList(lambda x:x.mot)
        self._items = WSortedList()
        self.request = request
        self.accents_flag = False
        for x in items:
            self._items.append(x)

    def accents(self, flag=None):
        if flag is None:
            return self.accents_flag
        self.accents_flag = flag

    def group_dict(self, dico, group_by):
        for k in dico.keys():
            if isinstance(dico[k], dict):
                dico[k] = self.group_dict(dico[k], group_by)
            else:
                assert isinstance(dico[k], SortedList)
                dico[k] = dico[k].group(group_by)

    # todo: lorsqu'on classe par longueur, puisqu'on place les listes
    # dans un dictionnaire, on ne les parcourt pas dans l'ordre de longueur.
    # les mots sont bien classés, mais ceux de longueur 3 peuvent apparaître
    # avant ceux de longueur 2, etc
    # use SortedDict ??
    def group(self, group_by):
        def nature_group_filter_key(wit: word_info_t):
            if wit.nature.startswith("flex-"):
                return wit.nature[5:]
            return wit.nature

        def len_group_filter_key(wit: word_info_t):
            return len(wit.mot)

        if not isinstance(group_by, list):
            group_by = [group_by]
        for b in group_by:
            assert b in ["len", "nature", "genre", "nbr"]
            key = None
        if group_by[0] == 'len':
            # key = lambda x: len(x.mot)
            key = len_group_filter_key
        else:
            if group_by[0] == "nature":
                key = nature_group_filter_key
            else:
                # key = lambda x: getattr(x, b)
                key = lambda x: getattr(x, b)
        groups = self._items.group(key)
        for b in group_by[1:]:
            key = None
            if b == 'len':
                # key = lambda x: len(x.mot)
                key = len_group_filter_key
            elif b == "nature":
                key = nature_group_filter_key
            else:
                # key = lambda x: getattr(x, b)
                key = lambda x: getattr(x, b)
            self.group_dict(groups, key)
        self.groups = groups
        self.group_names = group_by

    # filter items set.
    # grouping and sorting should be lost
    # filter: a callable with one parameter of type word_info_t. Should return true
    # if current element should be kept in new resultset
    def filter(self, filter):
        assert callable(filter)
        new_list = WSortedList()
        for x in self.items:
            if filter(x):
                new_list.append(x)
        return ResultSet(new_list)

    # obsolete
    @property
    def words(self):
        return [x.mot for x in self._items]

    @property
    def items(self):
        if hasattr(self, "groups"):
            for x in explore_to_words(self.groups):
                yield x
            return
        for x in self. _items:
            yield x

    def __repr__(self):
        return "[ResultSet {} items]".format(len(self._items))


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


# idem, not sre it's the right way.It's possible that MetaClass isn't useful here.
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
        # all_confused_letters = []
        # for t in confusions:
        #     for letter in t:
        #         all_confused_letters.append(letter)
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

    # def search_anagrammes(self, word, keep_accents=False, exact_match=False, confusions=[]):
    #     # def filter_word_list(word, node_list):
    #     #     words = []
    #     #     cword = cwapi.getCanonicForm(word, True)
    #     #     for n in node_list:
    #     #         if n.data is not None:
    #     #             for w in n.data:
    #     #                 cw = cwapi.getCanonicForm(w, True)
    #     #                 if cwapi.can_write(cword, cw):
    #     #                     words.append(w)
    #     #     return words
    #
    #     def create_accents_filter(word):
    #         return lambda x: can_write(self.key_valider(word, True), self.key_valider(x.mot, True))
    #     ret = []
    #     if exact_match:
    #         raise Exception("exact match option probably broken")
    #         n = self.search(self.key_valider(word), False)
    #         if len(word) != len(n.cw):
    #             n = []
    #         else:
    #             n = [n]
    #         rs = Index.ResultSet(n, word)
    #         if keep_accents:
    #             rs.filters.append(create_accents_filter(word))
    #         return rs
    #
    #     fifo = [(self.root_node, self.key_valider(word))]
    #     while len(fifo) > 0:
    #         s = fifo.pop()
    #         cn = s[0]
    #         cw = s[1]
    #         for i in range(0, len(cw)):
    #             if i > 0 and cw[i-1] == cw[i]:
    #                 continue
    #             child = cn.child(cw[i])
    #             if child is not None:
    #                 ret.append(child)
    #                 to_find = cw[:i] + cw[i+1:]
    #                 if len(to_find) > 0:
    #                     fifo.append((child, to_find))
    #                 # print("%s %s" % (child.cw, to_find))
    #     return_list = []
    #     for x in ret:
    #         if x.data is not None:
    #             for wit in x.data:
    #                 return_list.append(wit)
    #     rs = ResultSet(return_list, request=word)
    #     if keep_accents:
    #         rs.accents(True)
    #     return rs


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
