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
            raise Exception("Participe (%d) isn ot a valid mode" % VerbModeEnum.Participe.value)


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


# todo: verbes pronominaux
# todo: orthographes multiples (je déblaye/jé déblaie)
# todo: transitivité
# todo: antonymes/hyponymes/synonymes/champs lexicaux
class Verb_info:
    # verb_list = init_verb_list()
    verb_dict = []

    @property
    def participe_pé(self):
        return self.modes[VerbModeEnum.ParticipePé.getIndex()][0]

    @property
    def participe_pt(self):
        return self.modes[VerbModeEnum.ParticipePt.getIndex()][0]

    @property
    def infinitif(self):
        return self.modes[VerbModeEnum.Infinitif.getIndex()][0]

    def __init__(self, verbe_struct):
        self.modes = ["", "", "", "", "", "", ""]
        self.auxiliaire = AuxFlag.UNKNOWN
        self.transitivité = TransitFlag.UNKNOWN
        modes_list = ["In", "Im", "C", "S"]
        c_modes = [VerbModeEnum.Indicatif, VerbModeEnum.Impératif, VerbModeEnum.Conditionnel, VerbModeEnum.Subjonctif]
        # todo: ci-dessous comme ci-dessus
        # c_temps = []
        for m in modes_list:
            mode = c_modes[modes_list.index(m)].getIndex()
            self.modes[mode] = {}
            for t in verbe_struct[m]:
                # todo: ci-dessous comme ci-dessus
                temps = t
                self.modes[mode][temps] = []
                for x in verbe_struct[m][t]:
                    self.modes[mode][temps].append(word_t(x[0], x[1]))
        if verbe_struct["aux"] == "avoir":
            self.auxiliaire = AuxFlag.AVOIR
        if verbe_struct["aux"] == "être":
            self.aux = AuxFlag.ETRE
        self.modes[VerbModeEnum.Infinitif.getIndex()] = [verbe_struct['inf']]
        self.modes[VerbModeEnum.ParticipePt.getIndex()] = [verbe_struct["Part"]["Pr"]]
        self.modes[VerbModeEnum.ParticipePt.getIndex()] = [word_t(self.participe_pt[0], self.participe_pt[1])]
        self.modes[VerbModeEnum.ParticipePé.getIndex()] = [verbe_struct["Part"]["Pa"]]
        self.modes[VerbModeEnum.ParticipePé.getIndex()] = [word_t(self.participe_pé[0], self.participe_pé[1])]

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
        # todo: dans la ligne ci-dessous, j reconstruis les flex ddes participes, mais l'api n'est pas correcte pour les formes féminines...
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

    def getMode(self, m, t=None):
        mode_s = ""
        temps_s = None
        personne_s = None
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
                raise Exception("temps {} inconnu pour le mode {} du verbe {}".format(t, m[0], self.infinitif))
            mode = mode[temps_s]

        if personne_s is not None:
            assert len(personne_s) == 2, "personne inconnue: " + personne_s
            assert personne_s == "on" or (personne_s[0] in ["1", "2", "3"] and personne_s[1].lower() in 'sp'), "personne inconnue: " + personne_s
            idx = int(personne_s[0]) - 1
            if personne_s[1].lower() == 'p':
                idx += 1
            return mode[idx]
        return mode

    @classmethod
    def get(cls, v):
        verb = ""
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
        copyfile("data/verb_info_dict.dmp", "data/backup/verb_info_dict.dmp")
        f = open("data/verb_info_dict.dmp", "wb")
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


# init_verb_class()


def search_gcd(wlist):
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
