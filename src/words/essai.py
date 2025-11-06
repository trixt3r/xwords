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

def create_bitmask(length,offset):
    return ((1 << length) - 1) << offset

def bitmask_for_group(grps2tokens,gid):
    if isinstance(gid,list):
        return(sum(bitmask_for_group(grps2tokens,g) for g in gid))
    return create_bitmask(len(grps2tokens[gid]).bit_length(), sum(len(grps2tokens[g]).bit_length() for g in range(gid)))

def offset_for_group(grps2tokens,gid):
    return sum(len(grps2tokens[g]).bit_length() for g in range(gid))

def word_to_groups(word:str, grp2tokens)->list[int]:
    groups = []
    for gid, tokens in enumerate(grp2tokens):
        if any(tok in word for tok in tokens):
            groups.append(gid)
    return groups

def token_to_bits(token_code, bit_fields_lengths, reverse: bool = True)->int:
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

def bits_to_token(bits:int, bit_fields_lengths, reverse: bool = True)->tuple[int]:
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

class TokEnumBase(IntEnum):
    def __new__(cls, *args):
        # args is typically (value,) or (value, extra)
        value = args[0]
        # extra = args[1] if len(args) > 1 else None
        # create the int-backed enum member
        obj = int.__new__(cls, value)
        obj._value_ = value
        # attach any extra attributes you need
        obj.bitmask = args[1] if len(args) > 1 else 0
        obj.offset = args[2] if len(args) > 2 else 0
        obj.valid_word = args[3] if len(args) > 3 else False
        return obj

    def has_token(self, tok)->bool:
        return self.value & tok.bitmask == tok.value

    @classmethod
    def valid_words(cls):
        for tok in cls:
            if tok.valid_word:
                yield tok

def token_to_grp(tok:str,grp2tokens)->int:
    for gid, tokens in enumerate(grp2tokens):
        if tok in tokens:
            return gid
    raise Exception(f"token not found {tok}")

def word_to_code(tokens:list[str], grp2tokens:list[list[str]])->tuple[int]:
    code = [0]*len(grp2tokens)
    for tok in tokens:
        grp = token_to_grp(tok, grp2tokens)
        code[grp] = grp2tokens[grp].index(tok)+1
    return tuple(code)

def test_arbo(values_set):
    arbo = ArboComp(values_set)
    # for n in values_set:
    #     arbo.add_tokens(n)

    for n in arbo.values:
        print(n , arbo.comp_tokens(n))

    pprint(arbo.tokens)

    
    grp2tokens= arbo.analyze_new()
    
    

    


    bit_fields_lengths = [len(grp).bit_length() for grp in grp2tokens]

    enum_values = {w.replace("-", "_").upper(): (token_to_bits(word_to_code(arbo.tokenizer(w), grp2tokens), bit_fields_lengths), bitmask_for_group(grp2tokens, word_to_groups(w, grp2tokens)), 0, True)
         for w in arbo.values}
    #NOTE add also single-token natures, those are not strictly values, but useful to have as individual tokens, for tests
    enum_values.update({tok.upper(): (token_to_bits(word_to_code(arbo.tokenizer(tok), grp2tokens), bit_fields_lengths), bitmask_for_group(grp2tokens, token_to_grp(tok, grp2tokens)), offset_for_group(grp2tokens, token_to_grp(tok, grp2tokens)), False)  
        for tok in arbo.tokens if tok not in arbo.values})
    
    def word_to_group_path(word):
        return tuple(i for i,x in enumerate(word_to_code(arbo.tokenizer(word),grp2tokens)) if x>0)

    # create NatTok as before
    NatTok = TokEnumBase(
        "NatTok",
        enum_values
        )

    for x in NatTok:
        print(f"{x.name} {x.has_token(NatTok.ADJ)} bitmask:{x.bitmask:b} offset:{x.offset}")


    for n in NatTok:
        assert n.value == token_to_bits(word_to_code(arbo.tokenizer(n.name.replace("_","-").lower()), grp2tokens), bit_fields_lengths)
        # print(f"nature {n} code {get_code(n.name.replace('_','-').lower(), grp2tokens)} bin {bin(n.value)} bits {n.value:0{sum(bit_fields_lengths)}b}")

        for tok in [NatTok.SYMB, NatTok.ADJ, NatTok.VERB, NatTok.FLEX, NatTok.NOM, NatTok.FLEX_ADJ]:
            if tok==NatTok.NOM and "PRONOM" in n.name or "ONOMA" in n.name or "PRÉNOM" in n.name:
                print(f"skip nom/pronom/prénom/onoma test for {n.name} ")
                continue
            if tok.name in n.name:
                assert n.has_token(tok), f"nature {n} {n.name} incorrectly identified as NOT {tok.name} {tok.value}"
            else:
                assert not n.has_token(tok), f"nature {n} {n.name} incorrectly identified as {tok.name} {tok.value}"

    # [(n,word_to_group_path(n.name.replace("_","-").lower())) for n in NatTok]

    return NatTok

natures = {'pronom-rel', 'flex-verb', 'nom', 'flex-art-déf', 'var-typo', 'adj-dém', 'part', 'flex-art-indéf', 'flex-adj-pos', 'adj-indéf', 'prénom', 'nom-pr', 'pronom-pers', 'adj', 'adv', 'verb', 'art-part', 'flex-adj', 'flex-adj-indéf', 'onoma', 'adj-int', 'conj-coord', 'flex-adj-dém', 'adv-int', 'flex-nom', 'interj', 'symb', 'flex-pronom-dém', 'adv-rel', 'suf', 'pronom-dém', 'flex-pronom-rel', 'flex-pronom-pers', 'phr', 'flex-prép', 'lettre', 'adj-num', 'pronom-int', 'prép', 'flex-pronom-int', 'adj-rel', 'adj-pos', 'flex-adv', 'pronom', 'nom-fam', 'pronom-indéf', 'flex-pronom-indéf', 'art-indéf', 'flex-adj-int', 'art-déf', 'conj'}

NatTok = test_arbo(natures)

for tok in NatTok.valid_words():
    print(f"valid word token: {tok.name}")

for tok in NatTok:
    if not tok.valid_word:
        print(f"non-valid word token: {tok.name}")



