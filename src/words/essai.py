# from kiwix_crawler import *
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

    def testo3_suite(results):
        # calc = [set()]*len(results[results.keys()[0]])
        calc = [set() for _ in range(len(results[list(results.keys())[0]]))]
        for v,code in results.items():
            for i,c in enumerate(code):
                calc[i].add(c)
        
        # for each token position, the count of distinct possible tokens
        #NOTE pourquoi -1?
        tokens_count = [len(c)-1 for c in calc]
        bit_fields_lengths = [c.bit_length() for c in tokens_count]
        #NOTE minus one for the zero value
        remaining_codes = [2**b_f_l - tc - 1 for tc,b_f_l in zip(tokens_count, bit_fields_lengths)]
        return tokens_count, bit_fields_lengths, remaining_codes

    # result = repartis_tokens3(grp2tokens)
    result = create_codes(grp2tokens, token2group, arbo.values)
    assert len(result) == len(arbo.values)
    assert len(set(result.values())) == len(arbo.values)

    tokens_count, bit_fields_lengths, remaining_codes = testo3_suite(result)
    
    tzs = token_to_bits(result['var-typo'], bit_fields_lengths)
    ret = bits_to_token(tzs, bit_fields_lengths)
    ##########################################################################################################
    #TOUT EST Là !
    #################
    for nat in values_set:
        print(f"{nat} : {result[nat]}  -> {token_to_bits(result[nat], bit_fields_lengths)} -> {bits_to_token(token_to_bits(result[nat], bit_fields_lengths), bit_fields_lengths)}")
        assert bits_to_token(token_to_bits(result[nat], bit_fields_lengths), bit_fields_lengths) == result[nat]
    ##########################################################################################################
    
    codés={token_to_bits(result[nat], bit_fields_lengths):nat for nat in values_set}
    print(f"coded token max length : {max(codés.keys()).bit_length()}")
    pprint(tokens_count)
    pprint(bit_fields_lengths)
    pprint(remaining_codes)
    ##########################################################################################################
    #TOUT EST Là !
    #################
    for nat in values_set:
        print(f"{nat} : {result[nat]}  -> {token_to_bits(result[nat], bit_fields_lengths)} -> {bits_to_token(token_to_bits(result[nat], bit_fields_lengths), bit_fields_lengths)}")
        assert bits_to_token(token_to_bits(result[nat], bit_fields_lengths), bit_fields_lengths) == result[nat]

    return

def test_arbo_first(values_set):
    arbo = ArboComp()
    for n in values_set:
        arbo.add_tokens(n)

    for n in arbo.values:
        print(n , arbo.comp_tokens(n))

    pprint(arbo.tokens)

    for n in arbo.values:
        print(n , arbo.comp_tokens(n))

    counters_old, grp2tokens,initiaux,finaux, counters_new = arbo.analyze_new()
    
    assert(set(counters_old.keys())==set(counters_new.keys()))
    for k in counters_old.keys():
        cnt_new = counters_new[k]
        cnt_old = counters_old[k]
        assert cnt_new.bitmask == cnt_old[-1]
        assert cnt_new.start_counter == cnt_old[-3]
        assert cnt_new.end_counter == cnt_old[-2]
    # MAP token_state (1,2,3,6) TO token count for this state

    # token_count_by_état = {counters_new[k].bitmask:len([t for t in counters_new if counters_new[t].bitmask==counters_new[k].bitmask]) for k in counters_new}
    
    # 
    token2group = {t:g for g in grp2tokens for t in grp2tokens[g]}
    
    value2groups = ((v,[token2group[t] for t in arbo.tokenizer(v)]) for v in arbo.values)
    collisions = {value:states for value,states in value2groups if not len(set(states))==len(states)}

    # plusieurs tokens à la meme position, impossible. Repartitionner
    while not len(collisions) == 0:
        value, grps = collisions.popitem()
        fault_grps = set([g for g in grps if grps.count(g)>1])
        if len(fault_grps)==1:
            #il faut isoler les tokens de value, donc len(tokens(value))-1 nouveaux groupes
            #NOTE on en garde un dans le groupe d'origine, ici le premier qui vient
            for i,tok in enumerate(arbo.tokenizer(value)):
                if i==0:
                    continue
                # new_groups.append([tok])
                if token2group[tok] in fault_grps:
                    #créer un nouveau groupe
                    new_group_id = max(grp2tokens.keys())+1
                    grp2tokens[new_group_id] = []
                    grp2tokens[token2group[tok]].remove(tok)
                    grp2tokens[new_group_id].append(tok)
                    token2group[tok] = new_group_id

        token2group = {t:g for g in grp2tokens for t in grp2tokens[g]}
        value2groups = ((v,[token2group[t] for t in arbo.tokenizer(v)]) for v in arbo.values)
        collisions = {value:states for value,states in value2groups if not len(set(states))==len(states)}
        pass
    if len(collisions) == 0:
        print("woohoo!")

    for grp in grp2tokens:
        print(f"grp {grp} : {len(grp2tokens[grp])} tokens {(len(grp2tokens[grp])+1).bit_length()} bits")
        print(f"{grp2tokens[grp]}")
        pass

    for val in arbo.values:
        val_compress:list[int] = [0]*len(grp2tokens)
        tokens = arbo.tokenizer(val)
        for tok in tokens:
            grp = token2group[tok]
            #TODO il faudrait que grp2tokens soit un simple tableau indexable
            # val_compress[grp-1] = grp2tokens[grp].index(tok)+1
    

    #NOTE la suite est bonne à jeter haha

    #NOTE ça vient surement de par là
    #NOTE voir aussi bits_to_token et token_to_bits 
    def repartis_tokens3(grp2tokens):
        ret = {}
        for val in arbo.values:
            tokens = val.split('-')
            current = [0]*len(grp2tokens)
            i = 0
            for j,o in enumerate(sorted(grp2tokens.keys())):
                state = grp2tokens[o]
                if tokens[i] in state:
                    assert current[j]==0
                    current[j] = state.index(tokens[i])+1
                    # current.append(state.index(h[i])+1)
                    i+=1
                    # break
                else:
                    pass
                    # current.append(0)
                    # break
                if i==len(tokens):
                    break
            # while len(current)<len(token_by_état):
            #     current.append(0)
            ret[val] = current
        assert len(set([len(n) for n in ret.values()]))==1
        return ret

    def testo3_suite(results):
        # calc = [set()]*len(results[results.keys()[0]])
        calc = [set() for _ in range(len(results[list(results.keys())[0]]))]
        for v,code in results.items():
            for i,c in enumerate(code):
                calc[i].add(c)
        # for each token position, the count of distinct possible tokens
        #NOTE pourquoi -1?
        tokens_count = [len(c)-1 for c in calc]
        bit_fields_lengths = [c.bit_length() for c in tokens_count]
        #NOTE minus one for the zero value
        remaining_codes = [2**b_f_l - tc - 1 for tc,b_f_l in zip(tokens_count, bit_fields_lengths)]
        return tokens_count, bit_fields_lengths, remaining_codes

    result = repartis_tokens3(grp2tokens)


    tokens_count, bit_fields_lengths, remaining_codes = testo3_suite(result)
    
    tzs = token_to_bits(result['var-typo'], bit_fields_lengths)
    ret = bits_to_token(tzs, bit_fields_lengths)
    ##########################################################################################################
    #TOUT EST Là !
    #################
    for nat in values_set:
        print(f"{nat} : {result[nat]}  -> {token_to_bits(result[nat], bit_fields_lengths)} -> {bits_to_token(token_to_bits(result[nat], bit_fields_lengths), bit_fields_lengths)}")
        assert bits_to_token(token_to_bits(result[nat], bit_fields_lengths), bit_fields_lengths) == result[nat]
    ##########################################################################################################
    
    codés={token_to_bits(result[nat], bit_fields_lengths):nat for nat in values_set}
    print(f"coded token max length : {max(codés.keys()).bit_length()}")
    pprint(tokens_count)
    pprint(bit_fields_lengths)
    pprint(remaining_codes)
    ##########################################################################################################
    #TOUT EST Là !
    #################
    for nat in values_set:
        print(f"{nat} : {result[nat]}  -> {token_to_bits(result[nat], bit_fields_lengths)} -> {bits_to_token(token_to_bits(result[nat], bit_fields_lengths), bit_fields_lengths)}")
        assert bits_to_token(token_to_bits(result3[nat], bit_fields_lengths), bit_fields_lengths) == result3[nat]

    return
    collisioned_tokens = set(*[arbo.tokenizer(value) for value in collisions.keys()])
    value2collisioned_tokens = {}
    state2collisioned_tokens = {}
    for val,grps in collisions.items():
        d = {s:[] for s in grps}
        # for t,s in zip(val.split("-"), states):
        for tok,grp in zip(arbo.tokenizer(val), grps):
            d[grp].append(tok)
        dprime = {state:[tok] for tok,state in zip(arbo.tokenizer(val), grps)}
        print("#################################")
        pprint(d)
        print("**********************************")
        pprint(dprime)
        print("#################################")
        assert d==dprime
        #filter only states/tokens with collisions
        value2collisioned_tokens[val] = {k:v for k,v in d.items() if len(v)>1}
        for grp,tokens in value2collisioned_tokens[val].items():
            state2collisioned_tokens[grp]=set(tokens)
        collisions_by_token = {}
        for v,collisions in value2collisioned_tokens.items():
            for grp, tokens in collisions.items():
                for tok in tokens:
                    if not tok in collisions_by_token:
                        collisions_by_token[tok] = 1
                    else:
                        collisions_by_token[tok] += 1
        i=0
        while not len(collisions_by_token)==0:
            pass 
    tokens_categ = []
    if len(collisions) == 0:
        tokens_categ = [v for k,v, in grp2tokens.items()]
    else:
        pass

    for val, coll in value2collisioned_tokens.items():
        pass
        
    # collisioned_tokens.update()
    # for value,states in collisions.items():
    #     for t in arbo.tokenizer(value):
    #         collisioned_tokens.add(t)

    #NAZE
    state_bitlength = {e:len(bin(token_count_by_état[e]))-2 for e in token_count_by_état}
    

    #ça c'est bon
    #TODO comment déterminer l'ordre ?
    def repartis_tokens(token_by_état, ordre):
        ret = {}
        for nature in arbo.values:
            h = nature.split('-')
            current = []
            i = 0
            for j,o in enumerate(ordre):
                state = token_by_état[o]
                if h[i] in state:
                    current.append(state.index(h[i])+1)
                    i+=1
                    # break
                else:
                    current.append(0)
                    # break
                if i==len(h):
                    break
            while len(current)<len(ordre):
                current.append(0)
            ret[nature] = current
        assert len(set([len(n) for n in ret.values()]))==1
        return ret

    #NOTE repartis_tokens2 ne fonctionne pas correctement
    #NOTE il semble que l'ordre est bel et bien important
    def repartis_tokens2(token_by_état):
        ret = {}
        for nature in arbo.values:
            h = nature.split('-')
            current = []
            i = 0
            for j,o in enumerate(token_by_état.keys()):
                state = token_by_état[o]
                if h[i] in state:
                    current.append(state.index(h[i])+1)
                    i+=1
                    # break
                else:
                    current.append(0)
                    # break
                if i==len(h):
                    break
            while len(current)<len(token_by_état):
                current.append(0)
            ret[nature] = current
        assert len(set([len(n) for n in ret.values()]))==1
        return ret
    
    def repartis_tokens3(token_by_état):
        ret = {}
        for nature in arbo.values:
            h = nature.split('-')
            current = [0]*len(token_by_état)
            i = 0
            for j,o in enumerate(sorted(token_by_état.keys())):
                state = token_by_état[o]
                if h[i] in state:
                    current[j] = state.index(h[i])+1
                    # current.append(state.index(h[i])+1)
                    i+=1
                    # break
                else:
                    pass
                    # current.append(0)
                    # break
                if i==len(h):
                    break
            # while len(current)<len(token_by_état):
            #     current.append(0)
            ret[nature] = current
        assert len(set([len(n) for n in ret.values()]))==1
        return ret

    def testo3_suite(results):
        # calc = [set()]*len(results[results.keys()[0]])
        calc = [set() for _ in range(len(results[list(results.keys())[0]]))]
        for v,code in results.items():
            for i,c in enumerate(code):
                calc[i].add(c)
        # for each token position, the count of distinct possible tokens
        #NOTE pourquoi -1?
        tokens_count = [len(c)-1 for c in calc]
        bit_fields_lengths = [c.bit_length() for c in tokens_count]
        #NOTE minus one for the zero value
        remaining_codes = [2**b_f_l - tc - 1 for tc,b_f_l in zip(tokens_count, bit_fields_lengths)]
        return tokens_count, bit_fields_lengths, remaining_codes

    def testo3_suite_mieux(results):
        # calc = [set()]*len(results[results.keys()[0]])
        calc = {k:set() for k in results.keys()}
        for v,code in results.items():
            for i,c in enumerate(code):
                calc[i].add(c)
        # for each token position, the count of distinct possible tokens
        tokens_count = [len(c)-1 for c in calc]
        bit_fields_lengths = [c.bit_length() for c in tokens_count]
        #NOTE minus one for the zero value
        remaining_codes = [2**b_f_l - tc - 1 for tc,b_f_l in zip(tokens_count, bit_fields_lengths)]
        return tokens_count, bit_fields_lengths, remaining_codes

    
    

    #NOTE comment déterminer cet ordre ?
    ordre_états = [1,3,2,6]
    result2 = repartis_tokens(grp2tokens, [6,3,2,1])
    autre_result = repartis_tokens2(grp2tokens)
    result3 = repartis_tokens3(grp2tokens)
    result = result3
    

    
    pprint("**************")
    pprint(result)
    pprint("**********************")
    pprint(result2)
    def token_state(token):
        for s,tokens in grp2tokens.items():
            if token in tokens:
                return s
        raise Exception(f"token not found {token}")
            
    # code = "-".join([str(token_state(tok)) for tok in arbo.tokenizer(nat) ])
    valid_paths = set("-".join([str(token_state(tok)) for tok in arbo.tokenizer(nat) ]) for nat in values_set)
    pprint(valid_paths)
    
    pprint(result)
    
    tokens_count, bit_fields_lengths, remaining_codes = testo3_suite(result)
    
    tzs = token_to_bits(result['var-typo'], bit_fields_lengths)
    ret = bits_to_token(tzs, bit_fields_lengths)
    ##########################################################################################################
    #TOUT EST Là !
    #################
    for nat in values_set:
        print(f"{nat} : {result[nat]}  -> {token_to_bits(result[nat], bit_fields_lengths)} -> {bits_to_token(token_to_bits(result[nat], bit_fields_lengths), bit_fields_lengths)}")
        assert bits_to_token(token_to_bits(result3[nat], bit_fields_lengths), bit_fields_lengths) == result3[nat]
    ##########################################################################################################
    
    codés={token_to_bits(result[nat], bit_fields_lengths):nat for nat in values_set}
    print(f"coded token max length : {max(codés.keys()).bit_length()}")
    pprint(tokens_count)
    pprint(bit_fields_lengths)
    pprint(remaining_codes)

test_arbo(natures)



