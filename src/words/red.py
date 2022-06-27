import re
# from collections import namedtuple

from .words_tuple import word_info_t


def parcours_gramm(gramm_dict, fonction):
    for w in gramm_dict:
        for wt in gramm_dict[w]:
            fonction(wt)


def liste_natures(gramm_dict):
    nat = []

    def f(wt):
        if wt.nature not in nat:
            nat.append(wt.nature)
    parcours_gramm(gramm_dict, f)
    return nat


def filter_gramm(gramm_dict, nat=None):
    ret = []
    f_nat = nat
    if isinstance(nat,re.Pattern):
        f_nat = lambda x: nat.search(x)
    for w in gramm_dict:
        for wt in gramm_dict[w]:
            if f_nat(wt.nature):
                ret.append(w)
    return ret


def update_gramm(gramm_dict):
    for w in gramm_dict:
        flex = []
        for wt in gramm_dict[w]:
            wt_updated = word_info_t(nature=wt.nature, api=wt.api, genre=wt.genre, nbr=wt.nbr, lex=wt.lex, anto=wt.anto, hypo=wt.hypo, syno=wt.syno, desinences=wt.desinences, mot=w)
            flex.append(wt_updated)
        gramm_dict[w] = flex
