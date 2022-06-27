from enum import IntFlag
import unicodedata
# from words.cw import iter_api_phoneme
from cw import iter_api_phoneme

class IPAIter(object):
    class Options(IntFlag):
        NONE = 0
        SYLL = 2
        CONS = 4
        VOWE = 8

    def __init__(self, w:str):
        self.word = w
    
    def __iter__(self):
        self.i = 0
        return self
    
    def __next__(self):
        if self.i >= len(self.word):
            raise StopIteration
        cat = unicodedata.category(self.word[self.i])
        # skip points
        if cat == 'Po':
            self.i += 1
            return self.__next__()
        if not cat == 'Ll':
            # TODO: not sure if we shall pass here...
            to_ret =  self.word[self.i]
            self.i += 1
            return to_ret
        else:
            # got an accented letter
            if self.i < len(self.word) - 1 and unicodedata.category(self.word[self.i+1]) == 'Mn':
                to_ret=self.word[self.i:self.i+2]
                self.i += 2
                return to_ret
            else:
                # got a "simple" letter
                to_ret= self.word[self.i]
                self.i += 1
                return to_ret
        # self.i += 1

class IPASyllabeIter:
    def __init__(self,w):
        self.word = w
    def __iter__(self):
        self.i = 0
        return self
    def __next__(self):
        pass

class IPAStr(str):
    def __iter__(self):
        i = IPAIter(self)
        return i.__iter__()

def mytest():
    x="bɔ̃.ʒuʁ"
    ii=IPAIter(x)
    for i in ii:
        print(i)
    
    print("########################")
    
    ii=IPAIter(x)
    for i in ii[1:2]:
        print(i)