from collections.abc import Mapping
import numpy as np

import numpy as np

class SortedDictWithFallback(Mapping):
    def __init__(self, keys, values, fallback={}):
        self.keys = np.array(keys)
        self.values = np.array(values)
        self.fallback = fallback

    def __getitem__(self, key):
        index = np.searchsorted(self.keys, key)
        if index != len(self.keys) and self.keys[index] == key:
            return self.values[index]
        return self.fallback[key]

    def __setitem__(self, key, value):
        index = np.searchsorted(self.keys, key)
        if index != len(self.keys) and self.keys[index] == key:
            self.values[index] = value
        else:
            self.fallback[key] = value

    def __iter__(self):
        return iter(self.keys)

    def __len__(self):
        return len(self.keys)
    
    @classmethod
    def from_dict(cls, dict_input, fallback={}):
        keys = sorted(dict_input.keys())
        values = [dict_input[key] for key in keys]
        return cls(keys, values, fallback)