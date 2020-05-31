#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Canonical words module

functions to handle canonical words"""

import pickle

import requests
from bs4 import BeautifulSoup

import re
from bisect import bisect_left
from collections import namedtuple
word_info_t=namedtuple("word_info_t",["nature","api","genre","nbr","lex","anto","hypo","syno","desinences"],defaults=[""
,"","","",[],[],[],[],[]])
desinences_t=namedtuple("desinences_t",['ms','mp','fs','fp','rad'],defaults=['','','','',''])
word_t=namedtuple("word_t", ["ort", "api"])


def binary_search(a, x, lo=0, hi=None):
    hi = hi if hi is not None else len(a)
    pos = bisect_left(a, x, lo, hi)
    return (pos if (not pos == hi) and a[pos] == x else -1)


def auto_phonetics(node):
    if node.phonetics is None:
        p = extract_phonetic(node.cw)
        node.phonetics = p


def extract_phonetic(w):
    # TODO prepare w (unicode, espaces, accents)
    page = requests.get("https://fr.wiktionary.org/wiki/%s" % w)
    soup = BeautifulSoup(page.content, "html.parser")
    categram_spans = soup.find_all("span", class_="titredef", id=re.compile('^fr-'))
    spans = soup.find_all("span", class_="API", title="Prononciation API")
    prononciations = set()
    for s in spans:
        if s.find_previous("span", class_="sectionlangue").attrs['id'] == 'fr':
            prononciations.add(s.text[1:-1])
    return prononciations


def extract_word_phonetic(s):
    w = ""
    p = ""
    e = s.find('\\')
    w = s[:e]
    p = s[e + 1:]
    e = p.find('\\')
    p = p[:e]
    return w, p


def get_categrams(w):
    page = requests.get("https://fr.wiktionary.org/wiki/%s" % w)
    soup = BeautifulSoup(page.content, "html.parser")
    categram_spans = soup.find_all("span", class_="titredef", id=re.compile('^fr-'))
    return categram_spans


# return a list of <li> elements
# helper for extract infos, to find list of derived, synonyms, antonyms...
def _extract_list_elements(parent, list_name):
    html = parent.find_next("span", class_="titre" + list_name)
    # verifier que la liste correspond bien à la bonne sectionlangue
    #todo: c'est peut être la bonne langue mais pour un autre sens du mot ?
    if html is None or not html.find_previous("span", class_="sectionlangue") == parent.find_previous("span", class_="sectionlangue"):
        return []
    candidats = None
    candidats = html.find_next('div')
    previous_title = candidats.find_previous("span", class_=re.compile("titre"))
    # elements not in div (unique list ?)
    if not previous_title.attrs["class"] == "titre" + list_name:
        candidats = html.find_next("ul").find_all("li")
        # todo: another test yo ensure this is the good list
    else:
        candidats = [x.find_all("li") for x in candidats.find_all("ul")]
    return candidats


# génère la liste de toutes les flex du verbe
def verb_struct_all_words(vs):
    ret = []
    ret.append(vs['aux'])
    ret.append(vs['Part']['Pr'][0])
    ret.append(vs['Part']['Pa'][0])
    for temps in vs["In"]:
        for w in vs["In"][temps]:
            ret.append(w[0])
    for temps in vs["C"]:
        for w in vs["C"][temps]:
            ret.append(w[0])
    for temps in vs["Im"]:
        for w in vs["Im"][temps]:
            ret.append(w[0])
    for temps in vs["S"]:
        for w in vs["S"][temps]:
            ret.append(w[0])
    return list(set(ret))


# meilleur implémentation:
# faire une liste de tous les mots de tous les verbes
# cloner wlist de cette façon: on parcourt,
# et si w n'est pas dans la liste de verbes, on l'ajoute à la nouvelle liste
# complexité: o(log(n)) au lieu de o(n) dans cette version,
# car on n'invoque plu list.remove, on ne fait que des binary_search
def delete_verb_struct_from_list(wlist, verbs_struct):
    v_cnt = 0
    w_cnt = 0
    wlist.sort()
    for v in verbs_struct:
        verbs_struct[v]['inf'] = v
        v_cnt += 1
        all_words = verb_struct_all_words(verbs_struct[v])
        for w in all_words:
            if not binary_search(wlist, w) == -1:
                wlist.remove(w)
                w_cnt += 1
        if v_cnt % 50 == 0:
            print("*********verbe %d %s" % (v_cnt, v))
        if w_cnt % 100 == 0:
            print("verbe %s %d mots supprimés" % (v, w_cnt))
    return wlist


class champs_lex:
    all_champs = []

    def find(self, k):
        if isinstance(k, list):
            return [self.find(x) for x in k]
        if k not in self.all_champs:
            self.all_champs.append(k)
        return self.all_champs.index(k)


def extract_infos(w, all_champs_lex=[]):
    # TODO prepare w (unicode, espaces, accents)
    page = requests.get("https://fr.wiktionary.org/wiki/%s" % w)
    soup = BeautifulSoup(page.content, "html.parser")
    categram_spans = soup.find_all("span", class_="titredef", id=re.compile('^fr-'))
    #spans = soup.find_all("span", class_="API", title="Prononciation API")
    infos = []
    regex_nature=re.compile('[1-9]')

    for c in categram_spans:
        s = c.find_next("span", class_="API", title="Prononciation API")
        nature = c['id'][3:regex_nature.search(c['id']).span()[0]-1]
        if s is None:
            return []
        if s.find_previous("span", class_="sectionlangue").attrs['id'] == 'fr':
            if c['id'].startswith('fr-verb'):
                # todo: aller chercher toutes les déclinaisons si besoin
                infinitif = w
                # todo: pas assez robuste les tests sur champs lex
                champs_lex = set([x.text[1:-1] for x in c.find_next("ol").find_all("span", class_="term")])
                antonymes = [x.text for x in [x.find('a') for x in  _extract_list_elements(c, "anto")]]
                hyponymes = [x.text for x in [x.find('a') for x in  _extract_list_elements(c, "hypo")]]
                synonymes = [x.text for x in [x.find('a') for x in  _extract_list_elements(c, "syno")]]
                infos.append(word_info_t(nature, s.text[1:-1], '-', "-", champs_lex, antonymes, hyponymes, synonymes))
            elif c['id'].startswith('fr-flex-verb'):
                infinitif = c.find_next("th", colspan="3").find('i').text
                # todo: aller chercher toutes les déclinaisons si besoin
                infos.append(word_info_t(nature, s.text[1:-1], w, infinitif))
            elif c['id'].startswith('fr-nom-'):
                champs_lex = set([x.text[1:-1] for x in c.find_next("ol").find_all("span", class_="term")])
                antonymes = [x.text for x in [x.find('a') for x in  _extract_list_elements(c, "anto")]]
                hyponymes = [x.text for x in [x.find('a') for x in  _extract_list_elements(c, "hypo")]]
                synonymes = [x.text for x in [x.find('a') for x in  _extract_list_elements(c, "syno")]]
                genre = c.find_next('span', class_='ligne-de-forme')
                if genre is not None:
                    genre = genre.text
                    if genre == 'féminin':
                        genre = 'F'
                    else:
                        if genre == 'masculin':
                            genre = 'M'
                infos.append(word_info_t(nature, s.text[1:-1], genre, "S", champs_lex,antonymes,hyponymes,synonymes))
                pass
            elif c['id'].startswith('fr-flex-nom'):
                nombre_g = c.find_next('tr')
                if nombre_g is not None:
                    nombre_g = nombre_g.find_next('tr')
                if nombre_g is not None:
                    nombre_g = nombre_g.find_all('td')
                    # si la première case contient un selflink
                    # la forme est au singulier, sinon elle est au pluriel
                    cnt = 0
                    nbr = "?"
                    for td in nombre_g:
                        if td.find('a', class_="mw-selflink selflink") is not None:
                            if cnt == 0:
                                nombre_g = "S"
                            if cnt == 1:
                                nombre_g = "P"
                            break
                        cnt += 1

                genre = c.find_next('span', class_='ligne-de-forme')
                if genre is not None:
                    genre = genre.text
                    if genre == 'féminin':
                        genre = 'F'
                    else:
                        if genre == 'masculin':
                            genre = 'M'
                else:
                    genre = "?"
                infos.append(word_info_t(nature, s.text[1:-1], genre, nombre_g))
            elif c['id'].startswith("fr-adj"):
                genre = c.find_next('table', class_='flextable-fr-mfsp')
                tds_m = genre.find('tr', class_="flextable-fr-m").find_all('td')
                tds_f = genre.find('tr', class_="flextable-fr-f").find_all('td')
                masc = [x.text for x in tds_m]
                fem = [x.text for x in tds_f]
                ms = extract_word_phonetic(masc[0])
                mp = extract_word_phonetic(masc[1])
                fs = extract_word_phonetic(fem[0])
                fp = extract_word_phonetic(fem[1])
                rad = ""
                if mp[0].startswith(ms[0]):
                    mp = ("+"+mp[0][len(ms[0]):], mp[1])
                    pass
                if fs[0].startswith(ms[0]):
                    # exemple: petit, grand, factuel
                    if fp[0].startswith(fp[0]):
                        fp = ("+"+fp[0][len(ms[0]):], fp[1])
                    fs = ("+"+fs[0][len(ms[0]):], fs[1])
                else:
                    # exemple: inclusif
                    i = 0
                    while ms[0][i] == fs[0][i]:
                        i += 1
                    if i == len(ms[0])-1:
                        fs = ("-" + fs[0][i:], fs[1])
                        fp = ("-" + fs[0][i:], fp[1])
                        pass
                    else:
                        # cas relou, j'ai pas encore d'exemple
                        rad = ms[0][:i]
                        ms = ("+" + ms[0][i:], ms[1])
                        mp = ("+" + mp[0][i:], mp[1])
                        fs = ("+" + fs[0][i:], fs[1])
                        fp = ("+" + mp[0][i:], fp[1])
                        if len(rad) == 0:
                            # pas de radical commun entre masculin et feminin
                            # je sais même pas si un mot comme ça existe
                            pass
                desin = desinences_t(ms=ms, mp=mp, fs=fs, fp=fp)
                champs_lex = set([x.text[1:-1] for x in c.find_next("ol").find_all("span", class_="term")])
                antonymes = [x.text for x in [x.find('a') for x in  _extract_list_elements(c, "anto")]]
                hyponymes = [x.text for x in [x.find('a') for x in  _extract_list_elements(c, "hypo")]]
                synonymes = [x.text for x in [x.find('a') for x in  _extract_list_elements(c, "syno")]]
                infos.append(word_info_t(nature, desin.ms[1], "M", "S", champs_lex, antonymes, hyponymes, synonymes, desin))
                pass
            elif c['id'].startswith("fr-adv") or c['id'].startswith("fr-conj"):
                champs_lex = set([x.text[1:-1] for x in c.find_next("ol").find_all("span", class_="term")])
                antonymes = [x for x in [x.text for x in [x.find('a') for x in  _extract_list_elements(c, "anto")]]if not " " in x]
                hyponymes =  [x for x in [x.text for x in [x.find('a') for x in  _extract_list_elements(c, "hypo")]]if not " " in x]
                synonymes =  [x for x in [x.text for x in [x.find('a') for x in  _extract_list_elements(c, "syno")]]if not " " in x]
                infos.append(word_info_t(nature, s.text[1:-1], "-", "-", champs_lex,antonymes,hyponymes,synonymes, None))
                pass
            else:
                infos.append(word_info_t(nature, s.text[1:-1]))
    return infos


def extract_verb_info_wiki(v):
    # todo gérer les verbes intransitif et ceux qui n'ont que quelques pronoms
    # todo gérer les verbes composés ?
    page = requests.get("https://fr.wiktionary.org/wiki/Annexe:Conjugaison_en_français/%s" % v)
    soup = BeautifulSoup(page.content,"html.parser")
    def extract_temps(table):
        lines = table.find_all("tr")
        temps = lines[0].text.strip("\n")
        # print("****************** %s *******************" % temps)
        if temps in ["Passé", "Passé composé", "Plus-que-parfait", "Passé antérieur", "Futur antérieur"]:
            return (temps,[])
        desinences = []
        i1 = 1
        i2 = 3
        if len(lines) == 4:
            i2 = 2
        if len(lines) == 7 or len(lines) == 4:
            for l in lines[1:]:
                tds = l.find_all("td")
                # print("################# %d %s" % (len(tds), l.text))
                tds = l.find_all("td")
                w = tds[i1].text.strip("\n").strip("\\").strip("\xa0")
                api = tds[i2].text.strip("\n").strip("\\").strip("\xa0")
                # print("%s %s" % (w, api))
                desinences.append((w, api))
            pass
        return (temps, desinences)
    v_info={}
    modes_imp = soup.find("span", id="Modes_impersonnels")
    auxiliaire = ""
    # todo: gérer le cas des doubles auxiliaires
    infinitif_html = modes_imp.find_next("a", title="infinitif")
    while not infinitif_html.name == 'tr':
        infinitif_html = infinitif_html.parent
    infinitif_html = infinitif_html.find_all("td")
    auxiliaire = infinitif_html[4].text.strip("\n").strip("\\").strip("\xa0")
    v_info["aux"] = auxiliaire
    participe_row = modes_imp.find_next("a", title="participe")
    while not participe_row.name == 'tr':
        participe_row = participe_row.parent
    participe_html = participe_row.find_all('td')
    ppt = (participe_html[2].text, participe_html[3].text)
    ppt = (ppt[0].strip("\n").strip("\\").strip("\xa0"), ppt[1].strip("\n").strip("\\").strip("\xa0"))
    ppé = (participe_html[5].text, participe_html[6].text)
    ppé = (ppé[0].strip("\n").strip("\\").strip("\xa0"), ppé[1].strip("\n").strip("\\").strip("\xa0"))
    v_info["Part"] = {"Pr":ppt, "Pa":ppé}
    indic = soup.find("span", id="Indicatif").find_next("div").find("table").find_all("table")
    v_info['In']={}
    v_info['S']={}
    v_info['C']={}
    v_info['Im']={}
    for t in indic:
        temps = extract_temps(t)
        v_info['In'][temps[0]]=temps[1]
    subj = soup.find("span", id="Subjonctif").find_next("div").find("table").find_all("table")
    for t in subj:
        temps = extract_temps(t)
        v_info['S'][temps[0]]=temps[1]
    cond = soup.find("span", id="Conditionnel").find_next("div").find("table").find_all("table")
    for t in cond:
        temps = extract_temps(t)
        v_info['C'][temps[0]]=temps[1]
    impé = soup.find("span", id="Impératif").find_next("div").find("table").find_all("table")
    for t in impé:
        temps = extract_temps(t)
        v_info['Im'][temps[0]]=temps[1]
    return v_info


# def extract_verb_info(v):
#     page=requests.get("https://conjugueur.reverso.net/conjugaison-francais-verbe-%s.html" % v)
#     soup=BeautifulSoup(page.content,"html.parser")
#     modes = soup.find_all('div', class_="blue-box-wrap")
#     auxiliaire = soup.find_all('span', id="ch_lblAuxiliary")[0].text
#     v_info = {'modes':{'In':{},
#                         'S':{},
#                         'C':{},
#                         'Im':{}},
#                 'participes':{"Pr":"",'Pa':{}},
#                 'aux':auxiliaire
#             }
#     for m in modes:
#         t = m['mobile-title']
#         desinences = [x.text for x in m.find_all("i", class_="verbtxt")]
#         if not t.find("Indicatif") == -1:
#             if not t.find("Présent") == -1:
#                 v_info['modes']['In']['P'] = desinences
#                 pass
#             if not t.find("Imparfait") == -1:
#                 v_info['modes']['In']['I'] = desinences
#                 pass
#             if not t.find("Futur") == -1:
#                 v_info['modes']['In']['F'] = desinences
#                 pass
#             if not t.find("Passé simple") == -1:
#                 v_info['modes']['In']['PS'] = desinences
#                 pass
#         if not t.find("Subjonctif") == -1:
#             if not t.find("Présent") == -1:
#                 v_info['modes']['S']['P'] = desinences
#                 pass
#             if not t.find("Imparfait") == -1:
#                 v_info['modes']['S']['I'] = desinences
#                 pass
#         if not t.find("Conditionnel") == -1:
#             if not t.find("Présent") == -1:
#                 v_info['modes']['C']['P'] = desinences
#                 pass
#             #if not t.find("Passé première forme") == -1:
#                 #v_info['modes']['C']['P1'] = desinences
#                 #pass
#             #if not t.find("Passé deuxième forme") == -1:
#                 #v_info['modes']['C']['P2'] = desinences
#                 #pass
#         if not t.find("Impératif") == -1:
#             if not t.find("Présent") == -1:
#                 v_info['modes']['Im']['Pr'] = desinences
#                 pass
#         if not t.find('Participe') == -1:
#             if not t.find('Présent') == -1:
#                 v_info['participes']['Pr'] = m.find('i',class_='verbtxt').text
#             if not t.find('Passé') == -1 and t.find("composé") == -1:
#                 pp = m.find_all('i',class_='verbtxt')
#                 if len(pp) == 4:
#                     v_info['participes']['Pa']['ms'] = pp[0].text
#                     v_info['participes']['Pa']['mp'] = pp[1].text
#                     v_info['participes']['Pa']['fs'] = pp[2].text
#                     v_info['participes']['Pa']['fp'] = pp[3].text
#                 elif len(pp)==1:
#                     v_info['participes']['Pa']['ms'] = pp[0].text
#                     v_info['participes']['Pa']['mp'] = pp[0].text
#                     v_info['participes']['Pa']['fs'] = pp[0].text
#                     v_info['participes']['Pa']['fp'] = pp[0].text
#                 else:
#                     return None
#     return v_info







def kill_accents(word):
    """Replaces all accents"""
    word = word.replace("ç", "c")
    word = word.replace("é", "e")
    word = word.replace("è", "e")
    word = word.replace("ê", "e")
    word = word.replace("ë", "e")
    word = word.replace("â", "a")
    word = word.replace("à", "a")
    word = word.replace("ï", "i")
    word = word.replace("î", "i")
    word = word.replace("ô", "o")
    word = word.replace("ö", "o")
    word = word.replace("û", "u")
    word = word.replace("ü", "u")
    word = word.replace("ù", "u")
    return word


def sanitize_word(word):
    word = word.lower()
    word = kill_accents(word)
    word = word.replace(" ", "")
    word = word.replace("\t", "")
    word = word.replace("\n", "")
    word = word.replace("-", "")
    return word


def getCanonicForm(word):
    """Return canonical version of word"""
    word = sanitize_word(word)
    s1 = {}
    for c in word:
        if c in s1:
            s1[c] = s1[c] + 1
        else:
            s1[c] = 1
    ret_string = ""
    keys = list(s1.keys())
    keys.sort()
    for c in keys:
        ret_string += (c * s1[c])
    return ret_string


def getCanonical(word):
    return getCanonicForm(word)


def can_write(cw1, cw2):
    """Return true if all characters of cw1 are in cw2"""
    i = 0
    i_max = len(cw1)
    founds = 0
    for c in cw2:
        found = False
        while i < i_max:
            if cw1[i] == c:
                found = True
                founds += 1
                # print "found " + c
                break
            else:
                i += 1
        if founds == len(cw2):
            return True
        if not found:
            return False
        else:
            i += 1
        if i >= i_max:
            return False


def difference(cw1, cw2):
    """Return cw2 - cw1"""
    i = 0
    result = ""
    if cw1 == '':
        return cw2
    for c in cw1:
        while not cw2[i] == c:
            result += cw2[i]
            i += 1
            if i >= len(cw2):
                break
        i += 1
    while i < len(cw2):
        result += cw2[i]
        i += 1
    return result


def intersect(cw1, cw2):
    """Return all characters in cw1 AND cw2"""
    diff = ""
    for c in cw1:
        if c in cw2:
            # add c in returned string
            diff += c
            # delete c from cw2
            idx = cw2.index(c)
            cw2 = cw2[0:idx] + cw2[idx + 1:]
    return diff


_voyelles = "aeiouy"


from collections import defaultdict, namedtuple

# chunk = namedtuple('WordChunk',['text','occ'])


def chunkify(word):
    if '-' in word:
        r = []
        for w in word.split('-'):
            r += chunkify(w)
        return r

    canonic_word = word.lower()
    canonic_word = kill_accents(canonic_word)
    type_lettre_courante = canonic_word[0] in _voyelles  # True if voyelle
    chunks = []
    current_chunk = ""
    i = 0
    while i < len(word):
        c = canonic_word[i]
        type_c = c in _voyelles
        if type_lettre_courante == type_c:
            current_chunk += c
        else:
            chunks.append(current_chunk)
            current_chunk = c
            type_lettre_courante = type_c
            pass
        i += 1
    chunks.append(current_chunk)
    return chunks


def f_filter_start(ratio):
    def to_ret(chunks, chunks_start, chunks_end, k):
        return ratio < (chunks_start[k]*1.0/chunks[k])
    return to_ret


def filter_chunks_by(chunks, chunks_start, chunks_end, f_filter):
    for k in chunks:
        if f_filter(chunks, chunks_start, chunks_end, k):
            yield k


def syllabes(word):
    if isinstance(word, list):
        return [_syllabes(x) for x in word]
    return _syllabes(word)


def _syllabes(word):
    sons = chunkify(word)
    i = 0
    if len(sons) > 1:
        if not sons[0][0] in _voyelles:
            sons[1] = sons[0] + sons[1]
            del sons[0]
        else:
            if len(sons[1]) > 1:
                sons[0] += sons[1][0]
                sons[1] = sons[1][1:]

        if sons[-1][0] in _voyelles:
            sons[-2] += sons[-1]
            del sons[-1]

    while i < len(sons) - 1:
        s1 = sons[i]
        s2 = sons[i+1]
        if s1[-1] in "aeo":
            if (s2[0] in 'nm'):
                if (((len(s2) <= 1  or not s2[1] in 'nm')and len(sons) == i + 2)):
                    # todo#################################################
                    s1 += s2[0]
                    s2 = s2[1:]
        if len(s2) > 1:
            if len(s2) >= 2  and (s2[0] != s2[1] and not s2[1] in _voyelles and s2[1] != 'h'):
                if(not(s2 in ['gn']or s2[1] == 'r')):
                    s1 += s2[0]
                    s2 = s2[1:]
            elif s2.startswith('ll'):
                s1 += s2
                s2 = ''
            # if s2[0]=='r' and not s2[1]=='r':
            #     s1+='r'
            #     s2=s2[1:]
        sons[i] = s1
        sons[i+1] = s2

        i += 2
    i = 1
    while i < len(sons)-1:
        sons[i] += sons[i+1]
        del sons[i+1]
        i+=1
    if sons[-1] in 'rtsxz' and len(sons) >= 2:
        sons[-2] += sons[-1]
        del sons[-1]

    r = []
    i1 = 0
    for s in sons:
        i2 = len(s)
        r.append(word[i1:i1+i2])
        i1 += i2

    return r

def vc_set(words):
    import random
    vs = set()
    cs = set()
    i = 0
    t = 1000 + random.randrange(-150, 150)
    chunks = defaultdict(int)
    chunks_start = defaultdict(int)
    chunks_end = defaultdict(int)
    for w in words:
        vc = chunkify(w)
        chunks_start[vc[0]] += 1
        chunks_end[vc[-1]] += 1
        for e in vc:
            chunks[e] += 1
            if kill_accents(e[0]) in _voyelles:
                vs.add(e)
            else:
                cs.add(e)
        i += 1
        if i % t == 0:
            print("%d %s" % (i, w))
    return vs, cs, chunks, chunks_start, chunks_end


def set_syllabes(words):
    all_syllabes = set()
    i = 0
    for w in words:
        for s in syllabes(w):
            all_syllabes.add(s)
        i += 1
        if i % 1000 == 0:
            print("%d %s" % (i, w))
    return all_syllabes


def statistiques(vs, cs, chunks, chunks_start, chunks_end, kkk=None):
    if kkk is None:
        kkk = list(chunks.keys())
    for k in kkk:
        print("%3s %7d %7d %7d %7f %7f" % (k,chunks[k],chunks_start[k],chunks_end[k],chunks_start[k]*1.0/chunks[k],chunks_end[k]*1.0/chunks[k]))


def read_words_list(fname="data/words_list.dmp"):
    f = open(fname,"rb")
    l = pickle.load(f)
    f.close()
    return l


def search_ascii_primes(t=[37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,113], s=[251,257,263,269]):
    ret = []
    for a in t:
        for b in t:
            if not b == a:
                for c in t:
                    if not c == b and not c == a and a + b + c in s:
                        u = [a, b, c]
                        u.sort()
                        ret.append((chr(u[0]), chr(u[1]), chr(u[2]), a + b + c))
    return set(ret)


def valeur_numerique(w):
    w = w.lower()
    w = kill_accents(w)
    s = 0
    for c in w:
        if c.isalpha():
            s += ord(c) - 96
    return s
