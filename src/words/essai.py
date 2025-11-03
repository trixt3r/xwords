# from kiwix_crawler import *
import code
from enum import IntEnum
from retour import *
from pprint import pprint
natures = {'pronom-rel', 'flex-verb', 'nom', 'flex-art-déf', 'var-typo', 'adj-dém', 'part', 'flex-art-indéf', 'flex-adj-pos', 'adj-indéf', 'prénom', 'nom-pr', 'pronom-pers', 'adj', 'adv', 'verb', 'art-part', 'flex-adj', 'flex-adj-indéf', 'onoma', 'adj-int', 'conj-coord', 'flex-adj-dém', 'adv-int', 'flex-nom', 'interj', 'symb', 'flex-pronom-dém', 'adv-rel', 'suf', 'pronom-dém', 'flex-pronom-rel', 'flex-pronom-pers', 'phr', 'flex-prép', 'lettre', 'adj-num', 'pronom-int', 'prép', 'flex-pronom-int', 'adj-rel', 'adj-pos', 'flex-adv', 'pronom', 'nom-fam', 'pronom-indéf', 'flex-pronom-indéf', 'art-indéf', 'flex-adj-int', 'art-déf', 'conj'}
# natures_2 = collect_attribute_values(root, 'nature')
# assert set(natures) == set(natures_2)

####################################################
####################################################
#ça me saoule, je suis une merde en tout
####################################################
####################################################



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

    
    grp2tokens,token2group = arbo.analyze_new()
    # counters_old, grp2tokens,initiaux,finaux, counters_new = arbo.analyze_new()
    # assert(set(counters_old.keys())==set(counters_new.keys()))
    # for k in counters_old.keys():
    #     cnt_new = counters_new[k]
    #     cnt_old = counters_old[k]
    #     assert cnt_new.bitmask == cnt_old[-1]
    #     assert cnt_new.start_counter == cnt_old[-3]
    #     assert cnt_new.end_counter == cnt_old[-2]
    # # MAP token_state (1,2,3,6) TO token count for this state

    # token_count_by_état = {counters_new[k].bitmask:len([t for t in counters_new if counters_new[t].bitmask==counters_new[k].bitmask]) for k in counters_new}
    
    # indices = list(grp2tokens.keys())
    # indices.sort()
    # new_grp2tokens = [grp2tokens[i] for i in indices]
    # grp2tokens = new_grp2tokens

    
    # token2group = {t:gid for gid in range(len(grp2tokens)) for t in grp2tokens[gid]}

    # value2groups = ((v,[token2group[t] for t in arbo.tokenizer(v)]) for v in arbo.values)
    # collisions = {value:states for value,states in value2groups if not len(set(states))==len(states)}

    # # plusieurs tokens à la meme position, impossible. Repartitionner
    # while not len(collisions) == 0:
    #     value, grps = collisions.popitem()
    #     fault_grps = set([g for g in grps if grps.count(g)>1])
    #     if len(fault_grps)==1:
    #         #il faut isoler les tokens de value, donc len(tokens(value))-1 nouveaux groupes
    #         #NOTE on en garde un dans le groupe d'origine, ici le premier qui vient
    #         for i,tok in enumerate(arbo.tokenizer(value)):
    #             if i==0:
    #                 continue
    #             # new_groups.append([tok])
    #             if token2group[tok] in fault_grps:
    #                 #créer un nouveau groupe
    #                 new_group_id = len(grp2tokens)
    #                 grp2tokens.append([tok])
    #                 grp2tokens[token2group[tok]].remove(tok)
    #                 token2group[tok] = new_group_id

    #     token2group = {t:gid for gid in range(len(grp2tokens)) for t in grp2tokens[gid]}
    #     value2groups = ((v,[token2group[t] for t in arbo.tokenizer(v)]) for v in arbo.values)
    #     collisions = {value:states for value,states in value2groups if not len(set(states))==len(states)}
    #     pass
    # if len(collisions) == 0:
    #     print("woohoo!")

    for i,grp in enumerate(grp2tokens):
        print(f"grp {i} :  {len(grp2tokens[i])} tokens {(len(grp2tokens[i])+1).bit_length()} bits")
        print(f"{grp2tokens[i]}")
        pass

    
    def my_token_to_grp(tok:str,grp2tokens)->int:
        for gid, tokens in enumerate(grp2tokens):
            if tok in tokens:
                return gid
        raise Exception(f"token not found {tok}")
    
    def create_codes(grp2tokens:list[list[str]], token2group:list[int], values:list[str])->dict[str:tuple[int]]:
        ret = {}
        for val in values:
            val_compress:list[int] = [0]*len(grp2tokens)
            tokens = arbo.tokenizer(val)
            for tok in tokens:
                grp = token2group[tok]
                val_compress[grp] = grp2tokens[grp].index(tok)+1
            ret[val] = tuple(val_compress)
        return ret
    #NOTE la suite est bonne à jeter haha

    def testo3_suite(word2code:dict[str, tuple[int]]):
        # calc = [set()]*len(results[results.keys()[0]])
        calc:list[set] = [set() for _ in range(len(word2code[list(word2code.keys())[0]]))]
        for v,code in word2code.items():
            for i,c in enumerate(code):
                calc[i].add(c)

        # for each token position, the count of distinct possible tokens
        #NOTE pourquoi -1?
        tokens_count = [len(c)-1 for c in calc]
        bit_fields_lengths = [c.bit_length() for c in [len(c)-1 for c in calc]]
        #NOTE minus one for the zero value
        remaining_codes = [2**b_f_l - tc - 1 for tc,b_f_l in zip(tokens_count, bit_fields_lengths)]
        return bit_fields_lengths

    # result = repartis_tokens3(grp2tokens)
    word2code = create_codes(grp2tokens, token2group, arbo.values)
    assert len(word2code) == len(arbo.values)
    assert len(set(word2code.values())) == len(arbo.values)
    bit_field_lengths2 = [len(grp).bit_length() for grp in grp2tokens]
    bit_fields_lengths = testo3_suite(word2code)
    assert bit_field_lengths2 == bit_fields_lengths

    NatTok=IntEnum("NatTok", {(w.replace("-","_").upper(), token_to_bits(code,bit_fields_lengths)) for w, code in word2code.items()})
    
    tzs = token_to_bits(word2code['var-typo'], bit_fields_lengths)
    ret = bits_to_token(tzs, bit_fields_lengths)
    ##########################################################################################################
    #TOUT EST Là !
    #################
    for nat in arbo.values:
        print(f"{nat} : {word2code[nat]}  -> {token_to_bits(word2code[nat], bit_fields_lengths)} -> {bits_to_token(token_to_bits(word2code[nat], bit_fields_lengths), bit_fields_lengths)}")
        assert bits_to_token(token_to_bits(word2code[nat], bit_fields_lengths), bit_fields_lengths) == word2code[nat]
    ##########################################################################################################
    
    return

test_arbo(natures)



