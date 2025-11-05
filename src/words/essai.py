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
    # return ((1 << length) - 1) >> offset

def bitmask_for_group(grps2tokens,gid):
    
    return bitmask(len(grps2tokens[gid]).bit_length(), sum(len(grps2tokens[g]).bit_length() for g in range(gid)))
    
    # return bitmask(len(grps2tokens[gid]).bit_length(), sum(len(grps2tokens[g]).bit_length() for g in range(gid)))
    bit_fields_lengths = [len(grp).bit_length() for grp in grps2tokens]
    total_bits = sum(bit_fields_lengths)
    mask = (1 << total_bits) - 1
    return mask

def offset_for_group(grps2tokens,gid):
    return sum(len(grps2tokens[g]).bit_length() for g in range(gid))

def token_to_bits(token_code, bit_fields_lengths, reverse: bool = True):
    """
    Pack a tuple of integer codes into a single integer according to the provided
    bit field lengths.

    If reverse is False (default) the last element of token_code is placed in the
    least-significant bits (existing behavior). If reverse is True the first
    element of token_code is placed in the least-significant bits (mirrored packing).
    """
    bits = 0
    shift = 0
    if not reverse:
        seq = zip(reversed(token_code), reversed(bit_fields_lengths))
    else:
        seq = zip(token_code, bit_fields_lengths)
    for code, b_f_l in seq:
        bits |= (code << shift)
        shift += b_f_l
    return bits

def bits_to_token(bits, bit_fields_lengths, reverse: bool = True):
    """
    Unpack an integer into a tuple of integer codes according to the bit field lengths.

    If reverse is False (default) it decodes assuming the last token_code element
    was packed into the least-significant bits (existing behavior). If reverse is True
    it decodes assuming the first token_code element was packed into the least-significant bits.
    """
    token_code = []
    if not reverse:
        shift = sum(bit_fields_lengths)
        for b_f_l in bit_fields_lengths:
            shift -= b_f_l
            mask = (1 << b_f_l) - 1
            code = (bits >> shift) & mask
            token_code.append(code)
    else:
        shift = 0
        for b_f_l in bit_fields_lengths:
            mask = (1 << b_f_l) - 1
            code = (bits >> shift) & mask
            token_code.append(code)
            shift += b_f_l
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

    
    def token_to_grp(tok:str,grp2tokens)->int:
        for gid, tokens in enumerate(grp2tokens):
            if tok in tokens:
                return gid
        raise Exception(f"token not found {tok}")
    
    def word_to_code(word:str, grp2tokens:list[list[str]])->tuple[int]:
        code = [0]*len(grp2tokens)
        for tok in arbo.tokenizer(word):
            grp = token_to_grp(tok, grp2tokens)
            code[grp] = grp2tokens[grp].index(tok)+1
        return tuple(code)

    bit_fields_lengths = [len(grp).bit_length() for grp in grp2tokens]

    enum_values = {w.replace("-", "_").upper(): (token_to_bits(word_to_code(w, grp2tokens), bit_fields_lengths), 0, 0)
         for w in arbo.values}
    enum_values.update({tok.upper(): (token_to_bits(word_to_code(tok, grp2tokens), bit_fields_lengths), bitmask_for_group(grp2tokens, token_to_grp(tok, grp2tokens)), offset_for_group(grp2tokens, token_to_grp(tok, grp2tokens)))  
        for tok in arbo.tokens})
    # create NatTok as before
    
    class NatTokBase(IntEnum):
        def __new__(cls, *args):
            # args is typically (value,) or (value, extra)
            value = args[0]
            # extra = args[1] if len(args) > 1 else None

            # create the int-backed enum member
            obj = int.__new__(cls, value)
            obj._value_ = value
            # attach any extra attributes you need
            obj.bitmask = args[1]
            obj.offset = args[2]

            return obj

        def __init__(self, *args,**kwargs):
            print(f"init NatTokBase {args} {kwargs.keys()}")
            super().__init__(*args,**kwargs)

        def is_a_tok(self, tok)->bool:
            return self.value & tok.bitmask == tok.value
    

    NatTok = NatTokBase(
        "NatTok",
        enum_values)
    for x in NatTok:
        print(f"{x.name} {x.is_a_tok(NatTok.ADJ)} bitmask:{x.bitmask:b} offset:{x.offset}")
    NatTok.bit_fields_lengths = bit_fields_lengths
    # add extra fields to each member
    for nat in NatTok:
        nat.name_str = nat.name.replace("_","-").lower()                     # original token name
        # nat.code = word_to_code(nat.name_str, grp2tokens)                 # tuple code
        if len(nat.name_str.split("-")) == 1:
            grp = token_to_grp(nat.name_str, grp2tokens)
            # nat.group = my_token_to_grp(nat.name_str, grp2tokens)  # group id
            nat.bitmask = bitmask_for_group(grp2tokens, grp)
            nat.offset = offset_for_group(grp2tokens, grp)
        # nat.tokens = grp2tokens[ my_token_to_grp(nat.name, grp2tokens) ]  # token list for this group
        # nat.is_adj = ("adj" in nat.name)                             # any flag you want
    
    bitmask_for_group(grp2tokens,token_to_grp("adj",grp2tokens))
    
    def is_nom(nature:NatTok)->bool:
        return nature.is_a_tok(NatTok.NOM)
        return nature.value & NatTok.NOM.bitmask == NatTok.NOM.value
        return nature.value & bitmask_for_group(grp2tokens,NatTok.NOM.group) == NatTok.NOM.value
    
    def is_verb(nature:NatTok)->bool:
        return nature.is_a_tok(NatTok.VERB)
        return nature.value & NatTok.VERB.bitmask == NatTok.VERB.value
        return nature.value & bitmask_for_group(grp2tokens,NatTok.VERB.group) == NatTok.VERB.value


    def is_adj(nature:NatTok)->bool:
        return nature.is_a_tok(NatTok.ADJ)
        return nature.value & NatTok.ADJ.bitmask == NatTok.ADJ.value
        return nature.value & bitmask_for_group(grp2tokens,NatTok.ADJ.group) == NatTok.ADJ.value


    def is_symb(nature:NatTok)->bool:
        return nature.is_a_tok(NatTok.SYMB)
        return nature.value & NatTok.SYMB.bitmask == NatTok.SYMB.value
        return nature.value & bitmask_for_group(grp2tokens,NatTok.SYMB.group) == NatTok.SYMB.value
        # return nature.value & NatTok.ADJ.value == NatTok.ADJ.value
    
    def is_flex(nature:NatTok)->bool:
        return nature.is_a_tok(NatTok.FLEX)
        return nature.value & NatTok.FLEX.bitmask == NatTok.FLEX.value

    for n in NatTok:
        assert n.value == token_to_bits(word_to_code(n.name.replace("_","-").lower(), grp2tokens), bit_fields_lengths)
        # print(f"nature {n} code {get_code(n.name.replace('_','-').lower(), grp2tokens)} bin {bin(n.value)} bits {n.value:0{sum(bit_fields_lengths)}b}")
        is_symb(n)
        for tok, is_tok_func in [(NatTok.SYMB,is_symb), (NatTok.ADJ, is_adj), (NatTok.VERB, is_verb), (NatTok.FLEX, is_flex), (NatTok.NOM, is_nom)]:
            if tok==NatTok.NOM and "PRONOM" in n.name or "ONOMA" in n.name or "PRÉNOM" in n.name:
                print(f"skip nom/pronom/prénom/onoma test for {n} ")
                continue
            if tok.name in n.name:
                assert n.is_a_tok(tok), f"nature {n} {n.name} incorrectly identified as NOT {tok.name} {tok.value}"
                assert is_tok_func(n), f"nature {n} {n.name} incorrectly identified as NOT {tok.name} {tok.value}"
            else:
                assert not n.is_a_tok(tok), f"nature {n} {n.name} incorrectly identified as {tok.name} {tok.value}"
                assert not is_tok_func(n), f"nature {n} {n.name} incorrectly identified as {tok.name} {tok.value}"
        
    return NatTok

natures = {'pronom-rel', 'flex-verb', 'nom', 'flex-art-déf', 'var-typo', 'adj-dém', 'part', 'flex-art-indéf', 'flex-adj-pos', 'adj-indéf', 'prénom', 'nom-pr', 'pronom-pers', 'adj', 'adv', 'verb', 'art-part', 'flex-adj', 'flex-adj-indéf', 'onoma', 'adj-int', 'conj-coord', 'flex-adj-dém', 'adv-int', 'flex-nom', 'interj', 'symb', 'flex-pronom-dém', 'adv-rel', 'suf', 'pronom-dém', 'flex-pronom-rel', 'flex-pronom-pers', 'phr', 'flex-prép', 'lettre', 'adj-num', 'pronom-int', 'prép', 'flex-pronom-int', 'adj-rel', 'adj-pos', 'flex-adv', 'pronom', 'nom-fam', 'pronom-indéf', 'flex-pronom-indéf', 'art-indéf', 'flex-adj-int', 'art-déf', 'conj'}

NatTok = test_arbo(natures)



