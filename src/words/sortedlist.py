class SortedList(list):
    """a list always kept sorted.
    dichotomia is used to search and insert elements
    pos param of insert method is unused: right position is searched
    append method is a simple call to insert """

    def __init__(self, sort_key=lambda x: str(x)):
        """
        params:
        sort_key: a callable used to extract a sort key from objects in list
        """
        super(SortedList, self).__init__()
        if sort_key is not None:
            self.sort_key = sort_key

    def insert(self, pos, item):
        lo = 0
        hi = len(self)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.sort_key(self[mid]) < self.sort_key(item):
                lo = mid + 1
            else:
                hi = mid
        super(SortedList, self).insert(lo, item)

    def append(self, item):
        self.insert(-1, item)

    def sort(self, key=lambda x: x):
        """Set a new sort key for this list
            params:
            key: a new callable used to sort list
        """
        super(SortedList, self).sort(key)
        self.sort_key = key

    def __contains__(self, item):
        lo = 0
        hi = len(self)
        while lo < hi:
            mid = (lo+hi)//2
            if self.sort_key(self[mid]) < self.sort_key(item):
                lo = mid+1
            else:
                hi = mid
        return self.sort_key(self[lo]) == self.sort_key(item)

    def group(self, group_key):
        """ group items. Returns a dict which keys are determined by group_key param
            e.g: for a list of str, if group_key is "len" function, then the returned
            dict keys will be the lengths of str items, while the values will be a lsit
            of all str items having this length.
            params:
            group_key: callable called on each item
            returns:
            a dict
        """
        groups = {}
        for x in self:
            k = group_key(x)
            if k not in groups:
                groups[k] = SortedList(self.sort_key)
            groups[k].append(x)
        return groups

    def index(self, item):
        """ Search an item using dichotomia
            params:
            item: item to be searched
            returns:
            position of item in list
            raises ValueError if item not in list
        """
        lo = 0
        hi = len(self)
        while lo < hi:
            mid = (lo+hi)//2
            if self.sort_key(self[mid]) < self.sort_key(item):
                lo = mid+1
            else:
                hi = mid
        if self.sort_key(self[lo]) == self.sort_key(item):
            return lo
        raise ValueError(item + "is not in the list")
