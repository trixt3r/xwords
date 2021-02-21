import pickle
import time
import os.path
import random
import re
from shutil import copyfile

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet

from words_tuple import word_t, word_info_t, desinences_t, flex_adj
from verb import Verb_info
from cw import binary_search


# extrait les infos du mot w depuis une page wiktionnary
def extract_infos(w, all_champs_lex=[]):
    # TODO prepare w (unicode, espaces, accents)
    page = requests.get("https://fr.wiktionary.org/wiki/%s" % w)
    # page = requests.get("http://192.168.43.125:8181/wiktionary_fr_all_nopic_2020-10/A/%s" % w)
    soup = BeautifulSoup(page.content, "html.parser")
    categram_spans = soup.find_all("span", class_="titredef", id=re.compile('^fr-'))
    infos = []
    regex_nature = re.compile('[1-9]')

    for c in categram_spans:
        s = c.find_next("span", class_="API", title="Prononciation API")
        if s is None:
            return []
        nature = c['id'][3:regex_nature.search(c['id']).span()[0]-1]
        api = s.text[1:-1]
        champs_lex = set([x.text[1:-1] for x in c.find_next("ol").find_all("span", class_="term")])
        antonymes = [x.text for x in [x.find('a') for x in _extract_list_elements(c, "anto")] if x is not None]
        hyponymes = [x.text for x in [x.find('a') for x in _extract_list_elements(c, "hypo")] if x is not None]
        synonymes = [x.text for x in [x.find('a') for x in _extract_list_elements(c, "syno")] if x is not None]

        if s.find_previous("span", class_="sectionlangue").attrs['id'] == 'fr':
            info_t = None
            if c['id'].startswith('fr-verb'):
                # todo: aller chercher toutes les déclinaisons si besoin
                infinitif = w
                # todo: pas assez robuste les tests sur champs lex
                info_t = word_info_t(nature, api, '-', "-", lex=champs_lex, anto=antonymes, hypo=hyponymes, syno=synonymes, mot=w)
            elif c['id'].startswith('fr-nom-'):
                genre = _extract_nom_genre(c)
                info_t = word_info_t(nature, api, genre, "S", lex=champs_lex, anto=antonymes, hypo=hyponymes, syno=synonymes, mot=w)
            elif c['id'].startswith("fr-adj"):
                desin = _extract_adj_desinences(c, w)
                if isinstance(desin, word_t):
                    # adjectif invariable
                    info_t = word_info_t(nature, api, "I", "I", lex=champs_lex, anto=antonymes, hypo=hyponymes, syno=synonymes, desinences=None, mot=w)
                else:
                    info_t = word_info_t(nature, api, "M", "S", lex=champs_lex, anto=antonymes, hypo=hyponymes, syno=synonymes, desinences=desin, mot=w)
            elif c['id'].startswith('fr-flex-verb'):
                # todo: robustesse
                infinitif = c.find_next("th", colspan="3").find('i').text
                info_t = word_info_t(nature, api, w, infinitif, mot=w)
            elif c['id'].startswith('fr-flex-nom'):
                nombre = _extract_nombre(c)
                genre = _extract_nom_genre(c)
                info_t = word_info_t(nature, api, genre, nombre, lex=champs_lex, anto=antonymes, hypo=hyponymes, syno=synonymes, mot=w)
            # elif c['id'].startswith('fr-flex-adj'):
            #     lis = c.find_next("ol").find_all("li")
            #     if lis.len > 1:
            #         pass
            #     else:
            #         ms = lis[0].find("a").text
            #         tmp = lis[0].text.split(" ")
            #         if tmp[0].lower() == "féminin":
            #             genre = "F"
            #         elif tmp[0].lower() == "masculin":
            #             genre = "M"
            #         else:
            #             genre = None
            #         if tmp[1].lower() == "singulier":
            #             nombre = "S"
            #         elif tmp[1].lower() == "pluriel":
            #             nombre = "P"
            #         else:
            #             nombre = None
            #         # attention, je ne passe pas le masculin singulier, il est "perdu"
            #         # on pourrait le passer dans un des champs de tag ? genre, synonyme
            #         info_t = word_info_t(nature, api, genre, nombre, syno=[ms], mot=w)
            elif c['id'].startswith("fr-adv") or c['id'].startswith("fr-conj"):
                info_t = word_info_t(nature, api, "-", "-", lex=champs_lex, anto=antonymes, hypo=hyponymes, syno=synonymes, mot=w)
                pass
            else:
                # TODO: ARTICLES, PRONOMS, ...
                info_t = word_info_t(nature, api, lex=champs_lex, anto=antonymes, hypo=hyponymes, syno=synonymes, mot=w)
            if info_t is not None:
                for elt in info_t:
                    if isinstance(elt, Tag) or isinstance(elt, ResultSet):
                        append_bs4_error(w)
                        return None
                        pass
                infos.append(info_t)
    return infos


def append_bs4_error(w):
    f = open("data/bs4_error.dmp", "ab")
    pickle.dump(w, f)
    f.close()


def extract_verb_info_wiki(v):
    # todo gérer les verbes intransitif et ceux qui n'ont que quelques pronoms
    # todo gérer les verbes composés ?
    page = requests.get("https://fr.wiktionary.org/wiki/Annexe:Conjugaison_en_français/%s" % v)
    # page = requests.get("http://192.168.43.125:8181/wiktionary_fr_all_nopic_2020-10/A/%s" % v)
    soup = BeautifulSoup(page.content, "html.parser")

    def extract_temps(table):
        lines = table.find_all("tr")
        temps = lines[0].text.strip("\n")
        # print("****************** %s *******************" % temps)
        if temps in ["Passé", "Passé composé", "Plus-que-parfait", "Passé antérieur", "Futur antérieur"]:
            return (temps, [])
        desinences = []
        i1 = 1
        i2 = 3
        if len(lines) == 4:
            i2 = 2
        if len(lines) == 7 or len(lines) == 4:
            for line in lines[1:]:
                tds = line.find_all("td")
                # print("################# %d %s" % (len(tds), l.text))
                tds = line.find_all("td")
                w = tds[i1].text.strip("\n").strip("\xa0").strip("\\")
                api = tds[i2].text.strip("\n").strip("\\").strip("\xa0")
                # print("%s %s" % (w, api))
                desinences.append((w, api))
            pass
        return (temps, desinences)
    v_info = {}
    modes_imp = soup.find("span", id="Modes_impersonnels")
    if modes_imp is None:
        return None
    auxiliaire = ""
    # todo: gérer le cas des doubles auxiliaires
    infinitif_html = modes_imp.find_next("a", title="infinitif")
    while not infinitif_html.name == 'tr':
        infinitif_html = infinitif_html.parent
    infinitif_html = infinitif_html.find_all("td")
    v_info["inf"] = word_t(v, infinitif_html[3].text.strip("\n").strip("\xa0").strip("\\"))
    auxiliaire = infinitif_html[4].text.strip("\n").strip("\\").strip("\xa0").strip("\n")
    v_info["aux"] = auxiliaire
    participe_row = modes_imp.find_next("a", title="participe")
    while not participe_row.name == 'tr':
        participe_row = participe_row.parent
    participe_html = participe_row.find_all('td')
    ppt = (participe_html[2].text, participe_html[3].text)
    ppt = (ppt[0].strip("\n").strip("\xa0"), ppt[1].strip("\n").strip("\xa0").strip("\\"))
    ppé = (participe_html[5].text, participe_html[6].text)
    ppé = (ppé[0].strip("\n").strip("\xa0"), ppé[1].strip("\n").strip("\xa0").strip("\\"))
    v_info["Part"] = {"Pr": ppt, "Pa": ppé}
    indic = soup.find("span", id="Indicatif").find_next("div").find("table").find_all("table")
    v_info['In'] = {}
    v_info['S'] = {}
    v_info['C'] = {}
    v_info['Im'] = {}
    for t in indic:
        temps = extract_temps(t)
        v_info['In'][temps[0]] = temps[1]
    subj = soup.find("span", id="Subjonctif").find_next("div").find("table").find_all("table")
    for t in subj:
        temps = extract_temps(t)
        v_info['S'][temps[0]] = temps[1]
    cond = soup.find("span", id="Conditionnel").find_next("div").find("table").find_all("table")
    for t in cond:
        temps = extract_temps(t)
        v_info['C'][temps[0]] = temps[1]
    impé = soup.find("span", id="Impératif").find_next("div").find("table").find_all("table")
    for t in impé:
        print(t)
        temps = extract_temps(t)
        v_info['Im'][temps[0]] = temps[1]
    return v_info


def make_info_list(wlist=[]):
    """
    LA grosse fonction, qui prend une lsite de mots en entrée, et enrichit le dictionnaire
    en allant chercher les infos sur wiktionnary
    en tous cas elle est senée le faire.
    """
    def make_info_save(courants, error):
        gramm = {}
        if os.path.isfile("data/gramm.dmp"):
            copyfile("data/gramm.dmp", "data/backup/gramm.dmp")
            f = open("data/gramm.dmp", "rb")
            gramm = pickle.load(f)
            f.close()
        remains = []
        if os.path.isfile("data/remains_list.dmp"):
            copyfile("data/remains_list.dmp", "data/backup/remains_list.dmp")
            f = open("data/remains_list.dmp", "rb")
            remains = pickle.load(f)
            f.close()
        for k in courants:
            gramm[k] = courants[k]
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$ %s %s" % (k, gramm[k]))
            i = binary_search(remains, k)
            if not i == -1:
                del remains[i]
        f = open("data/gramm.dmp", "wb")
        pickle.dump(gramm, f)
        f.close()
        print("save %d " % len(gramm))
        f = open("data/remains_list.dmp", "wb")
        pickle.dump(remains, f)
        f.close()
        print("remains %d" % len(remains))
        nf = []
        if os.path.isfile("data/gramm_not_found.dmp"):
            copyfile("data/gramm_not_found.dmp", "data/backup/gramm_not_found.dmp")
            f = open("data/gramm_not_found.dmp", "rb")
            nf = pickle.load(f)
            f.close()
        nf += error
        nf = list(set(error))
        nf.sort()
        f = open("data/gramm_not_found.dmp", "wb")
        pickle.dump(nf, f)
        f.close()
        return
    if wlist == []:
        if os.path.isfile('data/remains_list.dmp'):
            f = open('data/remains_list.dmp', "rb")
            wlist = pickle.load(f)
            f.close()
    blacklist = []
    courants = {}
    error_list = []
    cnt = 1
    f = open("data/gramm.dmp", "rb")
    dico = pickle.load(f)
    f.close()
    liste_verbes = Verb_info.full_words_list()
    infos = None
    for w in wlist:
        if w in dico or w in liste_verbes:
            continue
        if cnt % 100 == 0:
            make_info_save(courants, error_list)
            cnt+=1
            error_list = []
        if not binary_search(blacklist, w) == -1:
            print("esquivé: %s" % w)
            continue
            pass
        infos = None
        try:
            infos = extract_infos(w)
        except:
            w = w.lower()
            try:
                infos = extract_infos(w)
            except:
                print("error: %s" % w)
                error_list.append(w)
                pass

        if(infos is None):
            error_list.append(w)
            print("error: %s" % w)
            continue
        # to know if w is only a verb or verb flex
        verb_only = True
        for cat in infos:
            # if not cat.nature.find("flex-adj") == -1:
            #     ms = cat.syno[0]
            #     if ms in courants:
            #         pass
            #     else:
            #         pass

            # forme de verbe ou verbe infinitif
            if not cat.nature.find("verb") == -1:
                verb = ""

                if not cat.nature.find("flex-verb") == -1:
                    verb = cat[3]
                    print("form de verbe: %s %s" % (w, verb))
                    print(Verb_info.get(verb))
                else:
                    verb = w
                # si le verbe n'est pas dans la liste, aller chercher sa conjugaison
                if Verb_info.get(verb) is None:
                    print(cat)
                    print("new verb: %s" % verb)
                    v_s = extract_verb_info_wiki(verb)
                    if v_s is None:
                        error_list.append(verb)
                        error_list.append(w)
                        error_list.sort()
                    else:
                        v_i = Verb_info(v_s)
                        Verb_info.add(v_i)
                        blacklist += v_i.words_list
                        blacklist = list(set(blacklist))
                        blacklist.sort()
                        # print(blacklist)
                        _remains = []
                        if os.path.isfile("data/remains_list.dmp"):
                            f = open("data/remains_list.dmp", "rb")
                            _remains = pickle.load(f)
                            f.close()
                        for k in blacklist:
                            i = binary_search(_remains, k)
                            if not i == -1:
                                del _remains[i]
                        f = open("data/remains_list.dmp", "wb")
                        pickle.dump(_remains, f)
                        f.close()
                else:
                    v_i = Verb_info.get(verb)
                    # print(v_i.words_list)
                    blacklist += v_i.words_list
                    blacklist = list(set(blacklist))
                    blacklist.sort()
                    # print(blacklist)

            else:
                # v_i = Verb_info.get(verb)
                # blacklist += v_i.words_list
                # blacklist = list(set(blacklist))
                # blacklist.sort()
                verb_only = False
        if not verb_only:
            print("ajout mot courant %s " % w)
            courants[w] = infos
        print("%d %s %d ok" % (cnt, w, len(infos)))
        cnt += 1
    # at last! end of list
    make_info_save(courants, error_list)
    pass


# fonction pur découvrir et éradiquer le bug qui fait qu'un élément bs4
# se retrouve dans mes objets à sauvegarder
def track_extract_bug(wlist):
    for w in wlist:
        infos = extract_infos(w)
        print(w)
        print(infos)
        f = open("data/tmp.dmp", "wb")
        pickle.dump(infos, f)
        f.close()


# creates verbes structure from wikipedia
def make_verb_list(verb_list=None):
    def save(verbs, errors):
        f = open('data/verbes_struct.dmp', 'wb')
        pickle.dump(verbs, f)
        f.close()
        f = open('data/verbes_struct_errors.dmp', 'wb')
        pickle.dump(errors, f)
        f.close()
    errors = []
    if verb_list is None:
        f = open('data/liste_verbes_1979.dmp', "rb")
        verb_list = pickle.load(f)
        f.close()
    if isinstance(verb_list, str):
        f = open(verb_list, "rb")
        verb_list = pickle.load(f)
        f.close()
    verbs = {}
    # loading already known verbs
    if os.path.isfile("data/verbes_struct.dmp"):
        f = open("data/verbes_struct.dmp", "rb")
        verbs = pickle.load(f)
        f.close()
        for v in verbs:
            if v in verb_list:
                verb_list.remove(v)
    # loading error verbs list
    if os.path.isfile("data/verbes_struct_errors.dmp"):
        f = open("data/verbes_struct_errors.dmp", "rb")
        errors = pickle.load(f)
        f.close()
        for v in errors:
            if v in verb_list:
                verb_list.remove(v)
    # treat verb list
    c = 0
    for v in verb_list:
        if v.startswith("se "):
            errors.append(v)
            print("verbe pronominal: %s" % v)
            continue
        if Verb_info.get(v) is not None:
            print("je l'ai déjà: %s" % v)
            continue
        try:
            verbs[v] = extract_verb_info_wiki(v)
            Verb_info.add(Verb_info(verbs[v]))
            print("%s ok" % v)
        except:
            errors.append(v)
            print("error : %s" % v)
            continue
        print(v)
        c += 1
        if c % 10 == 0:
            save(verbs, errors)
            print("tmp save %d" % c)
        time.sleep(random.randrange(3000) / 1000)
    save(verbs, errors)



def get_categrams(w):
    page = requests.get("https://fr.wiktionary.org/wiki/%s" % w)
    # page = requests.get("http://192.168.43.125:8181/wiktionary_fr_all_nopic_2020-10/A/%s" % w)

    soup = BeautifulSoup(page.content, "html.parser")
    categram_spans = soup.find_all("span", class_="titredef", id=re.compile('^fr-'))
    return categram_spans



# meilleur implémentation:
# faire une liste de tous les mots de tous les verbes
# cloner wlist de cette façon: on parcourt,
# et si w n'est pas dans la liste de verbes, on l'ajoute à la nouvelle liste
# complexité: o(log(n)) au lieu de o(n) dans cette version,
# car on n'invoque plu list.remove, on ne fait que des binary_search
# def delete_verb_struct_from_list(wlist, verbs_struct):
#     v_cnt = 0
#     w_cnt = 0
#     wlist.sort()
#     for v in verbs_struct:
#         verbs_struct[v]['inf'] = v
#         v_cnt += 1
#         all_words = verb_struct_all_words(verbs_struct[v])
#         for w in all_words:
#             if not binary_search(wlist, w) == -1:
#                 wlist.remove(w)
#                 w_cnt += 1
#         if v_cnt % 50 == 0:
#             print("*********verbe %d %s" % (v_cnt, v))
#         if w_cnt % 100 == 0:
#             print("verbe %s %d mots supprimés" % (v, w_cnt))
#     return wlist


class champs_lex:
    all_champs = []

    def find(self, k):
        if isinstance(k, list):
            return [self.find(x) for x in k]
        if k not in self.all_champs:
            self.all_champs.append(k)
        return self.all_champs.index(k)


def extract_adj_desinences(categ, w):
    return _extract_adj_desinences(categ, w)


def _extract_adj_desinences(categ, w):
    msi = False
    tmp = categ.find_next("span", class_="ligne-de-forme")
    if tmp is not None:
        tmp = tmp.text
    if tmp == 'masculin et féminin identiques':
        msi = True

    genre = categ.find_next('table', class_='flextable-fr-mfsp')
    if genre is None:
        genre = categ.find_next('table', class_='flextable')
        if genre.find_all('tr')[0].text.strip("\n") == "Invariable":
            adj = genre.find_all('tr')[1].text.strip("\n").split("\\")
            return word_t(adj[0], adj[1])
            # return desinences_t(word_t(adj[0], adj[1]),word_t(adj[0], adj[1]),word_t(adj[0], adj[1]),word_t(adj[0], adj[1]))
    trs = genre.find_all('tr')
    if "colspan" in trs[-1].find_all('td')[0].attrs:
        msi = True
    masc = None
    fem = None
    ms = None
    mp = None
    fs = None
    fp = None
    api = None
    if genre is None:
        # return desinences_t(ms=word_t("", ""), mp=word_t("", ""),fs=word_t("", ""),fp=word_t("", ""))
        raise Exception("Erreur pas de désinences")
    if msi is True:
        i = 0

        while i < len(trs):
            tr = trs[i]
            tds = tr.find_all('td')
            if len(tds) and tds[0].text.startswith(w):
                ms = tds[0].text.strip("\n").split("\\")
                if len(ms) == 1:
                    api = trs[-1].find("a").text.strip("\\")
                    ms = word_t(ms[0], api)
                else:
                    ms = word_t(ms[0], ms[1])
                mp = tds[1].text.strip("\n").split("\\")
                if len(mp) == 1:
                    mp = word_t(mp[0], api)
                else:
                    mp = word_t(mp[0], mp[1])
                fs = word_t(ms[0], ms[1])
                fp = word_t(mp[0], mp[1])
                break
            i += 1
        pass
    else:
        if genre.find_all('tr')[1].find('th').text.replace("\n", " ") == "Masculinet féminin ":
            # todo ça va planter si singulier et pluriel ont deux prononciations différentes
            #todo ça plante aussi si la première case "masculin et féminin" est absente (ex: abiotique)
            sing_plur = [x.text.strip("\n").strip("\xa0") for x in genre.find_all('tr')[1].find_all('td')]
            api = genre.find_all('tr')[2].text.strip("\n").strip("\\")
            ms = word_t(sing_plur[0], api)
            mp = word_t(sing_plur[1], api)
            fs = word_t(sing_plur[0], api)
            fp = word_t(sing_plur[1], api)
        else:
            tds_f = genre.find('tr', class_="flextable-fr-f").find_all('td')
            tds_m = genre.find('tr', class_="flextable-fr-m").find_all('td')
            masc = [x.text for x in tds_m]
            fem = [x.text for x in tds_f]
            ms = extract_word_phonetic(masc[0])  # word_t
            if len(masc) == 1:
                mp = ms
            else:
                mp = extract_word_phonetic(masc[1])  # word_t
            fs = extract_word_phonetic(fem[0])  # word_t
            if len(fem) == 1:
                fp = fs
            else:
                fp = extract_word_phonetic(fem[1])  # word_t
    # rad = ""
    # if mp[0].startswith(ms[0]):
    #     mp = word_t("+"+mp[0][len(ms[0]):], mp[1])
    #     pass
    # if fs[0].startswith(ms[0]):
    #     # exemple: petit, grand, factuel
    #     if fp[0].startswith(fp[0]):
    #         fp = word_t("+"+fp[0][len(ms[0]):], fp[1])
    #     fs = word_t("+"+fs[0][len(ms[0]):], fs[1])
    # else:
    #     # exemple: inclusif
    #     i = 0
    #     while ms[0][i] == fs[0][i]:
    #         i += 1
    #     if i == len(ms[0])-1:
    #         fs = word_t("-" + fs[0][i:], fs[1])
    #         fp = word_t("-" + fp[0][i:], fp[1])
    #         pass
    #     else:
    #         # cas relou, j'ai pas encore d'exemple
    #         # ça y est je savais bien que ça existait.
    #         # j'ai trouvé un exemple: beau/belle
    #         print(ms)
    #         print(mp)
    #         print(fs)
    #         print(fp)
    #         rad = ms[0][:i]
    #         print('rad: %s' % rad)
    #         ms = word_t("+" + ms[0][i:], ms[1])
    #         mp = word_t("+" + mp[0][i:], mp[1])
    #         fs = word_t("+" + fs[0][i:], fs[1])
    #         fp = word_t("+" + mp[0][i:], fp[1])
    #         if len(rad) == 0:
    #             # pas de radical commun entre masculin et feminin
    #             # je sais même pas si un mot comme ça existe
    #             pass
    desin = desinences_t(ms=ms, mp=mp, fs=fs, fp=fp)
    return desin


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


# testé pour nom, flex-nom
def _extract_nom_genre(categ):
    genre = categ.find_next('span', class_='ligne-de-forme')
    if genre is None:
        return "?"
    genre = genre.text
    if genre == 'féminin':
        genre = 'F'
    elif genre == 'masculin':
        genre = 'M'
    else:
        genre = "?"
    return genre


# testé pour flex-nom
def _extract_nombre(categ):
    nombre_g = categ.find_next('tr')
    if nombre_g is not None:
        nombre_g = nombre_g.find_next('tr')
    retry = 0
    if nombre_g is not None:
        while retry <2:
            nombre_g = nombre_g.find_all('td')
            # si la première case contient un selflink
            # la forme est au singulier, sinon elle est au pluriel
            cnt = 0
            #nombre_g = "?"
            for td in nombre_g:
                if td.find('a', class_="mw-selflink selflink") is not None:
                    if cnt == 0:
                        nombre_g = "S"
                    if cnt == 1:
                        nombre_g = "P"
                    break
                cnt += 1
            if nombre_g =="S" or nombre_g == 'P':
                break
            retry += 1
            nombre_g = nombre_g[0].find_next("tr")
    return nombre_g


# helper for extract infos
# scans str of form "nom \\<phonetics>\\"
def extract_word_phonetic(s):
    w = ""
    p = ""
    e = s.find('\\')
    w = s[:e]
    p = s[e + 1:]
    e = p.find('\\')
    p = p[:e]
    return w, p


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


import re

def parcours_gramm(gramm_dict, fonction):
    for w in gramm_dict:
        for wt in gramm_dict[w]:
            fonction(wt)

def liste_natures(gramm_dict):
    nat = []
    def f(wt):
        if not wt.nature in nat:
            nat.append(wt.nature)
    parcours_gramm(gramm_dict, f)
    return nat


def filter_gramm(gramm_dict, nat=None):
    ret = []
    for w in gramm_dict:
        for wt in gramm_dict[w]:
            if nat(wt.nature):
                ret.append(wt)
    return ret


def update_gramm(gramm_dict):
    for w in gramm_dict:
        flex = []
        for wt in gramm_dict[w]:
            wt_updated = word_info_t(nature=wt.nature, api=wt.api, genre=wt.genre, nbr=wt.nbr, lex=wt.lex, anto=wt.anto, hypo=wt.hypo, syno=wt.syno, desinences=wt.desinences, mot=w)
            flex.append(wt_updated)
        gramm_dict[w] = flex
