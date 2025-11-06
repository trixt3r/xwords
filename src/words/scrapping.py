import re
from typing import Generator
import warnings
import random

from urllib.parse import unquote

from bs4 import BeautifulSoup, element, Tag
import requests

from conjug_extract import ConjugExtract
from anagrammes import load_words_list
from GNode import *
from words_tuple import word_t
from scrap_base import BASE_URL, ExtractException, extract_api, search_gcd
from verb import Verb_info



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

def iter_over_level2_blocks(soup)->Generator[element.Tag, None, None]:
    for l in soup.find_all("details", attrs={"data-level":2}):
        yield l

def iter_over_level3_blocks(soup)->Generator[element.Tag, None, None]:
    for l in soup.find_all("details", attrs={"data-level":3}):
        yield l

def _get_key_desinence(genre, nombre):
    trad_genre = {"masculin":"m", "féminin":"f", "neutre":"n", "masculinetféminin":"mf", "invariable":"i"}
    #NOTE j'aime pas cette affaire de invariable/indénombrable
    #NOTE je pense que ça devrait le faire
    trad_nombre = {"singulier":"s", "pluriel":"p", "invariable":"i", "indénombrable":"i"}
    g = trad_genre[genre]
    n = trad_nombre[nombre]
    return f"{g}{n}"

def _get_val_desinence(key):
    if "m" in key:
        genre = "masculin"
    elif "f" in key:
        genre = "féminin"
    elif "n" in key:
        genre = "neutre"
    else:
        genre = None

    if "s" in key:
        nombre = "singulier"
    elif "p" in key:
        nombre = "pluriel"
    elif "i" in key:
        nombre = "invariable"
    else:
        nombre = None

    return genre, nombre

def extract_no_flextable(word,block):
    """
    Extraction pour les cas sans flextable
    """
    # for b in block.children:
    #    if isinstance(b,Tag):
    #       pass
    #    elif isinstance(b,NavigableString):
    #        pass 
    ldf = block.find_all("span", class_="ligne-de-forme")
    if len(ldf)==0:
        #a priori on doit facilement trouver là-dedans les infos
        tags = [x for x in block.children if isinstance(x,Tag)]
        if len(tags)==3:
            genre, nombre, api = None, None, None
            assert tags[0].name == "summary"
            assert tags[1].name == "p"
            assert tags[2].name == "ol"
            g_n = tags[2].text.strip().lower().split(" ")
            assert len(g_n)>=2
            assert g_n[0] in ["masculin","féminin"]
            assert g_n[1] in ["singulier","pluriel"]
            assert g_n[2] == "de"
            genre = g_n[0]
            nombre = g_n[1]
            _api = tags[1].text.strip().split(" ")
            assert len(_api)==2
            assert _api[1].startswith("\\") and _api[1].endswith("\\")
            api = extract_api(_api[1])
            return {_get_key_desinence(genre, nombre):( word, api)}, genre, nombre, api
            raise NotImplementedError("pas fini")
    else:
        assert len(set([x.parent for x in ldf])) == 1
    tmp = [e.text.strip() for e in ldf[0].parent]
    tmp = [x for x in tmp if x not in ["",","]]
    apis = [i for i,x in enumerate(tmp) if x.startswith("\\") and x.endswith("\\")]
    if len(apis)!=1:
        raise ExtractException(f"plusieurs ou pas d'api trouvée pour {word}")
    _api = extract_api(tmp[apis[0]])
    tmp.remove(tmp[apis[0]])
    
    orths = [i for i,x in enumerate(tmp) if x==word]
    if len(orths)!=1:
        raise ExtractException(f"plusieurs ou pas d'orthographe trouvée pour {word}")
    _orth = tmp[orths[0]]
    tmp.remove(tmp[orths[0]])

    _genre = None
    if "masculin" in tmp:
        genre = "masculin"
        tmp.remove("masculin")
    elif "féminin" in tmp:  
        genre = "féminin"
        tmp.remove("féminin")
    else:
        raise ExtractException(f"pas de genre trouvé pour {word}")
    if "au singulier uniquement" in tmp:
        nombre = "singulier"
        tmp.remove("au singulier uniquement")
    elif "au pluriel uniquement" in tmp:
        nombre = "pluriel"
        tmp.remove("au pluriel uniquement")
    elif "invariable" in tmp:
        nombre = "invariable"
        tmp.remove("invariable")
    elif "(Indénombrable)" in tmp:
        nombre = "indénombrable"
        tmp.remove("(Indénombrable)")
    else:
        raise ExtractException(f"pas de nombre trouvé pour {word}")
    return {_get_key_desinence(genre, nombre):( _orth, _api)}, genre, nombre, _api


def extract_flextable_new(word,block):

    ldf = None
    flextable = block.find("table", class_="flextable")
    if flextable is None:
        return extract_no_flextable(word,block)
        # raise ExtractException(f"pas de flextable trouvée pour {word}")
    _nombres = [x.text.strip().lower() for x in flextable.find("tr").find_all("th")]
    _genres = [x.find("th") for x in flextable.find_all("tr")[1:] if x.find("th") is not None]
    _genres = [x.text.strip().lower() for x in _genres]
    if len(_genres)==1:
        _genres = [_genres[0].replace(" ","")]
        if _genres[0] == "masculin" or _genres[0]=="féminin" or _genres[0]=="neutre":
            pass
        elif _genres[0] == "masculinetféminin":
            pass
            # raise ExtractException(f"cas 'masculin et féminin' non géré pour {word}")

    if len(_genres)==0:
        ldf = block.find_all("span", class_="ligne-de-forme")
        if len(ldf)==1:
            ldf = ldf[0].text.strip()
            _genres.append(ldf.lower())
        else:
            ldf = [x.text.strip() for x in ldf]
            if "masculin" in ldf:
                _genres.append("masculin")
            elif "féminin" in ldf:
                _genres.append("féminin")
            else:
                #NOTE arrivé là, on n'a pas de genre; c'est casse-bonbons
                # on peut imaginer que c'est un flex-nom
                # auquel cas, on peut sûrement récupérer l'info sur la page canonique du mot, au singulier

                #ça peut aussi être un adjectif (nom?) masculin et féminin identique, mais mal formaté
                #voir angiosperme adjectif
                _genres = ["?"]
                # raise ExtractException(f"pas de genre trouvé pour {word}")
            if "invariable" in ldf:
                _nombres = ["invariable"]
            pass
    
    rows = flextable.find_all("tr")[1:]
    rows = [row.find_all("td") for row in rows]
    if len(rows)==2:
        if len(_genres)==2 and len(_nombres) == 2:
            # cas général, masculin/féminin et singulier/pluriel
            rows = [[td for td in row] for row in rows]
            rows = [[tuple(y.text.strip() for y in x.find_all("a")) for x in row]for row in rows]
            for i,r in enumerate(rows):
                if not len(r)==2:
                    if len(r)==3:
                        if r[1].text.strip().startswith("\\") and r[1].text.strip().endswith("\\") and \
                            r[2].text.strip().startswith("\\") and r[2].text.strip().endswith("\\"):
                            warnings.warn(f"probably 2 phonetics variants for {word}, taking the first one, dropping the other")
                            rows[i] = [r[0], r[1]]
                    elif len(r)==1:
                        rows[i] = r*2
                    else:
                        raise ExtractException(f"1cas inattendu pour {word}")
            pass
        elif len(_genres)==1 and len(_nombres) == 2:
            # un seul genre (peut être: masculin et féminin identiques), singulier/pluriel
            if len(rows[1])==1:
                t = rows[1][0].text.strip()
                if t.startswith("\\") and t.endswith("\\"):
                    rows = [[(rows[0][0].text.strip(), rows[1][0].text.strip()),(rows[0][1].text.strip(),rows[1][0].text.strip())]]
                else:
                    raise ExtractException(f"2cas inattendu pour {word}")
                #NOTE: j'aime pas trop ça, mais bon...
                if _genres[0]=="?":
                    # on suppose que c'est masculin et féminin identiques, non indiqué
                    _genres = ["masculinetféminin"]
            else:
                raise ExtractException(f"3cas inattendu pour {word}")
        else:
            raise ExtractException(f"4cas inattendu pour {word}")
    elif len(rows)==1:
        # rows = [[x.text for x in rows[0].find_all("a")]]
        rows = [[tuple(y.text.strip() for y in x.find_all("a")) for x in row]for row in rows]
        pass


    if _genres[0]=="masculinetféminin" or _genres[0]=="masculin et féminin identiques":
        _genres = ["masculin", "féminin"]
        assert len(rows)==1
        rows.append(rows[0])
        
    result = {}
    
    if len(rows)==len(_genres) :
        for i, row in enumerate(rows):
            if len(row)!=len(_nombres):
                assert len(row)==1
                rows[i] = [row[0]]*len(_nombres)
        for i,row in enumerate(rows):
            result.update({_get_key_desinence(_genres[i], _nombres[j]):word_t(row[j][0], extract_api(row[j][1])) for j in range(len(_nombres))})
            # for j in range(len(_nombres)):
            #     result[_get_key_desinence(_genres[i], _nombres[j])] = (row[j][0], extract_api(row[j][1]))
    else:
        print(rows)
        raise ExtractException(f"nombre de lignes inattendu pour {word}")
    

    candidates_flex = [key for key,value in result.items() if value[0]==word]
    if len(candidates_flex) > 1:
        warnings.warn(f"ambiguité dans les flexions pour {word}, on prend la première")
    flex = candidates_flex[0]
    genre, nombre, api = None, None, None
    if "m" in flex:
        genre = "masculin"
    elif "f" in flex:
        genre = "féminin"   
    elif "n" in flex:
        genre = "neutre"
    else:
        raise ExtractException(f"pas de genre trouvé pour {word}")
    if "s" in flex:
        nombre = "singulier"
    elif "p" in flex:
        nombre = "pluriel"
    elif "i" in flex:
        nombre = "invariable"
    api = result[flex][1]
    return result, genre, nombre, api

def parse_flex_verb(w,block):
    
    
    li = block.find("ol").find("li")
    forme = None
    if li.find("i") is not None:
        forme = li.find("i").text.lower().split()
    else:
        #NOTE c'est sûrement une variante orthographique du verbe
        #exemple: "écoeurez" -> "écœurez"
        raise ExtractException(f"forme du verbe introuvable pour {w}")
    # elif li.find("a") is not None:
    #     forme = li.find("a").text.lower().split()
    
    forme = [x for x in forme if x not in ["du","de", "verbe", "personne"]]
    for i,f in enumerate(forme):
        if f.startswith("l’"):
            forme[i]=f[2:]
    if "participe" in forme:
        forme.remove("participe")
        type_participe = None
        if "présent" in forme:
            forme.remove("présent")
            type_participe = "présent"
        elif "passé" in forme:
            forme.remove("passé")
            type_participe = "passé"
        else:
            raise ExtractException(f"type de participe inconnu {forme}")
        genre = "m"
        nombre = "s"
        if "féminin" in forme:
            genre = "f"
            forme.remove("féminin")
        if "pluriel" in forme:
            nombre = "p"
            forme.remove("pluriel")
        return (f"participe {type_participe}", genre, nombre)
    pers = [x for x in forme if x in ["première","deuxième","troisième"]]
    assert len(pers)==1
    pers = pers[0]
    forme.remove(pers)
    pers = {"première": 1, "deuxième": 2, "troisième": 3}.get(pers)
    nombre = "s"
    if "pluriel" in forme:
        nombre = "p"
        forme.remove("pluriel")
    elif "singulier" in forme:
        nombre = "s"
        forme.remove("singulier")
    else:
        raise ExtractException(f"nombre inconnu dans la forme du verbe: {forme}")
    mode = [x for x in forme if x in ["indicatif", "subjonctif", "impératif", "conditionnel"]]
    assert len(mode)<2, f"mode {mode}inconnu dans la forme du verbe: {forme}"
    if len(mode)==0:
        mode = "indicatif"
    else:
        mode = mode[0]
        forme.remove(mode)
    temps = " ".join(forme)
    return (pers, nombre, mode, temps)

    
def default_api_handler(block, nature:str, w:str):
    apis = block.find_all("a", href="Annexe%3APrononciation/fran%C3%A7ais")
    if len(apis)==0:
        raise ExtractException(f"pas d'API trouvée pour {w} {nature}")
    if len(apis)==2:
        warnings.warn(f"2 phonetics pour {w}, a verifier. on droppe le second")
        apis = apis[0]
    elif len(apis)==1:
        apis = apis[0]
    api = extract_api(apis.text.strip())
    return {"nature":nature, "api":api, "mot":w}

def new_master_scrapper(word:str):
    
    page = requests.get(f"{BASE_URL}{word}")
    # page = requests.get("http://192.168.43.125:8181/wiktionary_fr_all_nopic_2020-10/A/%s" % w)
    soup = BeautifulSoup(unquote(page.content.decode('utf-8')), "html.parser")
    regex_nature = re.compile('[1-9]')
    # results = []
    all_senses = []
    current_sense = None
    default_etymo = ()
    for b in iter_over_level2_blocks(soup):
        summary = b.find("summary")
        if summary is None:
            raise ExtractException(f"no summary found for {word}")
        if summary.text=="Français":
            for block in b.select("details"):
                if block.get("data-level")=="3":
                    if current_sense is not None:
                        #  TODO il est possible que ce bloc de niveau 3 soit en rapport avec le sens courant
                        all_senses.append(current_sense)
                        current_sense = None

                    #TODO garder trace des titres qui passent
                    title = block.summary.text.strip().lower()
                    if title == "étymologie":
                        print(title)
                        links = block.find_all("a")
                        if len(links)==0:
                            continue
                        etym = {unquote(link['href']) for link in links}
                        if len(links)<=2:
                            if current_sense is not None:
                                current_sense["étymologie"] = etym
                            else:
                                warnings.warn(f"étymologie trouvée pour {word} sans sens courant associé")
                                default_etymo = etym
                        else:
                            warnings.warn(f"{word} etym {len(links)} liens, à vérifier")
                            continue
                        continue

                    elif title in ["prononciation", "voir aussi", "anagrammes", "références"]:
                        #  TODO 
                        continue

                    flex = False
                    nature = block.find("span", class_="titredef")
                    if nature is None:
                        ExtractException("pas de nature trouvée")
                    
                    tmp_nature = nature['id'][3:regex_nature.search(nature['id']).span()[0]-1]
                    nature = tmp_nature
                    if nature.startswith("flex-"):
                        flex = True
                        nature = nature[5:]

                    if nature in ["nom", "adj"]:
                        flextable, genre, nombre, api = extract_flextable_new(word,block)
                        # results.append(flextable)
                        if nombre == "invariable":
                            print(f"{word} est invariable")
                        print(flextable)
                        ol = block.find("ol")
                        semantics = extract_ol_semantic(ol)
                        # info_t = word_info_t(nature, api, genre[0], nombre, lex=champs_lex, anto=antonymes, hypo=hyponymes, syno=synonymes, mot=w)
                        #TODO: on renvoie le genre mais pas le nombre ?
                        current_sense={"nature":nature, "api":api, "mot":word, "genre":genre[0], "nombre":nombre, "semantics":semantics, "flex":flextable}
                    elif nature == "verb":
                        infinitif = None
                        if flex:
                            #extraire l'infinitif du verbe depuis la soup
                            print("flex")
                            t=block.find("table", class_="flextable")
                            # infinitif = t.find("a", href=re.compile("^Conjugaison%3Afran%C3%A7ais/")).attrs["href"][28:]
                            
                            infinitif = t.find("a", href=re.compile("^Conjugaison:français/"))
                            if infinitif is None:
                                warnings.warn(f"infinitif non trouvé pour {word}")
                                pass
                            infinitif = infinitif.attrs["href"][21:]
                            ##################################
                            forme = parse_flex_verb(word,block)
                            if len(forme) == 3:
                                #                                                                part. pst/passé,  genre,   nombre
                                current_sense = {"nature":"flex-verb", "infinitif":infinitif, "forme":(forme[0], forme[1], forme[2])}
                            elif len(forme) == 4:
                                #                                                                   personne,  nombre,   temps,    mode    
                                current_sense = {"nature":"flex-verb", "infinitif":infinitif, "forme":(forme[0], forme[1], forme[3], forme[2])}
                            else:
                                raise ExtractException(f"forme de verbe inattendue pour {word}: {forme}")
                        else:
                            conjug_extractor = ConjugExtract()
                            transitif=True
                            if "intransitif" in block.find("summary").findNextSibling("p").text:
                                transitif=False
                            verb_dict = conjug_extractor.extract_verb_info_wiki(word)
                            verb_dict["transitif"]=transitif
                            #TODO: que faire avec cet objet à présent ? on a extrait la conjugaison, il nous faut les infos sémantiques
                            #TODO visiter la page du verbe pour extraire les infos
                            current_sense = {"nature":"verb", "mot":verb_dict["inf"].ort, "api":verb_dict["inf"].api, "conjugaison":verb_dict}
                    elif nature == "ad-rel":
                        pass
                    elif nature == "art-déf":
                        flextable, genre, nombre, api = extract_flextable_new(word,block)
                        assert None not in [flextable, genre, nombre, api]
                        current_sense={"nature":nature, "api":api, "mot":word, "genre":genre, "nombre":nombre, "flex":flextable}
                    elif nature == "pronom-pers":
                        flextable, genre, nombre, api = extract_flextable_new(word,block)
                        assert None not in [flextable, genre, nombre, api]
                        current_sense={"nature":nature, "api":api, "mot":word, "genre":genre, "nombre":nombre, "flex":flextable}
                    elif nature == "pronom-rel":
                        pass
                    elif nature == "interj":
                        pass
                    elif nature == "pronom-int":
                        pass
                    elif nature == "art-indéf":
                        flextable, genre, nombre, api = extract_flextable_new(word,block)
                        assert None not in [flextable, genre, nombre, api]
                        current_sense={"nature":nature, "api":api, "mot":word, "genre":genre, "nombre":nombre, "flex":flextable}
                    elif nature == "conj":
                        current_sense = default_api_handler(block, nature, word)
                        if current_sense is None:
                            raise ExtractException(f"échec de l'extraction pour {word} {nature}")
                        pass
                    elif nature=="conj-coord":
                        current_sense = default_api_handler(block, nature, word)
                        if current_sense is None:
                            raise ExtractException(f"échec de l'extraction pour {word} {nature}")
                    elif "adv" in nature:
                        pass
                    else:
                        raise ExtractException(f"nature {nature} non gérée pour {word}")
                elif block.get("data-level")=="4":
                    # TODO il est possible que ce bloc de niveau 4 soit en rapport avec le sens courant
                    if block.summary is not None:
                        title = block.summary.text.strip().lower()
                        # print(f"skipped level 4 block : {title}")
                    # else:
                    #     print(f"skipped level 4 block : [no title]")
                    pass
    if current_sense is not None:
        all_senses.append(current_sense)
    return all_senses


def test_forme_verbe(w:str):
    page = requests.get(f"{BASE_URL}{w}")
    soup = BeautifulSoup(page.content, "html.parser")
    for b in iter_over_level2_blocks(soup):
        if b.find("summary").text=="Français":
            for block in b.find_all("details"):
                if block["data-level"]=="3":
                    title = block.summary.text.strip().lower()
                    if title in ["étymologie", "prononciation", "voir aussi", "anagrammes", "références"]:
                        continue
                    nature = block.find("span", class_="titredef")
                    if nature is None:
                        ExtractException("pas de nature trouvée")
                    nature = nature['id'][3:re.search('[1-9]', nature['id']).span()[0]-1]
                    print(f"nature: {nature}")
                    if nature == "flex-verb":
                        infinitif = None
                        return parse_flex_verb(w,block)



def test_scrapper(words:list[str], n=10):
    test_words = random.sample(words, n)
    return bulk_scrap(test_words)

def bulk_scrap(words:list[str]):
    all_results = {}
    root = WTupleNode()
    errors = set()
    for word in words:
        if "-" in word:
            warnings.warn(f"skip {word} with hyphen")
            errors.add(word)
            continue
        try:
            all_results[word] = new_master_scrapper(word)
            for w in all_results[word]:
                if w["nature"] == "verb":
                    verb_obj = Verb_info(w["conjugaison"])
                    all_results[verb_obj.infinitif.ort] = [{'nature':"verb", "conjugaison":verb_obj}]
                if w["nature"] == "flex-verb":
                    infinitif = w["infinitif"]
                    verb_obj = Verb_info.get(infinitif)
                    if verb_obj is None and not infinitif in all_results:
                        infi = new_master_scrapper(infinitif)
                        verb_obj = None
                        #TODO un peu n'imp
                        # on risque de perdre les autres natures du mot
                        # aussi peut etre on peut trouver deux verbes différents avec le même infinitif ??
                        for entry in infi:
                            if entry["nature"] == "verb":
                                
                                verb_obj = Verb_info(entry["conjugaison"])
                                all_results[verb_obj.infinitif.ort] = [{'nature':"verb", "conjugaison":verb_obj}]
                        
                        n = root.addData({"nature":"verb","mot":verb_obj.infinitif.ort,"api":verb_obj.infinitif.api, "conjugaison":verb_obj})
                        #TODO ajouter toutes les formes à l'arbre
                        radical_node = root.search(verb_obj.radical)
                        assert radical_node is not None, f"erreur, radical {verb_obj.radical} non trouvé dans l'arbre"
                        for term in verb_obj.terminaisons:
                            # NOTE on peut mieux faire
                            # NOTE je suis pas pret pour ça
                            pass
                        all_results[infinitif] = [{'nature':"verb", "conjugaison":verb_obj}]
                else:
                    word_node = root.addData(w)
        except ExtractException as e:
            errors.add(word)
            
            print(e)
    return all_results, errors

