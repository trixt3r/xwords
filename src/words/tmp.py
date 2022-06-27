from cw import iter_api_phoneme


def list_sons_mots(mots):
    sons = []
    for y in mots:
        for x in iter_api_phoneme(y.api):
            sons.append(x)
    sons = list(set(sons))
    sons.sort()
    return sons

def disp_sons(sons):
    for s in sons:
        if len(s) == 1:
            print("%s %d" %(s, ord(s[0])))
        else:
            print("%s %s %s %d %d" % (s, s[0], s[1], ord(s[0]), ord(s[1])))
