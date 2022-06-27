# from words_tuple import word_info_t


def search_by_lex(gramm, lex):
    ret = []
    if isinstance(lex, str):
        lex = (lex,)
    for k in gramm:
        for w in gramm[k]:
            for le in lex:
                if le in w.lex:
                    ret.append(w)
                    break
    return ret
