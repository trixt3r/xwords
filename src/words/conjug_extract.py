import re
from typing import Any
from bs4 import BeautifulSoup
import requests
import warnings

from verb import Verb_info, VerbModeEnum
from words_tuple import word_t
from scrap_base import *


class ConjugExtract(object):
    def select_types_conjugs(self, v, soup):
        types_conjug = extract_conjug_types(soup)
        
        #NOTE ci-dessous, quelques hacks pour les formes multiples
        #NOTE pour l'instant, on ne renvoie qu'une seule forme, active de préférence, ou pronominale si c'est la seule
        #NOTE Lorsque forme traditionnelle et forme de 1990, on garde la forme de 1990
        #NOTE lorsque forme avec y/avec i, on garde la forme avec y
        #TODO il faudrait pouvoir gérer tout ça dans verb_info

        if len(types_conjug)==4:
            forme_1990 = False
            for t in types_conjug:
                if "1990" in t[0]:
                    forme_1990 = True
                    break
            if forme_1990:
                types_conjug = [x for x in types_conjug if "1990" in x[0]]
            else:
                pass
                # types_conjug = [(x[0].split()[0],x[1]) for x in types_conjug if not "traditionnelle" in x[0]]
            if len(types_conjug)==4 and v=="résoudre":
                #NOTE cas particulier résoudre
                types_conjug = types_conjug[:2]
                warnings.warn("cas particulier: résoudre, on droppe")
                pass
            if len(types_conjug)==4:
                tmp = [conj for conj in types_conjug if "(finale -" in conj[0]]
                if len(tmp)==4:
                    finales = set([conj[0][conj[0].index("(finale -")+9:-1] for conj in tmp])
                    selected_finale = None
                    for f in finales:
                        if 'è' in f:
                            selected_finale = f
                            break
                    if selected_finale is None:
                        raise ExtractException(f"problème de sélection de finale pour le verbe {v}")
                    types_conjug = [conj for conj in types_conjug if selected_finale in conj[0]]
                else:
                    tmp = [conj for conj in types_conjug if "avec «\xa0y\xa0»" in conj[0]]
                    if len(tmp) == 2:
                        if v == "bayer":
                            types_conjug = [(tmp[0][0] + " active", tmp[0][1])]
                            warnings.warn("cas particulier: bayer (2 orth, 2 prononciations) on garde une seule forme")
                            pass
                        else:
                            types_conjug = tmp
                            types_conjug[0] = (types_conjug[0][0] + " active", types_conjug[0][1])
                            types_conjug[1] = (types_conjug[1][0] + " pronominale", types_conjug[1][1])
                            warnings.warn(f"deux variantes orthographiques pour le verbe {v}, on garde la forme avec « y »")
                    else:
                        if v == "rasseoir":
                            warnings.warn("cas particulier: rasseoir on garde la forme \"assois\"")
                            types_conjug = [conj for conj in types_conjug if "en -oi- / -oy-" in conj[0]]
                            pass
                        else:
                            raise ExtractException(f"problème de finales pour le verbe {v}")

        if len(types_conjug)==2:
            if "active" in types_conjug[0][0] and "pronominale" in types_conjug[1][0]:
                pass
            elif "traditionnelle" in types_conjug[0][0] and "de 1990" in types_conjug[1][0]:
                pass
            elif "Avec «\xa0y\xa0»" in types_conjug[0][0] and "Avec «\xa0i\xa0»" in types_conjug[1][0]:
                pass
            else:
                forme1 = types_conjug[0][0]
                forme2 = types_conjug[1][0]
                if forme1.startswith("Prononciation ") and forme2.startswith("Prononciation "):
                    forme1 = forme1[14:]
                    forme2 = forme2[14:]
                if forme1.startswith("\\") and forme1.endswith("\\") and forme2.startswith("\\") and forme2.endswith("\\"):
                    types_conjug = [types_conjug[1]]
                    warning_msg = f"deux variantes orthographiques pour le verbe {v}, on garde la seconde"
                elif forme1.startswith("en -") and forme2.startswith("en -"):
                    #NOTE on a deux formes inusitées, on garde la seconde
                    types_conjug = [types_conjug[1]]
                    warning_msg = f"deux variantes orthographiques pour le verbe {v}, on garde la seconde"
                    warnings.warn(warning_msg)
                elif v=="déchoir":
                    #NOTE cas particulier déchoir
                    types_conjug = [types_conjug[0]]
                    warnings.warn(f"cas particulier: déchoir on garde la forme 1")
                else:
                    raise ExtractException(f"problème conjugaison pour {v} forme1='{forme1}' forme2='{forme2}'")
        return types_conjug

    def extract_verb_info_wiki(self, v:str) -> dict[str,Any]:
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
        if v=="sourdre":
            #NOTE cas particulier sourdre
            warnings.warn("cas particulier: sourdre, on droppe tout")
            return None
        
        self.current_verb = v
        transitif = True
        page = requests.get(f"{BASE_VERB_URL}{v}")
        
        soup = BeautifulSoup(page.content, "html.parser")
        extract_verbe_group(soup)
        # types_conjug =extract_conjug_types(soup)
        types_conjug = self.select_types_conjugs(v, soup)

        
        # conjug_divs = soup.find_all(id=re.compile("^mb0og"))
        conjug_divs = [soup.find(id=f"mb0og{x[1]}") for x in types_conjug]
        assert len(conjug_divs)==len(types_conjug)
        if len(conjug_divs)>2:
            conjug_divs = [cd for cd in conjug_divs if not "avec élision" in types_conjug[conjug_divs.index(cd)][0]]
        if len(conjug_divs)>2:
            if v == "asseoir":
                warnings.warn("cas particulier: asseoir on garde la forme \"assois\"")
                conjug_divs = [cd for cd in conjug_divs if "assois" in types_conjug[conjug_divs.index(cd)][0]]
            elif v == "rafraîchir":
                warnings.warn("cas particulier: rafraîchir on droppe la forme 1990")
                conjug_divs = [cd for cd in conjug_divs if not "1990" in types_conjug[conjug_divs.index(cd)][0]]
        if len(conjug_divs)>2:
            print(conjug_divs)
            print(types_conjug)
            raise ExtractException(f"trop de formes de conjugaison pour {v}")
        # conjug = None
        if len(conjug_divs)==0:
            #le verbe n'a qu'une seule forme de conjugaison
            conjug_divs=[soup.find(id="mw-content-text")]
            if len(conjug_divs)==0:
                raise ExtractException(f"erreur de conjugaison pour {v}")

        
        all_verb_infos=[]
        v_info = None
        for div in conjug_divs:
            try:
                _type = self.extract_conjug_form(div)
                all_verb_infos.append(_type)
            except ExtractException as e:
                warnings.warn(f"erreur de conjugaison pour {v}: {e}")
                all_verb_infos.append(None)
                continue
        #TODO: extraire chaque forme de conjugaison
        #TODO: les comparer pour compresser si elles sont identiques
        #TODO: gérer les erreurs (ex: forme inusitée)
        #TODO: il faudra étendre verb_info pour gérer les différentes formes (active, pronominale, impersonnelle, etc)
        if len(all_verb_infos) == 2:
            if "traditionnelle" in types_conjug[0][0] and "de 1990" in types_conjug[1][0]:
                #NOTE on a la forme traditionnelle et la forme de 1990
                #on garde la forme de 1990
                v_info = all_verb_infos[1]
            elif "Avec «\xa0y\xa0»" in types_conjug[0][0] and "Avec «\xa0i\xa0»" in types_conjug[1][0]:
                #NOTE on a la forme avec « y » et la forme avec « i »
                v_info = all_verb_infos[0]
            else:
                #NOTE a priori forme active et pronominale
                if not None in all_verb_infos:
                    ok = compare_verb_info(all_verb_infos[0], all_verb_infos[1])
                    if not ok:
                        warnings.warn(f"différence entre les deux formes de conjugaison pour \"{v}\"")
                    warnings.warn(f"deux formes de conjugaison pour \"{v}\", on garde la première")
                    #NOTE que faire ? on garde la première ?
                    v_info = all_verb_infos[0]
                else:
                    #NOTE une des formes a échoué
                    if all_verb_infos[0] is None:
                        v_info = all_verb_infos[1]
                    else:
                        v_info = all_verb_infos[0]
                    warning_msg = f"une des formes de conjugaison a échoué pour {v}"
                    warnings.warn(warning_msg)
        elif len(all_verb_infos)==1:
            v_info = all_verb_infos[0]

        # try :
        #     v_info = extract_conjug_form(conjug_divs[0])
        # except ExtractException as e:
        #     v_info = extract_conjug_form(conjug_divs[1])

        formes = [ bt.find("a").text.strip() for bt in soup.find_all('div', id=re.compile("^mb0bt"))]
        # for f in formes:
        #     assert f[:12] == "Conjugaison "
        formes = [f[12:] for f in formes if f.startswith("Conjugaison ")]
        v_info["Part"] = self.complete_participes(v_info["Part"])
        return v_info

    def complete_participes(self, participes:dict):
        """
        Complète les participes pour les genres et nombres
        :param participes: dictionnaire avec les clés "Pr" et "Pa" 
        contenant chacun un tuple (orthographe, api)
        :return: dictionnaire avec les clés "Pr" et "Pa" 
        contenant chacun un dictionnaire avec les clés "ms", "fs", "mp", "fp"
        """
        présent = {
            "ms":word_t(participes["Pr"][0],participes["Pr"][1]), 
            "fs":word_t(participes["Pr"][0]+"e",participes["Pr"][1]+"t"), 
            "mp":word_t(participes["Pr"][0]+"s",participes["Pr"][1]), 
            "fp":word_t(participes["Pr"][0]+"es",participes["Pr"][1]+"t")
            }
        ref = participes["Pa"][0]
        suffixe_phonétique_féminin = ""
        suffixe_orthographique_masculin = "s"
        if ref[-1] in ["é","i","u"]:
            pass
        elif ref[-1] == 's':
            suffixe_phonétique_féminin = 'z'
            suffixe_orthographique_masculin = ""
        elif ref[-1] == 't':
            suffixe_phonétique_féminin = 't'
        else:
            raise Exception(f"suffixe phonétique du participe passé inconnu pour {ref}")
        
        passé = {
            "ms":word_t(participes["Pa"][0],participes["Pa"][1]), 
            "fs":word_t(participes["Pa"][0]+"e",participes["Pa"][1]+suffixe_phonétique_féminin),
            "mp":word_t(participes["Pa"][0]+suffixe_orthographique_masculin,participes["Pa"][1]),
            "fp":word_t(participes["Pa"][0]+"es",participes["Pa"][1]+suffixe_phonétique_féminin)
            }
        return {"Pr":présent, "Pa":passé}

    #extrait les infos d'un mode + temps
    #TODO: verbes impersonnels
    def extract_temps(self, table):
        lines = table.find_all("tr")
        temps = lines[0].text.strip("\n")
        with_aux = False
        # print("****************** %s *******************" % temps)

        if temps in ["Passé", "Passé composé", "Plus-que-parfait", "Passé antérieur", "Futur antérieur"]:
            with_aux=True
            return (temps, [])
        

        desinences = []
        i1 = 1
        i2 = 3
        #typiquement: impératif
        if len(lines) == 4:
            i2 = 2
        if len(lines) == 3:
            #NOTE probablement un verbe impersonnel
            warnings.warn(f'ici c\'est calqué pour le verbe corser mode pronominal - impersonnel')
            desinences = []
            for line in lines[1:]:
                tds = line.find_all("td")
                w = tds[1].text.strip("\n").strip("\xa0").strip("\\")
                api = extract_api(tds[-1].span.text)
                desinences.append(word_t('',''))
                desinences.append(word_t('',''))
                desinences.append(word_t(w, api))
            if len(desinences) == 6:
                return (temps, desinences)
            raise Exception("CRASH verbes impersonnels non gérés")
            
        if len(lines) == 7 or len(lines) == 4:
            for line in lines[1:]:
                tds = line.find_all("td")
                #NOTE ici à l'arrache, on gère les formes pronominales à l'impératif
                if tds[i1].text.strip() == "-toi":
                    i1=0
                # print("################# %d %s" % (len(tds), line.text))
                w = tds[i1].text.strip("\n").strip("\xa0").strip("\\")
                # api = tds[i2].text.strip("\n").strip("\\").strip("\xa0")

                api = extract_api(tds[i2].span.text)
                #NOTE toujours pour le cas pronominal/impératif
                #on supprime -toi -nous -vous de l'api
                if i1==0:
                    tmp_idx = api.rfind(".")
                    if api[tmp_idx+1:] in ["twa","vu","nu"]:
                        api = api[:tmp_idx]

                # api = tds[i2].span.text.strip("\\").replace(".)",").").replace("ɡ","g")
                
                # print("%s %s" % (w, api))
                desinences.append(word_t(w, api))
            pass
        return (temps, desinences)
    
    #TODO on extrait que la première forme (personnelle a priori)
    #TODO il faudrait tager l'objet renvoyé pour indiquer les autres formes
    #TODO il faudrait surtout extraire les autres formes; ici, on considère que les autres formes 
    #TODO ont des orthographes identiques 
    #dictionnaire retourné
    def extract_conjug_form(self,conjug,pronominale=False):
        v_info = {}

        # NOTE h3 sur wikipedia, h2 pour kiwix ? en fait ça dépend ...
        # modes_imp = conjug.find("h2", id="Modes_impersonnels")
        modes_imp = conjug.find("h2", id=lambda x: x.startswith("Modes_impersonnels"))
        if modes_imp is None:
            # modes_imp = conjug.find("h3", id="Modes_impersonnels")
            modes_imp = conjug.find("h3", id=lambda x: x.startswith("Modes_impersonnels"))
        if modes_imp is None:
            print("S1")
            #NOTE probablement un verbe réfléchi
            raise ExtractException(f"pas de modes impersonnels pour {self.current_verb}")
        # Auxiliaires, participes, infinitif
        auxiliaire = ""
        infinitif_html = modes_imp.find_next("a", title="infinitif")
        while not infinitif_html.name == 'tr':
            infinitif_html = infinitif_html.parent
        infinitif_html = infinitif_html.find_all("td")
        api_infinitif = extract_api(infinitif_html[3].text.strip())
        #NOTE ici encore, un hack pour les verbes pronominaux
        if api_infinitif.split()[0] == "sə": 
            api_infinitif = api_infinitif[3:]
        elif api_infinitif.startswith("s‿"):
            api_infinitif = api_infinitif[2:]
        v_info["inf"] = word_t(self.current_verb, api_infinitif)
        
        # TODO: gérer le cas des doubles auxiliaires
        auxiliaire = infinitif_html[4].text.strip("\n").strip("\\").strip("\xa0").strip("\n")
        auxiliaire2 = infinitif_html[4].text.strip()
        assert auxiliaire == auxiliaire2, f"auxiliaire différent: '{auxiliaire}' vs '{auxiliaire2}'"
        if "être" in auxiliaire:
            auxiliaire = "être"
        elif "avoir" in auxiliaire:
            auxiliaire = "avoir"
        else:
            raise ExtractException(f"auxiliaire inattendu: '{self.current_verb} {auxiliaire}'")
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

        verbes_modes = ("Indicatif", "Subjonctif", "Conditionnel", "Impératif")
        v_info.update({k:{} for k in verbes_modes})

        for mode in verbes_modes:
            # NOTE idem h3/h2
            # times = conjug.find('h2', id=mode)
            times = conjug.find('h2', id=lambda x: x.startswith(mode))
            if times is None:
                # times = conjug.find('h3', id=mode)
                times = conjug.find('h3', id=lambda x: x.startswith(mode))
            times = times.find_next("div").find("table").find_all("table")
            # print("vide")
            for t in times:
                temps = self.extract_temps(t)
                v_info[mode][temps[0]] = temps[1]
        return v_info












