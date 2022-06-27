from dico import iter_api_phoneme


def scan_gramm_for_sound(gramm, sound):
    l1 = []
    l2 = []
    for k in gramm:
        for w in gramm[k]:
            if sound in w.api:
                l1.append(w)
            if sound in [x for x in iter_api_phoneme(w.api)]:
                l2.append(w)
    return (l1, l2)
    pass
