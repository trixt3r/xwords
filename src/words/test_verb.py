from typing import Optional
from verb import *


from scrapping import *

def test_verb(verb_str:str, tuples_test:list[tuple[int,str,str,str,str]]=[])->Optional[Verb_info]:
    verb_data = new_master_scrapper(verb_str)
    verb_info: Optional[Verb_info] = None
    for vd in verb_data:
        if vd["nature"] == "verb" and "conjugaison" in vd:
            verb_info = Verb_info(vd["conjugaison"])
    for t in tuples_test:
        personne_idx, personne_nbr, mode_s, temps_s, expected_form = t
        form = verb_info.getMode_str(f"{mode_s}:{temps_s}:{personne_idx}{personne_nbr}")
        # form2 = verb_info.getMode(VerbModeEnum.from_str(mode_s), VerbTempsEnum.from_str(temps_s), personne_idx)
        
        brut_personne_idx = personne_idx -1
        if personne_nbr == 'p':
            brut_personne_idx +=3
        form3 = ConjVerbStr(Verb_flex(verb_info, VerbModeEnum.fromName(mode_s), VerbTempsEnum.fromName(temps_s), brut_personne_idx))
        assert form.ort == form3, f"Erreur pour le verbe {verb_str} en {mode_s}:{temps_s} personne {personne_idx}, attendu {form}, obtenu {form3}"
        # if isinstance(form, list):
        #     form = form[personne_idx]
        assert form.ort == expected_form, f"Erreur pour le verbe {verb_str} en {mode_s}:{temps_s} personne {personne_idx+1}, attendu {expected_form}, obtenu {form.ort}"
    return verb_info

verb_data = new_master_scrapper("voyager")

verb_data = new_master_scrapper("manger")
verb_info: Optional[Verb_info] = None
for vd in verb_data:
    if vd["nature"] == "verb" and "conjugaison" in vd:
        verb_info = Verb_info(vd["conjugaison"])

flex1 = Verb_flex(verb_info, VerbModeEnum.Indicatif, VerbTempsEnum.Présent, 1)
print(flex1)
print(flex1.get_word())
special_str = ConjVerbStr(flex1)
print(special_str)

test_verb("manger", 
            [(1,'s','Indicatif','Présent','mange'),
             (2,'s','Indicatif','Présent','manges'),
             (3,'s','Indicatif','Présent','mange'),
             (1,'p','Indicatif','Présent','mangeons'),
             (2,'p','Indicatif','Présent','mangez'),
             (3,'p','Indicatif','Présent','mangent'),
             (1,'s', 'Indicatif', "Imparfait","mangeais"),
             (2,'s', 'Indicatif', "Imparfait","mangeais"),
             (3,'s', 'Indicatif', "Imparfait","mangeait"),
             (1,'p', 'Indicatif', "Imparfait","mangions"),
             (2,'p', 'Indicatif', "Imparfait","mangiez"),
             (3,'p', 'Indicatif', "Imparfait","mangeaient")
        ])
