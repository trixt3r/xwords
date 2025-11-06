from conjug_extract import ConjugExtract
from verb import *
from GNode import GenericListNode, GenericNode, NewGrammNode, parcours_largeur_yield


def test_compressed_verb(v_list:list[str]):
    extractor = ConjugExtract()
    v_dict = {v: extractor.extract_verb_info_wiki(v) for v in v_list}
    for v_d in v_dict.values():
        v_nc = Verb_info(v_d)
        v_compressed = Verb_info(v_d, True)
        words_compressed = v_compressed.get_words_list(False)
        words_compressed.sort(key=lambda x:x.ort)
        term_compressed = v_compressed.terminaisons
        root=GenericListNode()
        for t in term_compressed:
            root.addData(t)
        words_nc = v_nc.get_words_list(False)
        words_nc.sort()
        assert words_compressed==words_nc
        # TODO: vérifier aussi getMode, infinitif, participes...
        a_tester = ["Indicatif:Présent:1p","Subjonctif:Imparfait:2s", "Impératif:Présent", "Indicatif:Passé-composé:3p"]
        for t in a_tester:
            r_nc = v_nc.getMode_str(t)
            r_c = v_compressed.getMode_str(t)
            assert(r_nc==r_c) 

    return 

def create_terminaisons_tree(v:Verb_info, reverse=False)->GenericListNode:
    root = GenericListNode()
    for t in v.terminaisons:
        if reverse:
            t = t[::-1]
        root.addData(t)
    return root

def test_terminaison_tree(v_list:list[str])->dict[str, GenericListNode]:
    extractor = ConjugExtract()
    v_dict = {v_str: extractor.extract_verb_info_wiki(v_str) for v_str in v_list}
    verbs = {}
    vToTree = {}
    for v_str, v_d in v_dict.items():
        # v_nc = Verb_info(v_d)
        verbs[v_str] = Verb_info(v_d, compressed=True)
        vToTree[v_str] = create_terminaisons_tree(verbs[v_str])
    
    for i in range(1, len(v_list)):
        v1 = v_list[i-1]
        v2 = v_list[i]
        t1 = vToTree[v1]
        t2 = vToTree[v2]
        assert t1 == t2
    
    return vToTree

def test_reconstruction_et_arbre(v_list:list[str]=["venir", "tressaillir"]):
    extractor= ConjugExtract()
    verbs: dict[str, Verb_info] = {w: Verb_info(extractor.extract_verb_info_wiki(w), compressed=True) for w in v_list}
    trees = {w: (create_terminaisons_tree(verbs[w]),create_terminaisons_tree(verbs[w], reverse=True)) for w in v_list}
    for w, roots in trees.items():
        termi_inverses = []
        for x in parcours_largeur_yield(roots[1]):
            if hasattr(x, "data"):
                termi_inverses.extend([w[::-1] for w in x.data])
        termi_inverses = set(termi_inverses)
        assert termi_inverses == verbs[w].terminaisons
        termi_straight = []
        for x in parcours_largeur_yield(roots[0]):
            if hasattr(x, "data"):
                termi_straight.extend(x.data)
        termi_straight = set(termi_straight)
        assert termi_straight == verbs[w].terminaisons
    return

test_compressed_verb(["tressaillir", "manger", "sauter", "venir"])

test_terminaison_tree(["tressauter", "sauter"])
test_terminaison_tree(["manger", "changer"])
test_terminaison_tree(["venir", "revenir"])
test_terminaison_tree(["tressaillir", "assaillir"])
#NOTE celui-ci bugge
# test_terminaison_tree(["sortir", "partir"])
test_reconstruction_et_arbre(["tressaillir", "manger", "sauter", "venir", "revenir"])


# verbes_problématiques_ok = ["absoudre", "amonceler", "bayer", "breveter", "ciseler", "corser", "débiner", "desseller", "laver", "manger", "raviser", "repayer",  "duveter", "encroûter",  "tressaillir","transparaître","intervenir","prévaloir","survenir","reconquérir","conquérir","souscrire","inscrire","prescrire","proscrire","circoncire","méconnaître","reconnaître","abstraire","détruire","construire","inclure","exclure","réinclure","réconcilier","réintroduire","substituer","dissoudre","absoudre","moudre","coudre","foudroyer","assaillir","breveter","duveter","encroûter","décroûter","héler","rappeler","récapituler","surgeler","refondre","refendre","défendre","ciseler","déciseler","amonceler","débiner","rebiner","desseller","resseller","corser","raviser","repayer"]
# verbes_problématiques = ["asseoir","déchoir","résoudre","sourdre","rasseoir","rafraîchir",]
