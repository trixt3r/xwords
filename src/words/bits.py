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