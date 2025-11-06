from enum import IntEnum
from words_tuple import word_t
from scrap_base import search_gcd

class FlexType(IntEnum):
    ms=1
    mp=2
    fs=3
    fp=4
    mi=5
    fi=6

class Flextable:
    flexions:dict[FlexType,word_t]
    ort_radical:str
    api_radical:str
    
    def __init__(self,dict_obj:dict):
        self.ort_radical = search_gcd([v.ort for v in dict_obj.values()])
        self.api_radical = search_gcd([v.api for v in dict_obj.values()])
        self.flexions ={FlexType[k]:word_t(v.ort[len(self.ort_radical):], v.api[len(self.api_radical):]) for k,v in dict_obj.items()}

    def get_flexion(self, flex_type:FlexType)->word_t:
        return word_t(self.ort_radical + self.flexions[flex_type].ort,
                      self.api_radical + self.flexions[flex_type].api)

mot1 = {"nature":"nom", 'api': 'fœj.tɔ.nist', 'mot': 'feuilletoniste', 'genre': 'm', 'nombre': 'singulier',"flex":{
    'ms': word_t('feuilletoniste', 'fœj.tɔ.nist'),
    'mp': word_t('feuilletonistes', 'fœj.tɔ.nist'),
    'fs': word_t('feuilletoniste', 'fœj.tɔ.nist'),
    'fp': word_t('feuilletonistes', 'fœj.tɔ.nist')
}}
mot2 = {"nature":"adj","flex":{
    'ms': word_t('heureux', 'ø.ʁø'),
    'mp': word_t('heureux', 'ø.ʁø'),
    'fs': word_t('heureuse', 'ø.ʁøz'),
    'fp': word_t('heureuses', 'ø.ʁøz')
}}
word_t('feuilletoniste', 'fœj.tɔ.nist')
flext = Flextable(mot2["flex"])
print(f"radical ortho: {flext.ort_radical}, radical api: {flext.api_radical}")
A= 3