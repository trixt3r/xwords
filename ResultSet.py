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
