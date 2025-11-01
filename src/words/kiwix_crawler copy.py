import pickle
import time
import os.path
import random
import re
from shutil import copyfile

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet

from anagrammes import load_words_list
from words_tuple import word_t, word_info_t, desinences_t, flex_word
from verb import Verb_info
from cw import binary_search
import random

# BASE_URL = "https://fr.wiktionary.org/wiki/"

WIKTIONARY_ZIM = "wiktionary_fr_all_maxi_2024-06"

BASE_URL = f"http://127.0.0.1:8080/viewer#{WIKTIONARY_ZIM}/A/"
BASE_URL=f"http://127.0.0.1:8080/content/{WIKTIONARY_ZIM}/A/"
BASE_VERB_URL = f"http://127.0.0.1:8080/content/{WIKTIONARY_ZIM}/A/Conjugaison%3Afran%C3%A7ais/"


#explore la liste ol des différents sens/utilisations possibles du mot, pour en extraire des proto-champs lexicaux
def extract_ol_semantic(ol):
    semantics=[]
    for span in ol.find_all("span", id=re.compile("^fr-")):
        s = span.text.strip()
        semantics.append(s)
    for span in ol.find_all("span", class_=lambda x:x in ["registre","emploi"]):
        s = span.text.strip()
        semantics.append(s)
    return set(semantics)


def extract_flextable(flex_t):
    rows = flex_t.tbody.find_all("tr")
    mf:bool = False  #  True if masculin et féminin identique
    invariable = False

    if len(rows)==2:
        _text = rows[0].th.text.lower()
        # if "invariable" in rows[0].th.text.lower():
        if _text=="au singulier uniquement":
            anchors = rows[1].td.find_all("a")
            assert len(anchors) == 2
            api = anchors[1].span.text.strip()[1:-1]
            word = anchors[0].text.strip()
            return ({"I":(word, api)}, mf)
        if _text in ["invariable", "singulier et pluriel"]:
            anchors = rows[1].td.find_all("a")
            assert len(anchors) == 2
            api = anchors[1].span.text.strip()[1:-1]
            word = anchors[0].text.strip()
            return ({"I":(word, api)}, mf)

    elif len(rows)==3:
        assert flex_t.tbody.tr.text.replace('\n','')=="SingulierPluriel"
        if rows[1].has_attr("class") and "flextable-fr-m" in rows[1]["class"] and rows[2].has_attr("class") and "flextable-fr-f" in rows[2]["class"]:
            #  cas général: masculin/féminin pluriel/singulier
        #MASCULIN
            current_row_cells = rows[1].find_all('td')
            anchors = current_row_cells[0].find_all("a")
            m_s_ort=anchors[0].text
            m_s_api=anchors[-1].text[1:-1]
            if len(anchors)==3:
                assert anchors[1].attrs["title"]=="h aspiré"
            
            if len(current_row_cells) == 1:
                # NOTE: singulier/pluriel identique
                # NOTE: exemples:douloureux, nombreux...
                assert current_row_cells[0]["colspan"] == "2"
                m_p_ort=m_s_ort
                m_p_api=m_s_api
            else:
                anchors = current_row_cells[1].find_all("a")
                assert len(anchors) >= 2, "Une seule API"
                m_p_ort=anchors[0].text
                if len(anchors)==3:
                    assert anchors[1].attrs["title"]=="h aspiré"
                m_p_api=anchors[-1].text[1:-1]
        #FEMININ
            current_row_cells = rows[2].find_all('td')
            anchors = current_row_cells[0].find_all("a")
            assert len(anchors) >= 2, "Une seule API"
            f_s_ort=anchors[0].text
            if len(anchors)==3:
                    assert anchors[1].attrs["title"]=="h aspiré"
            f_s_api=anchors[-1].text[1:-1]
            anchors = current_row_cells[1].find_all("a")
            f_p_ort=anchors[0].text
            f_p_api=anchors[-1].text[1:-1]
            return({
                "ms":(m_s_ort,m_s_api),
                "mp":(m_p_ort,m_p_api),
                "fs":(f_s_ort,f_s_api),
                "fp":(f_p_ort,f_p_api),
            }, mf)

        if "invariable" in rows[0].th.text.lower():
            api = rows[2].a.span.text[1:-1]
            word = rows[1].td.a.text[1:-1]
            return {"I":(word, api)}

        if rows[1].th is not None:
            if rows[1].th.text.replace(" ","").lower()=="masculinetféminin":
                mf = True

        # une seule prononciation singulier/pluriel
        if rows[2].td["colspan"]=="2":
            api = rows[2].a.span.text[1:-1]
            current_row_cells = rows[1].find_all("td")
            singulier = current_row_cells[0].text
            pluriel=current_row_cells[1].text            
            return({
                "s":(singulier,api),
                "p":(pluriel,api)
            }, mf)

    return None



# extrait les infos du mot w depuis une page wiktionnary
def extract_infos(w, all_champs_lex=[]):
    # TODO prepare w (unicode, espaces, accents)
    # TODO data-level=5 existe, voir "temps"
    page = requests.get(f"{BASE_URL}{w}")
    # page = requests.get("http://192.168.43.125:8181/wiktionary_fr_all_nopic_2020-10/A/%s" % w)
    soup = BeautifulSoup(page.content, "html.parser")
    lang_block = None
    all_senses = []
    regex_nature = re.compile('[1-9]')
    for l in soup.find_all("details", attrs={"data-level":2}):
        if l.find("summary").text=="Français":
            lang_block = l
            break
    
    # assert lang is not None
    if lang_block is None:
        return None

    #ICI, lang_block pointe sur le bloc FRANÇAIS
    current_sense = None
    semantics = []
    for block in lang_block.find_all("details"):
        if block["data-level"]=="3":
            if current_sense is not None:
                #  TODO il est possible que ce bloc de niveau 3 soit en rapport avec le sens courant
                all_senses.append(current_sense)
                current_sense = None
            title = block.summary.text.strip().lower()
            if title in ["étymologie", "prononciation", "voir aussi", "anagrammes", "références"]:
                #  TODO 
                continue
            nature = block.find("span", class_="titredef")
            nombre="?"
            flextable = None
            mf_identiques = False
            if nature is not None:
                flex=False
                nature = nature['id'][3:regex_nature.search(nature['id']).span()[0]-1]
                print(f"nature = {nature}")
                if nature.startswith("flex-"):
                    flex = True
                    nature = nature[5:]

                if nature in ["nom", "adj"]:
                    flextable = block.find("table", class_="flextable")
                    if flextable is None:
                        print('vide')
                        return []
                    flextable, mf_identiques = extract_flextable(flextable)
                    genre = _extract_nom_genre(block)
                    if genre[0] == "?" and mf_identiques:
                        genre = ("MF",genre[1])
                    for k in flextable:
                        if flextable[k][0]==w:
                            api = flextable[k][1]
                            nombre = k
                            break
                    if genre[0]=="M":
                        assert "f" not in nombre
                    if genre[0]=="F":
                        assert "m" not in nombre
                    if "p" in nombre:
                        nombre = "P"
                    elif "s" in nombre:
                        nombre = "S"
                    else:
                        nombre = "I"
                    ol = block.find("ol")
                    semantics = extract_ol_semantic(ol)
                    # info_t = word_info_t(nature, api, genre[0], nombre, lex=champs_lex, anto=antonymes, hypo=hyponymes, syno=synonymes, mot=w)
                    #TODO: on renvoie le genre mais pas le nombre ?
                    current_sense={"nature":nature, "api":api, "mot":w, "genre":genre[0], "nombre":nombre, "semantics":semantics, "flex":flextable}
                elif nature=="verb":
                    infinitif = None
                    if flex:
                        #extraire l'infinitif du verbe depuis la soup
                        print("flex")
                        t=block.find("table", class_="flextable")
                        infinitif = t.find("a", href=re.compile("^Conjugaison%3Afran%C3%A7ais/")).attrs["href"][28:]
                        #TODO: gérer le cas
                        current_sense={"nature":"flex-verb", "infinitif":infinitif}
                        
                    else:
                        infinitif = w
                    if infinitif is not None:
                        verb_dict = extract_verb_info_wiki(infinitif)
                        #TODO: que faire avec cet objet à présent ? on a extrait la conjugaison, il nous faut les infos sémantiques
                        #TODO visiter la page du verbe pour extraire les infos
                        current_sense = {"nature":"verb", "conjugaison":verb_dict}
                else:
                    continue

            # TODO
        elif block["data-level"]=='4':
            # TODO infos sémantiques
            pass
    if current_sense is not None and current_sense not in all_senses:
        all_senses.append(current_sense)
    return all_senses


def append_bs4_error(w):
    f = open("data/bs4_error.dmp", "ab")
    pickle.dump(w, f)
    f.close()


def extract_verbe_group(soup):
    # TODO on trouvera cette table pour chaque onglet de forme de conjugaison
    tables = soup.find_all("table", class_="wikitable")
    group = None
    conju = None
    for table in tables:
        if table.tbody.tr.th.text.strip() == "Conjugaison en français":
            rows = table.tbody.find_all("tr")
            assert len(rows)==3
            line = rows[2].td.text.strip().lower()
            anchors = rows[2].td.find_all("a")
            for a in anchors:
                t = a.text.strip().lower()
                if t.endswith("groupe"):
                    if not t.find("premier") == -1:
                        group = 1
                    elif not t.find("deuxième") == -1:
                        group = 2
                    elif not t.find("troisième") == -1:
                        group = 3
                    else:
                        raise Exception("pas trouvé le groupe du verbe")
                idx1 = line.find("{{")
                idx2 = line.find("}}")
                if idx1>=0 and idx2 >= 0:
                    conju = line[idx1+2:idx2]
                    pass
            print(line)
    return(group, conju)


##INFOS pour réparer extract_verb_info
# $("a.mw-selflink") : repère les onglets active/pronominale (pour verbes réfléchis etc)
#$("div#mw-content-text") #lebloc qui nous intéresse. Contient les onglets conjugaisons active/pronominale
# le div renvoyé contient les onglets de conjugaison (active/personnelle)
#plus simple: $("div#mb0og1") renvoie l'onglet 1 et $("div#mb0og2") l'onglet 2

#pour les formes de conjugaison: personnelle, impersonnelle, pronominale...
#
#soup.find(id="mb0bt1").text: nom de la premiere forme
#soup.find(id="mb0og1"): le div contenant les conjugaisons correspondantes
#VERSION KIWIX
def extract_verb_info_wiki(v:str):
    """
    Scrappe la conjugaison d'un verbe sur wiktionary
    TODO: gérer les conjugaisons pronominales, impersonnelles, ...
    TODO: gérer les variantes (exemple: é/è)
    TODO: pour le mode impératif, erreur: comme il y a moins de formes, les index sont décalés: 
    TODO: seul 2s, 1p et 2p devraient être valides. or, 1s renvoie 2s, 2s renvoie 1p, etc
    TODO: verbes composés ?
    :param v: le verbe à scrapper
    :return: un dictionnaire formaté pour le constructeur de Verb_info
    """
    # todo gérer les verbes intransitifs et ceux qui n'ont que quelques pronoms
    # todo gérer les verbes composés ?
    page = requests.get(f"{BASE_VERB_URL}{v}")
    print(f"requesting {BASE_VERB_URL}{v}")
    # page = requests.get("http://192.168.43.125:8181/wiktionary_fr_all_nopic_2020-10/A/%s" % v)
    soup = BeautifulSoup(page.content, "html.parser")
    extract_verbe_group(soup)

    i=1
    while True:
        conjug = soup.find(id=f"mb0bt{i}")
        if conjug is None:
            break
        forme_name = conjug.text
        print(f"id: mb0og{i}")
        forme_div = soup.find(id=f"mb0og{i}")
        print(f"{i} {forme_name} {hash(forme_div)}")
        i+=1

    

    #extrait les infos d'un mode + temps
    #TODO: verbes impersonnels
    def extract_temps(table):
        lines = table.find_all("tr")
        temps = lines[0].text.strip("\n")
        with_aux = False
        # print("****************** %s *******************" % temps)

        if temps in ["Passé", "Passé composé", "Plus-que-parfait", "Passé antérieur", "Futur antérieur"]:
            with_aux=True
            return (temps, [])
        else:
            print(temps)

        desinences = []
        i1 = 1
        i2 = 3
        if len(lines) == 4:
            i2 = 2
        if len(lines) == 7 or len(lines) == 4:
            for line in lines[1:]:
                tds = line.find_all("td")
                # print("################# %d %s" % (len(tds), line.text))
                w = tds[i1].text.strip("\n").strip("\xa0").strip("\\")
                # api = tds[i2].text.strip("\n").strip("\\").strip("\xa0")
                api = tds[i2].span.text.strip("\\")
                # print("%s %s" % (w, api))
                desinences.append((w, api))
            pass
        return (temps, desinences)
    conjugs = soup.find_all(id=re.compile("^mb0og"))
    if len(conjugs)==0:
        #le verbe n'a qu'une seule forme de conjugaison
        conjugs=[soup.find(id="mw-content-text")]
        if len(conjugs)==0:
            return soup
    
    #TODO on extrait que la première forme (personnelle a priori)
    #TODO il faudrait tager l'objet renvoyé pour indiquer les autres formes
    #TODO il faudrait surtout extraire les autres formes; ici, on considère que les autres formes 
    #TODO ont des orthographes identiques 
    conjug = conjugs[0]
    #dictionnaire retourné
    v_info = {}

    # NOTE h3 sur wikipedia, h2 pour kwix ? en fait ça dépend ...
    modes_imp = conjug.find("h2", id="Modes_impersonnels")
    if modes_imp is None:
        modes_imp = conjug.find("h3", id="Modes_impersonnels")
    if modes_imp is None:
        print("S1")
        return soup
    # Auxiliaires, participes, infinitif
    auxiliaire = ""
    infinitif_html = modes_imp.find_next("a", title="infinitif")
    while not infinitif_html.name == 'tr':
        infinitif_html = infinitif_html.parent
    infinitif_html = infinitif_html.find_all("td")
    v_info["inf"] = word_t(v, infinitif_html[3].text.strip("\n").strip("\xa0").strip("\\"))
    # TODO: gérer le cas des doubles auxiliaires
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
    
    verbes_modes = {"Indicatif":"In", "Subjonctif":"S", "Conditionnel":"C", "Impératif":"Im"}
    v_info['In'] = {}
    v_info['S'] = {}
    v_info['C'] = {}
    v_info['Im'] = {}

    for mode in verbes_modes:
        # NOTE idem h3/h2
        times = conjug.find('h2', id=mode)
        if times is None:
            times = conjug.find('h3', id=mode)
        times = times.find_next("div").find("table").find_all("table")
        # print("vide")
        for t in times:
            temps = extract_temps(t)
            v_info[verbes_modes[mode]][temps[0]] = temps[1]
    
    formes = [ bt.find("a").text.strip() for bt in soup.find_all('div', id=re.compile("^mb0bt"))]
    # for f in formes:
    #     assert f[:12] == "Conjugaison "
    formes = [f[12:] for f in formes if f.startswith("Conjugaison ")]

    return v_info


def make_info_list(wlist=[]):
    """
    LA grosse fonction, qui prend une lsite de mots en entrée, et enrichit le dictionnaire
    en allant chercher les infos sur wiktionnary
    en tous cas elle est sensée le faire.
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



# def get_categrams(w):
#     page = requests.get(f"{BASE_URL}{w}")
#     # page = requests.get("http://192.168.43.125:8181/wiktionary_fr_all_nopic_2020-10/A/%s" % w)

#     soup = BeautifulSoup(page.content, "html.parser")
#     categram_spans = soup.find_all("span", class_="titredef", id=re.compile('^fr-'))
#     return categram_spans



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


# def extract_adj_desinences(categ, w):
#     return _extract_adj_desinences(categ, w)


# def _extract_adj_desinences(categ, w):
#     msi = False
#     tmp = categ.find_next("span", class_="ligne-de-forme")
#     if tmp is not None:
#         tmp = tmp.text
#     if tmp == 'masculin et féminin identiques':
#         msi = True

#     genre = categ.find_next('table', class_='flextable-fr-mfsp')
#     if genre is None:
#         genre = categ.find_next('table', class_='flextable')
#         if genre.find_all('tr')[0].text.strip("\n") == "Invariable":
#             adj = genre.find_all('tr')[1].text.strip("\n").split("\\")
#             return word_t(adj[0], adj[1])
#             # return desinences_t(word_t(adj[0], adj[1]),word_t(adj[0], adj[1]),word_t(adj[0], adj[1]),word_t(adj[0], adj[1]))
#     trs = genre.find_all('tr')
#     if "colspan" in trs[-1].find_all('td')[0].attrs:
#         msi = True
#     masc = None
#     fem = None
#     ms = None
#     mp = None
#     fs = None
#     fp = None
#     api = None
#     if genre is None:
#         # return desinences_t(ms=word_t("", ""), mp=word_t("", ""),fs=word_t("", ""),fp=word_t("", ""))
#         raise Exception("Erreur pas de désinences")
#     if msi is True:
#         i = 0

#         while i < len(trs):
#             tr = trs[i]
#             tds = tr.find_all('td')
#             if len(tds) and tds[0].text.startswith(w):
#                 ms = tds[0].text.strip("\n").split("\\")
#                 if len(ms) == 1:
#                     api = trs[-1].find("a").text.strip("\\")
#                     ms = word_t(ms[0], api)
#                 else:
#                     ms = word_t(ms[0], ms[1])
#                 mp = tds[1].text.strip("\n").split("\\")
#                 if len(mp) == 1:
#                     mp = word_t(mp[0], api)
#                 else:
#                     mp = word_t(mp[0], mp[1])
#                 fs = word_t(ms[0], ms[1])
#                 fp = word_t(mp[0], mp[1])
#                 break
#             i += 1
#         pass
#     else:
#         if genre.find_all('tr')[1].find('th').text.replace("\n", " ") == "Masculinet féminin ":
#             # todo ça va planter si singulier et pluriel ont deux prononciations différentes
#             #todo ça plante aussi si la première case "masculin et féminin" est absente (ex: abiotique)
#             sing_plur = [x.text.strip("\n").strip("\xa0") for x in genre.find_all('tr')[1].find_all('td')]
#             api = genre.find_all('tr')[2].text.strip("\n").strip("\\")
#             ms = word_t(sing_plur[0], api)
#             mp = word_t(sing_plur[1], api)
#             fs = word_t(sing_plur[0], api)
#             fp = word_t(sing_plur[1], api)
#         else:
#             tds_f = genre.find('tr', class_="flextable-fr-f").find_all('td')
#             tds_m = genre.find('tr', class_="flextable-fr-m").find_all('td')
#             masc = [x.text for x in tds_m]
#             fem = [x.text for x in tds_f]
#             ms = extract_word_phonetic(masc[0])  # word_t
#             if len(masc) == 1:
#                 mp = ms
#             else:
#                 mp = extract_word_phonetic(masc[1])  # word_t
#             fs = extract_word_phonetic(fem[0])  # word_t
#             if len(fem) == 1:
#                 fp = fs
#             else:
#                 fp = extract_word_phonetic(fem[1])  # word_t

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

    # desin = desinences_t(ms=ms, mp=mp, fs=fs, fp=fp)
    # return desin


# return a list of <li> elements
# helper for extract infos, to find list of derived, synonyms, antonyms...
# def _extract_list_elements(parent, list_name):
#     html = parent.find_next("span", class_="titre" + list_name)
#     # verifier que la liste correspond bien à la bonne sectionlangue
#     #todo: c'est peut être la bonne langue mais pour un autre sens du mot ?
#     if html is None or not html.find_previous("span", class_="sectionlangue") == parent.find_previous("span", class_="sectionlangue"):
#         return []
#     candidats = None
#     candidats = html.find_next('div')
#     previous_title = candidats.find_previous("span", class_=re.compile("titre"))
#     # elements not in div (unique list ?)
#     if not previous_title.attrs["class"] == "titre" + list_name:
#         candidats = html.find_next("ul").find_all("li")
#         # todo: another test yo ensure this is the good list
#     else:
#         candidats = [x.find_all("li") for x in candidats.find_all("ul")]
#     return candidats


# testé pour nom, flex-nom
def _extract_nom_genre(categ):
    genre = categ.find_next('span', class_='ligne-de-forme')
    if genre is None:
        return ["?", "?"]
    genre_t = genre.text
    if genre_t == 'féminin':
        genre_t = 'F'
    elif genre_t == 'masculin':
        genre_t = 'M'
    else:
        genre_t = "?"
    nombre = genre.find_next('span', class_='ligne-de-forme')  # ici, ça buggue avec le nom "gamin"
    # nombre_t = '?'
    nombre_t = 'S'  #TODO ici solution scabreuse: on considère que par défaut, c'est singulier.
                    #reste à voir si ça n'interfère pas avec les noms invariables
    if nombre is not None:  #TODO ici ça semble bugger avec "gamin"
        nombre_t = nombre.text
        if nombre_t == 'pluriel':
            nombre_t = 'P'
        elif nombre_t == 'singulier':
            nombre_t = 'S'
        else:
            nombre_t = '?'
    return (genre_t, nombre_t)


# testé pour flex-nom
# def _extract_nombre(categ):
#     nombre_g = categ.find_next('tr')
#     if nombre_g is not None:
#         nombre_g = nombre_g.find_next('tr')
#     retry = 0
#     if nombre_g is not None:
#         while retry <2:
#             nombre_g = nombre_g.find_all('td')
#             # si la première case contient un selflink
#             # la forme est au singulier, sinon elle est au pluriel
#             cnt = 0
#             #nombre_g = "?"
#             for td in nombre_g:
#                 if td.find('a', class_="mw-selflink selflink") is not None:
#                     if cnt == 0:
#                         nombre_g = "S"
#                     if cnt == 1:
#                         nombre_g = "P"
#                     break
#                 cnt += 1
#             if nombre_g =="S" or nombre_g == 'P':
#                 break
#             retry += 1
#             nombre_g = nombre_g[0].find_next("tr")
#     return nombre_g


# helper for extract infos
# scans str of form "nom \\<phonetics>\\"
# def extract_word_phonetic(s):
#     w = ""
#     p = ""
#     e = s.find('\\')
#     w = s[:e]
#     p = s[e + 1:]
#     e = p.find('\\')
#     p = p[:e]
#     return w, p


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


##############################################
##########Session fin 2024
###############################################

def batch(words:list[str]):
    for w in words:
        extract_infos(w)

    pass

def q_load_verb(v):
    dic = extract_verb_info_wiki(v)
    if dic is None:
        print("Erreur 1")
        return None
    if not isinstance(dic, dict):
        print("Erreur2")
        return dic
    return Verb_info(dic)

def my_test():
    acc = q_load_verb("accompagner")
    aller = q_load_verb("aller")
    assert acc.getMode("Indicatif:Présent:2s").ort == "accompagnes", acc.getMode("Indicatif:Présent:2s")
    assert aller.getMode("Indicatif:Imparfait:2p").ort == "alliez"

cartouche = extract_infos("cartouche")
gamin=extract_infos("gamin")
maire=extract_infos("maire")
# maires=flex_word(maire[0]["flex"],"p")
# print(maires)
temps=extract_infos("temps")  # TODO problème détection nature
acc = q_load_verb("accompagner")
avoir = q_load_verb("avoir")
être = q_load_verb("être")
manger = q_load_verb("manger")

my_test()


def my_test2(words_count=100):
    words_list=load_words_list("data/gutenberg.txt")
    ret_dict={}
    for i in range(0,words_count):
        x = random.randint(0, len(words_list) - 1)
        w = words_list[x]
        print(w)
        ret_dict[w]=extract_infos(w)
    return ret_dict

# x=random.randint(0,100) 
# ws = my_test2()
dl=extract_infos("douloureuse") 
dl_s=extract_infos("douloureuses") # typiquement, aucune info ici
thêta = extract_infos("thêta")
dépendance = extract_infos("dépendance")
encore=extract_infos("encore")
demanderions = extract_infos("demanderions")
#TODO autres mots qui déconnent: hasté, romani
hasté = extract_infos("hasté")
romani = extract_infos("romani")

