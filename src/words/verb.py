from enum import IntFlag, Enum, auto
from typing import Optional
import warnings
from scrap_base import search_gcd
from words_tuple import word_t
import os.path
import pickle
from shutil import copyfile

##############################
# error = [v for v in verb.Verb_info.verb_dict.keys() if verb.Verb_info.get(v).words_list[0].startswith("-")]
# error2 = [v for v in verb.Verb_info.verb_dict.keys() if verb.Verb_info.get(v).getMode('Impératif:Présent:1s').ort.startswith("-")]
################


class AuxFlag(IntFlag):
    ETRE = 1
    AVOIR = 2
    BOTH = 3
    UNKNOWN = 4


class TransitFlag(IntFlag):
    TRANSITIF = 1
    INTRANSITIF = 2
    UNKNOWN = 4

class VerbModeEnum(IntFlag):
    Infinitif = 0
    Indicatif = 2
    Subjonctif = 4
    Conditionnel = 8
    Impératif = 16
    Participe = 32
    ParticipePt = 64 + 32
    ParticipePé = 128 + 32
    @classmethod
    def fromAbrev(cls, abrev:str):
        if abrev == "In":
            return VerbModeEnum.Indicatif
        elif abrev == "Im":
            return VerbModeEnum.Impératif
        elif abrev == "C":
            return VerbModeEnum.Conditionnel
        elif abrev == "S":
            return VerbModeEnum.Subjonctif
        else:
            raise Exception("abrev de mode inconnu: {}".format(abrev))
    @classmethod
    def fromName(cls, name:str):
        if name == "Infinitif":
            return VerbModeEnum.Infinitif
        elif name == "Indicatif":
            return VerbModeEnum.Indicatif
        elif name == "Impératif":
            return VerbModeEnum.Impératif
        elif name == "Conditionnel":
            return VerbModeEnum.Conditionnel
        elif name == "Subjonctif":
            return VerbModeEnum.Subjonctif
        else:
            raise Exception("nom de mode inconnu: {}".format(name))
    def getIndex(self):
        if self.value == VerbModeEnum.Infinitif.value:
            return 0
        elif self.value == VerbModeEnum.Indicatif.value:
            return 1
        elif self.value == VerbModeEnum.Subjonctif.value:
            return 2
        elif self.value == VerbModeEnum.Conditionnel.value:
            return 3
        elif self.value == VerbModeEnum.Impératif.value:
            return 4
        elif self.value == VerbModeEnum.ParticipePt.value:
            return 5
        elif self.value == VerbModeEnum.ParticipePé.value:
            return 6
        elif self.value == VerbModeEnum.Participe.value:
            raise Exception("Participe (%d) is not a valid mode" % VerbModeEnum.Participe.value)


class VerbTempsEnum(Enum):
    Présent = auto()
    Passé = auto()
    Passé_simple = auto()
    Passé_composé = auto()
    Passé_antérieur = auto()
    Imparfait = auto()
    Plus_que_parfait = auto()
    Futur_simple = auto()
    Futur_antérieur = auto()
    
    @classmethod
    def fromAbrev(cls, abrev:str):
        if abrev == "Pr":
            return VerbTempsEnum.Présent
        elif abrev == "Pa":
            return VerbTempsEnum.Passé
        elif abrev == "Ps":
            return VerbTempsEnum.Passé_simple
        elif abrev == "Pc":
            return VerbTempsEnum.Passé_composé
        elif abrev == "Paé":
            return VerbTempsEnum.Passé_antérieur
        elif abrev == "Imp":
            return VerbTempsEnum.Imparfait
        elif abrev == "Pqp":
            return VerbTempsEnum.Plus_que_parfait
        elif abrev == "Fs":
            return VerbTempsEnum.Futur_simple
        elif abrev == "Faé":
            return VerbTempsEnum.Futur_antérieur
        else:
            raise Exception("abrev de temps inconnu: {}".format(abrev))
    @classmethod
    def fromName(cls, name:str):
        name = name.replace(" ","_")
        if name == "Présent":
            return VerbTempsEnum.Présent
        elif name == "Passé":
            return VerbTempsEnum.Passé
        elif name == "Passé_simple":
            return VerbTempsEnum.Passé_simple
        elif name == "Passé_composé":
            return VerbTempsEnum.Passé_composé
        elif name == "Passé_antérieur":
            return VerbTempsEnum.Passé_antérieur
        elif name == "Imparfait":
            return VerbTempsEnum.Imparfait
        elif name == "Plus_que_parfait":
            return VerbTempsEnum.Plus_que_parfait
        elif name == "Futur_simple":
            return VerbTempsEnum.Futur_simple
        elif name == "Futur_antérieur":
            return VerbTempsEnum.Futur_antérieur
        else:
            raise Exception("nom de temps inconnu: {}".format(name))

def parcours_verbe(verb):
    for mode in verb.modes:
        if mode == VerbModeEnum.Infinitif:
            yield verb.modes[mode][0]
        elif mode == VerbModeEnum.ParticipePt or mode == VerbModeEnum.ParticipePé:
            for k, word in verb.modes[mode].items():
                yield word
        else:
            for temps in verb.modes[mode]:
                formes = verb.modes[mode][temps]
                for i, f in enumerate(formes):
                    yield f

def parcours_verbe_dict(verb_info:dict):
    for mode in verb_info:
        if mode == "aux":
            continue
        if mode == "inf":
            yield verb_info[mode]
        elif mode == "Part":
            for k,part in verb_info[mode].items():
                for genre_nombre, word in part.items():
                    yield word
        else:
            for temps in verb_info[mode]:
                formes = verb_info[mode][temps]
                for i, f in enumerate(formes):
                    yield f


def compress_word_t(w:word_t,ort_radic:str,api_radic:str):
    return word_t(w.ort[len(ort_radic):], w.api[len(api_radic):])

def decompress_word_t(w:word_t, ort_radic, api_radic):
    return word_t(ort_radic+w.ort, api_radic+w.api)

def compress_verb_dict(verb:dict):
    res = [w for w in parcours_verbe_dict(verb)]
    res.sort(key=lambda x:x.ort)
    words = [w.ort for w in res]
    apis = [w.api for w in res]
    ort_radic = search_gcd(words)
    api_radic = search_gcd(apis)
    for mode in verb:
        if mode == "aux":
            continue
        if mode == "inf":
            verb[mode] = compress_word_t(verb[mode], ort_radic, api_radic)
        elif mode == "Part":
            for k,part in verb[mode].items():
                verb[mode][k] = {genre_nombre: compress_word_t(word, ort_radic, api_radic) for genre_nombre, word in part.items()}
        else:
            for temps in verb[mode]:
                verb[mode][temps] = [compress_word_t(w, ort_radic, api_radic) for w in verb[mode][temps]]
    return (verb, ort_radic, api_radic)

def decompress_verb_dict(verb:dict, ort_radic:str, api_radic:str):
    for mode in verb:
        if mode == "aux":
            continue
        if mode == "inf":
            verb[mode] = decompress_word_t(verb[mode], ort_radic, api_radic)
        elif mode == "Part":
            for k,part in verb[mode].items():
                verb[mode][k] = {genre_nombre: decompress_word_t(word, ort_radic, api_radic) for genre_nombre, word in part.items()}
        else:
            for temps in verb[mode]:
                verb[mode][temps] = [decompress_word_t(w, ort_radic, api_radic) for w in verb[mode][temps]]
    return verb



# TODO: l'auxilliaire dépend de la forme... parfois, c'est "avoir" en forme active et "être" en forme pronominale...
# TODO: verbes pronominaux
# TODO: orthographes multiples (je déblaye/jé déblaie)
# TODO: transitivité
# TODO: antonymes/hyponymes/synonymes/champs lexicaux
class Verb_info:
    # verb_list = init_verb_list()
    verb_dict = {}
    modes_dict={
        "In":VerbModeEnum.Indicatif,
        "Im":VerbModeEnum.Impératif,
        "C":VerbModeEnum.Conditionnel,
        "S":VerbModeEnum.Subjonctif
    }
    # temps_dict={
    #     "Pr":"Présent",
    # "Pa":"Passé",
    # "Ps":"Passé_simple",
    # "Pc":"Passé_composé",
    # "Paé":"Passé_antérieur",
    # "Imp":"Imparfait",  
    # "Pqp":"Plus_que_parfait",
    # "Fs":"Futur_simple",
    # "Faé":"Futur_antérieur"
    # }

    def participe_pé(self, genre_nombre: str = None):
        warnings.warn("attention, participe passé")
        if genre_nombre is None:
            return self.modes[VerbModeEnum.ParticipePé]['ms'][0]
        return self.modes[VerbModeEnum.ParticipePé][genre_nombre][0]


    def participe_pt(self, genre_nombre: str = None):
        warnings.warn("attention, participe présent")
        if genre_nombre is None:
            return self.modes[VerbModeEnum.ParticipePt]['ms'][0]
        return self.modes[VerbModeEnum.ParticipePt][genre_nombre][0]

    @property
    def infinitif(self):
        return self.modes[VerbModeEnum.Infinitif][0]

    def __init__(self, verbe_struct,compressed=False):
        self.auxiliaire = AuxFlag.UNKNOWN
        self.transitif = verbe_struct["transitif"] if "transitif" in verbe_struct else TransitFlag.UNKNOWN
        self.compressed = compressed
        if compressed:
            verbe_struct, ort_radic, api_radic = compress_verb_dict(verbe_struct)
            self.ort_radic = ort_radic
            self.api_radic = api_radic
        # TODO: ci-dessous comme ci-dessus
        # c_temps = []
        # modes_list = ["In", "Im", "C", "S"]
        # c_modes = [VerbModeEnum.Indicatif, VerbModeEnum.Impératif, VerbModeEnum.Conditionnel, VerbModeEnum.Subjonctif]
        # for m in modes_list:
            # mode = c_modes[modes_list.index(m)].getIndex()
        self.modes = {k:{} for k in [VerbModeEnum.Indicatif, VerbModeEnum.Subjonctif, VerbModeEnum.Conditionnel, VerbModeEnum.Impératif]}
        for mode in VerbModeEnum:
            # mode = modes_dict[mode_key].getIndex()
            if mode == VerbModeEnum.Participe or mode == VerbModeEnum.Infinitif:
                continue
            for temps in verbe_struct[mode.name]:
                # todo: ci-dessous comme ci-dessus
                current_temps_list = []
                for x in verbe_struct[mode.name][temps]:
                    current_temps_list.append(word_t(x[0], x[1]))
                self.modes[mode][VerbTempsEnum.fromName(temps.replace(" ","_").replace("-","_"))] = current_temps_list
        if verbe_struct["aux"] == "avoir":
            self.auxiliaire = AuxFlag.AVOIR
        if verbe_struct["aux"] == "être":
            self.aux = AuxFlag.ETRE
        self.modes[VerbModeEnum.Infinitif] = [verbe_struct['inf']]
        self.modes[VerbModeEnum.ParticipePt] = verbe_struct["Part"]["Pr"]
        # self.modes[VerbModeEnum.ParticipePt] = [word_t(self.participe_pt[0], self.participe_pt[1])]
        self.modes[VerbModeEnum.ParticipePé] = verbe_struct["Part"]["Pa"]
        # self.modes[VerbModeEnum.ParticipePé] = [word_t(self.participe_pé[0], self.participe_pé[1])]
        self._radical = search_gcd(self.words_list)

    @property
    def radical(self):
        if self.compressed:
            return self.ort_radic
        #TODO: c'est n'importe quoi.
        if not hasattr(self, "_radical") or self._radical is None:
            self._radical = search_gcd(self.words_list)
        return self._radical

    @property
    def terminaisons(self):
        if self.compressed:
            self._terminaisons = set([x.ort for x in parcours_verbe(self)])
        if not hasattr(self, "_terminaisons") or self._terminaisons is None:
            self._terminaisons = list(set([x[len(self.radical):] for x in self.words_list]))
            self._terminaisons.sort()
        return self._terminaisons

    @property
    def words_list(self):
        return self.get_words_list()

    def get_words_list(self, as_str=True):
        ppé = self.modes[VerbModeEnum.ParticipePé]
        ppt = self.modes[VerbModeEnum.ParticipePt]
        #NOTE: dans la ligne ci-dessous, je reconstruis les flex des participes, mais l'api n'est pas correcte pour les formes féminines...
        #TODO: faire la reconstruction dans le constructeur
        to_return = [self.infinitif, ppé['ms'], ppé["fs"], ppé["mp"], ppé["fp"], ppt['ms'], ppt["fs"], ppt["mp"], ppt["fp"]]

        for i in [VerbModeEnum.Indicatif, VerbModeEnum.Subjonctif, VerbModeEnum.Conditionnel, VerbModeEnum.Impératif]:
            for t in self.modes[i]:
                for f in self.modes[i][t]:
                    to_return.append(f)
        if as_str:
            to_return = [x.ort for x in to_return]
            to_return.sort()
        else:
            to_return.sort(key=lambda x: x.ort)
        if self.compressed:
            if as_str:
                to_return = [self.ort_radic + w for w in to_return]
            else:
                to_return = [decompress_word_t(w,self.ort_radic, self.api_radic) for w in to_return]
        return to_return

    def __repr__(self):
        return "<verbe: {}>".format(self.infinitif.ort)

    def getMode(self, mode:VerbModeEnum, temps:Optional[VerbTempsEnum]=None, personne_idx:Optional[int]=None,return_tuple:bool=False):
        prepare = None
        if return_tuple:
            prepare = lambda x: x
        else:
            prepare = lambda x: x.ort
        if temps is not None:
            temps_obj = self.modes[mode][temps]
            if personne_idx is not None:
                return prepare(self.modes[mode][temps][personne_idx])
            else:
                return prepare([x for x in temps_obj])
        else:
            raise NotImplementedError("get mode sans temps non implémenté")
    #exemples: getMode("Indicatif") getMode("Indicatif:Présent"), getMode("Indicatif:Présent:1s"), getMode("Impératif:Présent:2p")
    def getMode_str(self, m:str, t=None):
        # mode_s = ""
        # temps_s = None
        temps = None
        mode = None
        personne_s = None
        personne_idx = None
        if t is None:
            toks = m.split(':')
            # mode = Verb_info.modes_dict[m[0]]
            mode = VerbModeEnum.fromName(toks[0])
            if len(toks) >= 2:
                temps = VerbTempsEnum.fromName(toks[1].replace(" ","_").replace("-","_"))
            if len(toks) == 3:
                personne_s = toks[2]
                personne_idx = int(personne_s[0]) - 1
                if personne_s[1].lower() == 'p':
                    personne_idx += 3

                
        else:
            raise Exception("utilisation dépréciée de getMode, utiliser getMode('Mode:Temps:Personne')")
            mode_s = m
            temps_s = t
        # try:
        #     mode = VerbModeEnum[mode_s]
        # except KeyError:
        #     raise Exception("mode inconnu: {}".format(mode_s))
        try:
            mode = self.modes[mode]
        except IndexError:
            raise Exception("mode {} inconnu du verbe {}".format(mode, self.infinitif))

        if temps is not None:
            if temps not in mode:
                raise Exception(f"temps {t} inconnu pour le mode {m[0]} du verbe {self.infinitif}")
            mode = mode[temps]

        # if personne_s is not None:
        #     print(f"personne: {personne_s}")
        #     assert len(personne_s) == 2, "personne inconnue: " + personne_s
        #     assert personne_s == "on" or (personne_s[0] in ["1", "2", "3"] and personne_s[1].lower() in 'sp'), "personne inconnue: " + personne_s
        #     assert personne_s == "on" or (personne_s[0] in "123" and personne_s[1].lower() in 'sp'), "personne inconnue: " + personne_s
            
            
        if personne_idx is None:
            if self.compressed:
                return [decompress_word_t(w,self.ort_radic, self.api_radic) for w in mode]
            return mode
        else:
            if personne_idx < len(mode):
                if self.compressed:
                    return decompress_word_t(mode[personne_idx],self.ort_radic, self.api_radic)
                return mode[personne_idx]
            else:
                return None

    @classmethod
    def get(cls, v:str):
        verb:Verb_info = None
        mode = ""
        temps = ""
        v = v.split(":")
        verb = v[0]
        if Verb_info.verb_dict is not None and verb in Verb_info.verb_dict:
            verb = Verb_info.verb_dict[verb]
        else:
            # raise Exception("Verbe inconnu: {}".format(v))
            return None
        if len(v) > 1:
            mode = v[1].capitalize()
            if len(v) > 2:
                temps = v[2].capitalize()
                return verb.getMode_str(mode, temps)
            else:
                return verb.getMode_str(mode)
        return verb

    @classmethod
    def add(cls, verb):
        assert(isinstance(verb, Verb_info))
        infinitif = verb.infinitif
        # todo ce test doit disparaitre
        if not isinstance(infinitif, str):
            infinitif = infinitif.ort
        assert(infinitif not in Verb_info.verb_dict)
        Verb_info.verb_dict[infinitif] = verb
        if os.path.exists("src/words/data/verb_info_dict.dmp"):
            copyfile("src/words/data/verb_info_dict.dmp", "src/words/data/backup/verb_info_dict.dmp")
            f = open("src/words/data/verb_info_dict.dmp", "wb")
            pickle.dump(Verb_info.verb_dict,f)
            f.close()
        elif os.path.exists("words/data/verb_info_dict.dmp"):
            copyfile("words/data/verb_info_dict.dmp", "words/data/backup/verb_info_dict.dmp")
            f = open("words/data/verb_info_dict.dmp", "wb")
            pickle.dump(Verb_info.verb_dict,f)
            f.close()

    @classmethod
    def full_words_list(cls, verbs=None, filter=None):
        if verbs is None:
            verbs = Verb_info.verb_dict.values()
        verbes_list = []
        c = 0
        for v in verbs:
            try:
                verbes_list += v.words_list
                c += 1
            except Exception:
                pass
        verbes_list=list(set(verbes_list))
        verbes_list.sort()
        print("%d verbes %d words" % (c, len(verbes_list)))
        return verbes_list

    @classmethod
    def full_words_list_g(cls, verbs=None, filter=None):
        if verbs is None:
            verbs = Verb_info.verb_dict.values()
        verbes_list = []
        c = 0
        for v in verbs:
            try:
                verbes_list = v.words_list
                for x in verbes_list:
                    yield x
                c += 1
            except Exception:
                pass
        print("%d verbes %d words" % (c, len(verbes_list)))


def init_verb_class():
    Verb_info.verb_dict = {}
    if os.path.isfile("data/verb_info_dict.dmp"):
        f = open("data/verb_info_dict.dmp", "rb")
        verbs = pickle.load(f)
        f.close()
        print("chargés %d verbes" % len(verbs))
        Verb_info.verb_dict = verbs
    elif os.path.isfile("src/words/data/verb_info_dict.dmp"):
        f = open("src/words/data/verb_info_dict.dmp", "rb")
        verbs = pickle.load(f)
        f.close()
        print("chargés %d verbes" % len(verbs))
        Verb_info.verb_dict = verbs


init_verb_class()





def convert_verb_list(fname):
    f = open(fname, "rb")
    vlist = pickle.load(f)
    to_ret = {}
    f.close()
    cnt = 0
    for v in vlist:
        verb = vlist[v]
        verb["inf"] = v
        to_ret[v] = Verb_info(verb)
        cnt += 1
        if cnt % 50 ==0:
            print("%s %d" % (v, cnt))
    return to_ret




# gestion terminaisons
# ger = [verb.Verb_info.get(x) for x in verb.Verb_info.verb_dict.keys() if verb.Verb_info.get(x).infinitif[0].endswith('ger')]
# end_ger=verb.Verb_info.get('dommager').terminaisons
# [x for x in ger if x.terminaisons != end_ger]

from words_tuple import word_info_t

def add_verbs_to_index(idx):
    cnt = 0
    for v in Verb_info.verb_dict.keys():
        verb = Verb_info.get(v)
        words_list = verb.get_words_list(False)
        for w in words_list:
            if not w.ort.startswith("-"):
                idx.addWord(w.ort, word_info_t(nature="verb", api=w.api, mot=w.ort))
                cnt += 1
    print("ajoutés: %d mots" % cnt)

# verbe_test = Verb_info.get("produire")

# apis = set([x[1] for x in verbe_test.get_words_list(False) if not x[1]=="produit" and not x[1]=="produisant"])
# orths = set([x[0] for x in verbe_test.get_words_list(False)])

# rad_api = search_gcd(apis)
# term_api = [x[len(rad_api):] for x in apis]

# rad_ort = search_gcd(orths)
# term_ort = [x[len(rad_ort):] for x in orths]

class Verb_flex:
    verb:Verb_info = None
    mode:VerbModeEnum = None
    temps:VerbTempsEnum = None
    pronom:int = None

    def __init__(self, verb:Verb_info, mode:VerbModeEnum, temps:VerbTempsEnum, pronom:int):
        """
        pronom: 0..5 (1s,2s,3s,1p,2p,3p)
        """
        self.verb = verb
        self.mode = mode
        self.temps = temps
        self.pronom = pronom

    @classmethod
    def from_str(cls, verb:Verb_info, flex_str:str):
        toks = flex_str.split(":")
        mode = VerbModeEnum.fromName(toks[0])
        temps = VerbTempsEnum.fromName(toks[1].replace(" ","_").replace("-","_"))
        personne_s = toks[2]
        personne_idx = int(personne_s[0]) - 1
        if personne_s[1].lower() == 'p':
            personne_idx += 3
        return cls(verb, mode, temps, personne_idx)

    def get_word(self, get_tuple:bool=False)->word_t:
        return self.verb.getMode(self.mode, self.temps, self.pronom, get_tuple)

    def __unicode__(self):
        pronoms=["je","tu","il/elle/on","nous","vous","ils/elles"]
        # w = self.verb.modes[self.mode][self.temps][self.pronom-1].ort
        w = f"<{self.verb.infinitif.ort}:{self.mode}:{self.temps}:{self.pronom} ({pronoms[self.pronom]})>"
        return w
    
    def __repr__(self):
        return self.__unicode__()

class ConjVerbStr(str):
    flex:Verb_flex = None
    def __new__(cls, flex:Verb_flex):
        instance = str.__new__(cls, flex.get_word())
        instance.flex = flex
        return instance