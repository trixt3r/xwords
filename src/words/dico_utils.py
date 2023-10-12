import codecs
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


def convert_file_utf(fname):
    BLOCKSIZE = 1048576 # or some other, desired size in bytes
    with codecs.open(fname, "r", "UTF-8") as sourceFile:
        with codecs.open(fname+".out", "w", "utf-8") as targetFile:
            while True:
                contents = sourceFile.read(BLOCKSIZE)
                if not contents:
                    break
                targetFile.write(contents)


def list_utf_file(fname, enc="UTF-8"):
    wl = []
    with open(fname, encoding=enc) as f:
        for l in f.readlines():
            wl.append(l[:-1])
    return wl