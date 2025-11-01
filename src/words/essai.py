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

def test_arbo(values_set):
    arbo = ArboComp()
    for n in values_set:
        arbo.add_tokens(n)

    for n in arbo.values:
        print(n , arbo.comp_tokens(n))

    pprint(arbo.tokens)

    for n in arbo.values:
        print(n , arbo.comp_tokens(n))

    counters_old, token_by_état,initiaux,finaux, counters_new = arbo.analyze_new()
    
    assert(set(counters_old.keys())==set(counters_new.keys()))
    for k in counters_old.keys():
        cnt_new = counters_new[k]
        cnt_old = counters_old[k]
        assert cnt_new.bitmask == cnt_old[-1]
        assert cnt_new.start_counter == cnt_old[-3]
        assert cnt_new.end_counter == cnt_old[-2]
    # MAP token_state (1,2,3,6) TO token count for this state

    # token_count_by_état = {counters_new[k].bitmask:len([t for t in counters_new if counters_new[t].bitmask==counters_new[k].bitmask]) for k in counters_new}
    
    token_to_state = {t:s for s in token_by_état for t in token_by_état[s]}
    value_to_states = {v:[token_to_state[t] for t in arbo.tokenizer(v)] for v in arbo.values}
    
    # plusieurs tokens à la meme position, impossible. Repartitionner
    collisions = {value:states for value,states in value_to_states.items() if not len(set(states))==len(states)}
    collisioned_tokens = set(*[arbo.tokenizer(value) for value in collisions.keys()])
    collisioned_tokens_by_value = {}
    collisioned_tokens_by_state = {}
    for val,states in collisions.items():
        d = {s:[] for s in states}
        # for t,s in zip(val.split("-"), states):
        for t,s in zip(arbo.tokenizer(val), states):
            d[s].append(t)
        #filter only states/tokens with collisions
        collisioned_tokens_by_value[val] = {k:v for k,v in d.items() if len(v)>1}
        for s,tokens in collisioned_tokens_by_value[val].items():
            collisioned_tokens_by_state[s]=set(tokens)
        collisions_by_token = {}
        for v,collisions in collisioned_tokens_by_value.items():
            for s, tokens in collisions.items():
                for t in tokens:
                    if not t in collisions_by_token:
                        collisions_by_token[t] = 1
                    else:
                        collisions_by_token[t] += 1
        i=0
        while not len(collisions_by_token)==0:
            pass 
    tokens_categ = []
    if len(collisions) == 0:
        tokens_categ = [v for k,v, in token_by_état.items()]
    else:
        pass

    for val, coll in collisioned_tokens_by_value.items():
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
        return token_code
    

    #NOTE comment déterminer cet ordre ?
    ordre_états = [1,3,2,6]
    result2 = repartis_tokens(token_by_état, [6,3,2,1])
    autre_result = repartis_tokens2(token_by_état)
    result3 = repartis_tokens3(token_by_état)
    result = result3
    

    
    pprint("**************")
    pprint(result)
    pprint("**********************")
    pprint(result2)
    def token_state(token):
        for s,tokens in token_by_état.items():
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



