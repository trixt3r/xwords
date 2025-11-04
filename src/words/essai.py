# from kiwix_crawler import *
import code
from enum import IntEnum
from retour import *
from pprint import pprint
# natures_2 = collect_attribute_values(root, 'nature')
# assert set(natures) == set(natures_2)

####################################################
####################################################
#ça me saoule, je suis une merde en tout
# mais non, faut pas dire ça
####################################################
####################################################

def bitmask(length,offset):
    return ((1 << length) - 1) << offset

def bitmask_for_group(grps2tokens,gid):
    return bitmask(len(grps2tokens[gid]).bit_length(), sum(len(grps2tokens[g]).bit_length() for g in range(gid)))
    bit_fields_lengths = [len(grp).bit_length() for grp in grps2tokens]
    total_bits = sum(bit_fields_lengths)
    mask = (1 << total_bits) - 1
    return mask

def token_to_bits(token_code, bit_fields_lengths):
    bits = 0
    shift = 0
    for code, b_f_l in zip(reversed(token_code), reversed(bit_fields_lengths)):
        bits |= (code << shift)
        shift += b_f_l
    return bits
    
def bits_to_token(bits, bit_fields_lengths):
    token_code = []
    shift = sum(bit_fields_lengths)
    for b_f_l in bit_fields_lengths:
        shift -= b_f_l
        mask = (1 << b_f_l) - 1
        code = (bits >> shift) & mask
        token_code.append(code)
    return tuple(token_code)

def test_arbo(values_set):
    arbo = ArboComp()
    for n in values_set:
        arbo.add_tokens(n)

    for n in arbo.values:
        print(n , arbo.comp_tokens(n))

    pprint(arbo.tokens)

    
    grp2tokens= arbo.analyze_new()
    
    for i,grp in enumerate(grp2tokens):
        print(f"grp {i} :  {len(grp2tokens[i])} tokens {(len(grp2tokens[i])+1).bit_length()} bits")
        print(f"{grp2tokens[i]}")
        pass

    
    def my_token_to_grp(tok:str,grp2tokens)->int:
        for gid, tokens in enumerate(grp2tokens):
            if tok in tokens:
                return gid
        raise Exception(f"token not found {tok}")
    
    def get_code(word:str, grp2tokens:list[list[str]])->tuple[int]:
        code = [0]*len(grp2tokens)
        for tok in arbo.tokenizer(word):
            grp = my_token_to_grp(tok, grp2tokens)
            code[grp] = grp2tokens[grp].index(tok)+1
        return tuple(code)

    bit_fields_lengths = [len(grp).bit_length() for grp in grp2tokens]



    NatTok=IntEnum("NatTok", {(w.replace("-","_").upper(), token_to_bits(get_code(w, grp2tokens),bit_fields_lengths)) for w in arbo.values})
    def is_adj(nature:NatTok)->bool:
        return nature.value & NatTok.ADJ.value == NatTok.ADJ.value
    
    for n in NatTok:
        assert n.value == token_to_bits(get_code(n.name.replace("_","-").lower(), grp2tokens), bit_fields_lengths)
        print(f"nature {n} code {get_code(n.name.replace('_','-').lower(), grp2tokens)} bin {bin(n.value)} bits {n.value:0{sum(bit_fields_lengths)}b}")
        if "ADJ" in n.name:

            assert is_adj(n), f"nature {n} {n.name} incorrectly identified as NOT adj {NatTok.ADJ.value}"
        else:
            assert not is_adj(n), f"nature {n} {n.name} incorrectly identified as adj {NatTok.ADJ.value}"
    return NatTok

natures = {'pronom-rel', 'flex-verb', 'nom', 'flex-art-déf', 'var-typo', 'adj-dém', 'part', 'flex-art-indéf', 'flex-adj-pos', 'adj-indéf', 'prénom', 'nom-pr', 'pronom-pers', 'adj', 'adv', 'verb', 'art-part', 'flex-adj', 'flex-adj-indéf', 'onoma', 'adj-int', 'conj-coord', 'flex-adj-dém', 'adv-int', 'flex-nom', 'interj', 'symb', 'flex-pronom-dém', 'adv-rel', 'suf', 'pronom-dém', 'flex-pronom-rel', 'flex-pronom-pers', 'phr', 'flex-prép', 'lettre', 'adj-num', 'pronom-int', 'prép', 'flex-pronom-int', 'adj-rel', 'adj-pos', 'flex-adv', 'pronom', 'nom-fam', 'pronom-indéf', 'flex-pronom-indéf', 'art-indéf', 'flex-adj-int', 'art-déf', 'conj'}

NatTok = test_arbo(natures)



