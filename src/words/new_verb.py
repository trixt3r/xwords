from enum import IntFlag, Enum, auto
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


# TODO: l'auxilliaire dépend de la forme... parfois, c'est "avoir" en forme active et "être" en forme pronominale...
# TODO: verbes pronominaux
# TODO: orthographes multiples (je déblaye/jé déblaie)
# TODO: transitivité
# TODO: antonymes/hyponymes/synonymes/champs lexicaux
class Verb_info:
    # verb_list = init_verb_list()
    verb_dict = {}

    @property
    def participe_pé(self):
        return self.modes[VerbModeEnum.ParticipePé][0]

    @property
    def participe_pt(self):
        return self.modes[VerbModeEnum.ParticipePt][0]

    @property
    def infinitif(self):
        return self.modes[VerbModeEnum.Infinitif][0]

    def __init__(self, verbe_struct:dict):
        self.modes:dict = {}
        self.auxiliaire = AuxFlag.UNKNOWN
        self.transitivité = TransitFlag.UNKNOWN
        # TODO: ci-dessous comme ci-dessus
        # c_temps = []
        # modes_list = ["In", "Im", "C", "S"]
        # c_modes = [VerbModeEnum.Indicatif, VerbModeEnum.Impératif, VerbModeEnum.Conditionnel, VerbModeEnum.Subjonctif]
        # for m in modes_list:
            # mode = c_modes[modes_list.index(m)].getIndex()
        modes_dict={
            "In":VerbModeEnum.Indicatif,
            "Im":VerbModeEnum.Impératif,
            "C":VerbModeEnum.Conditionnel,
            "S":VerbModeEnum.Subjonctif
        }
        for m,mode in modes_dict.items():
            self.modes[mode] = {}
            for temps in verbe_struct[m]:
                #NOTE ici pas top on perd l'info de la personne (ex: corse dans "ça se corse")
                self.modes[mode][temps] = [word_t(x[0], x[1]) for x in verbe_struct[m][temps]]
        if verbe_struct["aux"] == "avoir":
            self.auxiliaire = AuxFlag.AVOIR
        if verbe_struct["aux"] == "être":
            self.aux = AuxFlag.ETRE
        self.modes[VerbModeEnum.Infinitif] = [verbe_struct['inf']]
        self.modes[VerbModeEnum.ParticipePt] = [verbe_struct["Part"]["Pr"]]
        self.modes[VerbModeEnum.ParticipePt] = [word_t(self.participe_pt[0], self.participe_pt[1])]
        self.modes[VerbModeEnum.ParticipePé] = [verbe_struct["Part"]["Pa"]]
        self.modes[VerbModeEnum.ParticipePé] = [word_t(self.participe_pé[0], self.participe_pé[1])]

    @property
    def radical(self):
        return search_gcd(self.words_list)

    @property
    def terminaisons(self):
        ret = list(set([x[len(self.radical):] for x in self.words_list]))
        ret.sort()
        return ret

    @property
    def words_list(self):
        return self.get_words_list()

    def get_words_list(self, as_str=True):
        ppé = self.participe_pé
        ppt = self.participe_pt
        # todo: dans la ligne ci-dessous, je reconstruis les flex des participes, mais l'api n'est pas correcte pour les formes féminines...
        to_return = [self.infinitif, ppé, word_t(ppé.ort+"e", ppé.ort), word_t(ppé.ort+"es", ppé.ort), word_t(ppé.ort+"s", ppé.ort), ppt, word_t(ppt.ort+"s", ppt.ort), word_t(ppt.ort+"es", ppt.ort), word_t(ppt.ort+"e", ppt.ort)]
        for i in range(1, 5):
            for t in self.modes[i]:
                for f in self.modes[i][t]:
                    to_return.append(f)
        if as_str:
            to_return = [x.ort for x in to_return]
            to_return.sort()
        else:
            to_return.sort(key=lambda x: x.ort)
        return to_return
    
    #TODO version générateur
    def gen_words_list(self, as_str=True):
        ppé = self.participe_pé
        ppt = self.participe_pt
        # todo: dans la ligne ci-dessous, je reconstruis les flex des participes, mais l'api n'est pas correcte pour les formes féminines...
        to_return = [self.infinitif, ppé, word_t(ppé.ort+"e", ppé.ort), word_t(ppé.ort+"es", ppé.ort), word_t(ppé.ort+"s", ppé.ort), ppt, word_t(ppt.ort+"s", ppt.ort), word_t(ppt.ort+"es", ppt.ort), word_t(ppt.ort+"e", ppt.ort)]
        for i in range(1, 5):
            for t in self.modes[i]:
                for f in self.modes[i][t]:
                    to_return.append(f)
        if as_str:
            to_return = [x.ort for x in to_return]
            to_return.sort()
        else:
            to_return.sort(key=lambda x: x.ort)
        return to_return

    def __repr__(self):
        return "<verbe: {}>".format(self.infinitif.ort)

    #exemples: getMode("Indicatif") getMode("Indicatif:Présent"), getMode("Indicatif:Présent:1s"), getMode("Impératif:Présent:2p")
    def getMode(self, m, t=None):
        mode_s = ""
        temps_s = None
        personne_s = None
        personne_idx = 0
        mode = None
        if t is None:
            m = m.split(':')
            mode_s = m[0]
            if len(m) >= 2:
                temps_s = m[1]
            if len(m) == 3:
                personne_s = m[2]
        else:
            mode_s = m
            temps_s = t
        try:
            mode = VerbModeEnum[mode_s]
        except KeyError:
            raise Exception("mode inconnu: {}".format(mode_s))
        try:
            mode = self.modes[mode.getIndex()]
        except IndexError:
            raise Exception("mode {} inconnu du verbe {}".format(mode_s, self.infinitif))

        if temps_s is not None:
            if temps_s not in mode:
                raise Exception(f"temps {t} inconnu pour le mode {m[0]} du verbe {self.infinitif}")
            mode = mode[temps_s]

        if personne_s is not None:
            print(f"personne: {personne_s}")
            assert len(personne_s) == 2, "personne inconnue: " + personne_s
            assert personne_s == "on" or (personne_s[0] in ["1", "2", "3"] and personne_s[1].lower() in 'sp'), "personne inconnue: " + personne_s
            personne_idx = int(personne_s[0]) - 1
            if personne_s[1].lower() == 'p':
                personne_idx += 3

        if personne_idx==0:
            return mode
        else:
            if personne_idx < len(mode):
                return mode[personne_idx]
            else:
                return None

    @classmethod
    def get(cls, v):
        verb: Verb_info = None
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
                return verb.getMode(mode, temps)
            else:
                return verb.getMode(mode)
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


def search_gcd(wlist:list):
    ''' Return greatest comon prefix of all words in list'''
    def check_candidat(wlist, candidat):
        for w in wlist:
            if not w.startswith(candidat):
                return False
        return True
    min_len = min([len(w) for w in wlist])
    min_w = list(set([w[:min_len] for w in wlist]))
    while min_len > 0 and len(min_w) > 1:
        min_len -= 1
        min_w = list(set([w[:min_len] for w in wlist]))
    if min_len == 0 or len(min_w) == 0:
        return ""
    return min_w[0]


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

class Verb_flex:
    verb = None
    mode = None
    temps = None
    pronom = None
    def __unicode__(self):
        # w = self.verb.modes[self.mode][self.temps][self.pronom-1].ort
        w = "<{}:{}:{}:{}>".format(self.verb.infinitif,self.temps,self.mode,self.pronom-1)
        return w


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
