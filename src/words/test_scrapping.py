from scrapping import *
from flextable import FlexType, Flextable

mots = ["les", "aux", "des,", "la","des","donc", "où", "quand", "mais", "si", "et", "or", "ni", "car", "comment", "carrément", "pourquoi", "quel", "quelle", "quelles", "quels", "lequel", "laquelle", "lesquelles", "lesquels", "auquel", "à laquelle", "auxquelles", "auxquels", "duquel", "de laquelle", "desquelles", "desquels"]
result = {}
for w in mots:
    try:
        result[w] = new_master_scrapper(w)
    except Exception as e:
        print(f"Erreur lors de l'extraction pour {w}: {e}")
        
print(result)
words_list=load_words_list("data/gutenberg.txt")

voyager, errors_voyeger = bulk_scrap(["voyager"])
# print(voyager[0].)
bulk_scrap(["mangiez"])

ok, errors = test_scrapper(words_list,100)
print(f"ok ratio: {len(ok)}/200, errors: {len(errors)}")
for k,words in ok.items():
    for w in words:
        if "flex" in w:
            flextable = Flextable(w["flex"])
            for cas,flexion in w["flex"].items():
                assert flexion == flextable.get_flexion(FlexType[cas]) , f"Erreur de flexion pour le mot {k} cas {cas}: attendu {flexion}, obtenu {flextable.get_flexion(FlexType[cas])}"
problemes_resolus = ["poisseux", "sableuse", "outrageante", "temps", "aurignacien"]
problemes = ["angiosperme", "chauve", "écœurez", "écoeurez", "titillait", "tissaient", "sculpturaux", "débecqueter", "perturbée", "documentée", "rucher"]
verbes_intransitifs = set(["dormir", "courir", "venir", "arriver", "partir", "naître", "mourir", "tomber", "rester", "séjourner", "habiter", "exister", "subsister", "résider", "surgir", "survenir", "advenir", "émerger","aller", "arriver", "courir", "venir", "pleurer", "nager"])
# results, errors = bulk_scrap(problemes)
# avec "rapides" c'est relou. 
# Le block adjectif est ok: il indique "masculin et féminin identique"
# par contre la forme de nom commun n'indique rien, il faut deviner 

# test_parse_flextable("rapides")
# results = [(w,test_parse_flextable(w)) for w in ["ami","amie","amis","amies","temps","belle","beau","beaux","belles","heureux","heureuse","heureuses","heureuxs","rapide","rapides","lent","lente","lentes","lents", "cartouche", "cartouches"]]
