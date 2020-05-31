from enum import IntFlag, Enum, auto
from cw import word_t


class AuxFlag(IntFlag):
    ETRE = 1
    AVOIR = 2
    BOTH = 3
    UNKNOWN = 4


class TransitFlag(IntFlag):
    TRANSITIF = 1
    INTRANSITIF = 2
    UNKNOWN = 4


class VerbModeEnum(Enum):
    Infinitif=auto()
    Indicatif=auto()
    Subjonctif=auto()
    Conditionnel=auto()
    Impératif=auto()
    Participe=auto()


class VerbTempsEnum(Enum):
    Présent=auto()
    Passé=auto()
    Passé_simple=auto()
    Passé_composé=auto()
    Passé_antérieur=auto()
    Imparfait=auto()
    Plus_que_parfait=auto()
    Futur_simple=auto()
    Futur_antérieur=auto()




# todo: verbes pronominaux
# todo: transitivité
# todo: antonymes/hyponymes/synonymes/champs lexicaux
class Verb_info:
    auxiliaire=AuxFlag.UNKNOWN
    transitivité=TransitFlag.UNKNOWN
    participe_pt=""
    participe_pé=""
    infinitif = ""
    modes={}

    def __init__(self, verbe_struct):
        for m in ["In","Im","C","S"]:
            self.modes[m]={}
            for t in verbe_struct[m]:
                self.modes[m][t]=[]
                for x in verbe_struct[m][t]:
                    self.modes[m][t].append(word_t(x[0], x[1]))
        if verbe_struct["aux"]=="avoir":
            self.auxiliaire=AuxFlag.AVOIR
        if verbe_struct["aux"]=="être":
            self.aux=AuxFlag.ETRE
        self.infinitif=verbe_struct['inf']
        self.participe_pt = verbe_struct["Part"]["Pr"]
        self.participe_pé = verbe_struct["Part"]["Pa"]


class Verb_flex:
    verb = None
    mode = None
    temps = None
    pronom = None
    def __unicode__(self):
        # w = self.verb.modes[self.mode][self.temps][self.pronom-1].ort
        w = "<{}:{}:{}:{}>".format(self.verb.infinitif,self.temps,self.mode,self.pronom-1)
        return w
