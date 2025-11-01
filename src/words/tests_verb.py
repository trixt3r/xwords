from conjug_extract import ConjugExtract
from verb import *

def test_compressed_verb(v_list:list[str]):
    extractor = ConjugExtract()
    v_dict = {v: extractor.extract_verb_info_wiki(v) for v in v_list}
    for v_d in v_dict.values():
        v_nc = Verb_info(v_d)
        v_compressed = Verb_info(v_d, True)
        words_compressed = v_compressed.get_words_list(False)
        words_compressed.sort(key=lambda x:x.ort)
        words_nc = v_nc.get_words_list(False)
        words_nc.sort()
        assert words_compressed==words_nc
        # TODO: vérifier aussi getMode, infinitif, participes...
        a_tester = ["Indicatif:Présent:1p","Subjonctif:Imparfait:2s", "Impératif:Présent", "Indicatif:Passé-composé:3p"]
        for t in a_tester:
            r_nc = v_nc.getMode(t)
            r_c = v_compressed.getMode(t)
            assert(r_nc==r_c) 

    return 

    res = [w for w in parcours_verbe_dict(v1_dict)]
    res.sort(key=lambda x:x.ort)


    words = [w.ort for w in res]
    apis = [w.api for w in res]
    ort_radic = search_gcd(words)
    api_radic = search_gcd(apis)
    print(f" {v1} {ort_radic} {api_radic}")
    print("#")
    compressed,ort_radic, api_radic = compress_verb_dict(v1_dict)
    print(compressed)
    ort_term = [x.ort for x in parcours_verbe_dict(compressed)]
    api_term = [x.api for x in parcours_verbe_dict(compressed)]
    decompressed = decompress_verb_dict(compressed, ort_radic, api_radic)
    res_decompressed = [w for w in parcours_verbe_dict(decompressed)]
    res_decompressed.sort(key=lambda x:x.ort)


    words_decompressed = [w.ort for w in res_decompressed]
    apis_decompressed = [w.api for w in res_decompressed]
    assert words == words_decompressed
    assert apis == apis_decompressed

    v1_compressed = Verb_info(v1_dict,True)
    print([x for x in v1_compressed.terminaisons])
    words_c = v1_compressed.get_words_list(False)
    words_c.sort(key=lambda x:x.ort)

    words_nc = v1.get_words_list(False)
    words_nc.sort()

    assert words_c==words_nc


test_compressed_verb(["tressaillir", "manger"])


# verbes_problématiques_ok = ["absoudre", "amonceler", "bayer", "breveter", "ciseler", "corser", "débiner", "desseller", "laver", "manger", "raviser", "repayer",  "duveter", "encroûter",  "tressaillir","transparaître","intervenir","prévaloir","survenir","reconquérir","conquérir","souscrire","inscrire","prescrire","proscrire","circoncire","méconnaître","reconnaître","abstraire","détruire","construire","inclure","exclure","réinclure","réconcilier","réintroduire","substituer","dissoudre","absoudre","moudre","coudre","foudroyer","assaillir","breveter","duveter","encroûter","décroûter","héler","rappeler","récapituler","surgeler","refondre","refendre","défendre","ciseler","déciseler","amonceler","débiner","rebiner","desseller","resseller","corser","raviser","repayer"]
# verbes_problématiques = ["asseoir","déchoir","résoudre","sourdre","rasseoir","rafraîchir",]

# results = {verb: extractor.extract_verb_info_wiki(verb) for verb in verbes_problématiques_ok}
# for verb, info in results.items():
#     verb_struct = Verb_info(info)
# results_2 = {verb: extractor.extract_verb_info_wiki(verb) for verb in verbes_problématiques}
