# from kiwix_crawler import *
import code
from enum import IntEnum
from retour import *
from bits import *
from pprint import pprint
# natures_2 = collect_attribute_values(root, 'nature')
# assert set(natures) == set(natures_2)

####################################################
####################################################
#ça me saoule, je suis une merde en tout
# mais non, faut pas dire ça
####################################################
####################################################


def test_arbo(values_set):
    arbo = ArboComp(values_set)
    # for n in values_set:
    #     arbo.add_tokens(n)

    for n in arbo.values:
        print(n , arbo.comp_tokens(n))

    pprint(arbo.tokens)

    
    NatTok= arbo.analyze_new()
    for tok in NatTok.valid_words():
        print(f"valid word token: {tok.name} {tok.name_str} {tok.value}")

    for tok in NatTok:
        if not tok.valid_word:
            print(f"non-valid word token: {tok.name} {tok.name_str} {tok.value}")

    a_tester = [NatTok.ADJ,NatTok.FLEX, NatTok.FLEX_ADV]
    for word in values_set:
        tok = NatTok[word.replace("-","_").upper()]
        print(f"{tok} {tok.name_str} {tok.name} {tok.value}")
        print(" ".join([f"     has {n.name} " if tok.has_token(n) else f"       has not {n.name}" for n in a_tester]))
        print("*********************")

    # for x in NatTok:
    #     print(f"{x.name} {x.has_token(NatTok.ADJ)} bitmask:{x.bitmask:b} offset:{x.offset}")


    # for n in NatTok:
    #     assert n.value == token_to_bits(word_to_code(arbo.tokenizer(n.name.replace("_","-").lower()), grp2tokens), bit_fields_lengths)
    #     # print(f"nature {n} code {get_code(n.name.replace('_','-').lower(), grp2tokens)} bin {bin(n.value)} bits {n.value:0{sum(bit_fields_lengths)}b}")

    #     for tok in [NatTok.SYMB, NatTok.ADJ, NatTok.VERB, NatTok.FLEX, NatTok.NOM, NatTok.FLEX_ADJ]:
    #         if tok==NatTok.NOM and "PRONOM" in n.name or "ONOMA" in n.name or "PRÉNOM" in n.name:
    #             print(f"skip nom/pronom/prénom/onoma test for {n.name} ")
    #             continue
    #         if tok.name in n.name:
    #             assert n.has_token(tok), f"nature {n} {n.name} incorrectly identified as NOT {tok.name} {tok.value}"
    #         else:
    #             assert not n.has_token(tok), f"nature {n} {n.name} incorrectly identified as {tok.name} {tok.value}"

    # [(n,word_to_group_path(n.name.replace("_","-").lower())) for n in NatTok]

    return NatTok

natures = {'pronom-rel', 'flex-verb', 'nom', 'flex-art-déf', 'var-typo', 'adj-dém', 'part', 'flex-art-indéf', 'flex-adj-pos', 'adj-indéf', 'prénom', 'nom-pr', 'pronom-pers', 'adj', 'adv', 'verb', 'art-part', 'flex-adj', 'flex-adj-indéf', 'onoma', 'adj-int', 'conj-coord', 'flex-adj-dém', 'adv-int', 'flex-nom', 'interj', 'symb', 'flex-pronom-dém', 'adv-rel', 'suf', 'pronom-dém', 'flex-pronom-rel', 'flex-pronom-pers', 'phr', 'flex-prép', 'lettre', 'adj-num', 'pronom-int', 'prép', 'flex-pronom-int', 'adj-rel', 'adj-pos', 'flex-adv', 'pronom', 'nom-fam', 'pronom-indéf', 'flex-pronom-indéf', 'art-indéf', 'flex-adj-int', 'art-déf', 'conj'}

NatTok = test_arbo(natures)

# from GNode import *

# root=GenericNode()
# for nat in natures:
#     root.addData(nat)

# print(root)



