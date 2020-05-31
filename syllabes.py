# -*- coding: utf-8 -*-
from node import *
from cw import *
import pickle
import time
import random
import os.path


def make_list():
    def tmp_save(found, not_found):
        f = open("data/aoi.dmp", "wb")
        pickle.dump(found, f)
        f.close()
        f = open("data/aoi_not_found.dmp", "wb")
        pickle.dump(not_found, f)
        f.close()
    index = Index("data/dico.dmp", "data/tree.dmp")
    dico = index.dico
    root = index.rootNode
    found = {}
    not_found = []
    cnt = 0
    wlist = []
    for x in dico:
        for w in dico[x]:
            wlist.append(w)
    if os.path.isfile("data/aoi.dmp"):
        f = open("data/aoi.dmp", "rb")
        found = pickle.load(f)
        f.close()
        for k in found:
            wlist.remove(k)
    if os.path.isfile("data/aoi_not_found.dmp"):
        f = open("data/aoi_not_found.dmp", "rb")
        not_found = pickle.load(f)
        f.close()
        for w in not_found:
            wlist.remove(w)

    print("total: %d" % len(wlist))

    for w in wlist:
        phonetics = extract_phonetic(w)
        if len(phonetics) > 0:
            found[w] = phonetics
            pass
        else:
            not_found.append(w)
        cnt += 1
        if cnt % 500 == 0:
            tmp_save(found, not_found)
            print("mot numéro %d : %s" % (cnt, w))
        time.sleep(random.randrange(10000) / 1000)
    tmp_save(found, not_found)



# TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# repasser l'ensemble des mots générés par gramm_todo_verbs
# pour être sûr d'avoir les mots qui s'orthographient comme un
# verbe (conjugué ou non) mais qui n'en sont pas
# exemple: (du) manger
def make_info_list(wlist=[]):
    def tmp_save(found, verbs, not_found, todo_verbs, remains, last_words):
        f = open("data/last_words.dmp", "wb")
        pickle.dump(last_words)
        f.close()
        f = open("data/gramm.dmp", "wb")
        pickle.dump(found, f)
        f.close()
        f = open("data/gramm_verbs.dmp", "wb")
        pickle.dump(verbs, f)
        f.close()
        f = open("data/gramm_not_found.dmp", "wb")
        pickle.dump(not_found, f)
        f.close()
        f = open("data/gramm_todo_verbs.dmp", "wb")
        pickle.dump(todo_verbs, f)
        f.close()
        f = open("data/gramm_remains.dmp", "wb")
        pickle.dump(remains, f)
        f.close()

    found = {}
    verbs = {}
    last_words = []
    not_found = []
    cnt = 0
    remains = []
    remains_clone = []
    todo_verbs = []
    if os.path.isfile("data/gramm_remains.dmp"):
        f = open("data/gramm_remains.dmp", "rb")
        remains = pickle.load(f)
        f.close()
        f = open("data/gramm_remains.dmp", "rb")
        remains_clone = pickle.load(f)
        f.close()
    if os.path.isfile("data/gramm_todo_verbs.dmp"):
        f = open("data/gramm_todo_verbs.dmp", "rb")
        todo_verbs = pickle.load(f)
        f.close()
    if remains == [] and wlist == []:
        f = open('data/big_words_list_336557.dmp', 'rb')
        wlist = pickle.load(f)
        f.close()
    # loading previous words
    if os.path.isfile("data/gramm.dmp"):
        f = open("data/gramm.dmp", "rb")
        found = pickle.load(f)
        f.close()
        if remains == []:
            for k in found:
                if k in wlist:
                    wlist.remove(k)
        print("%d words" % len(found))

    if os.path.isfile("data/gramm_verbs.dmp"):
        f = open("data/gramm_verbs.dmp", "rb")
        verbs = pickle.load(f)
        f.close()
        u = 0
        for k in verbs:
            for w in verbs[k]:
                print("remove verb %s " % w[0])
                u += 1
                if remains == [] and w[0] in wlist:
                    wlist.remove(w[0])
        print("%d form verbs" % u)
    if os.path.isfile("data/gramm_not_found.dmp"):
        f = open("data/gramm_not_found.dmp", "rb")
        not_found = pickle.load(f)
        f.close()
        print("%d words not found" % len(not_found))
        if remains == []:
            for w in not_found:
                if w in wlist:
                    wlist.remove(w)

    if remains == []:
        f = open("data/gramm_remains.dmp", "wb")
        pickle.dump(wlist, f)
        f.close();
    else:
        wlist = remains

    print("total remaining: %d" % len(wlist))
    for w in wlist:
        print("#######################""%s" % w)
        infos = []
        remains_clone.remove(w)
        last_words.append(w)
        try:
            infos = extract_infos(w)
        except :
            print("error : %s" % w)
            pass
        if len(infos) == 0:
            try:
                w = w.lower()
                infos = extract_infos(w)
            except :
                print("error : %s" % w)
                pass
        print(w)
        if len(infos) > 0:
            for i in infos:
                ov = -1
                if not i[0].find('verb') == -1:
                    if not i[2] in verbs:
                        verbs[i[2]] = []
                    verbs[i[2]].append((w, i))
                    if ov == -1:
                        ov = 1
                else:
                    ov = 0
            #here, if ov == 1, current word is only a verb
            #if ov == 0 current word has other gram categ
            if ov == 0:
                found[w] = infos
                print("##################### %d formes" % len(infos))
                for categ in infos:
                    print (categ)
                    if categ.nature.startswith("flex-verb"):
                        infinitif = categ[3]
                        if infinitif not in verbs:
                            print("todo verb: %s" % infinitif)
                            if infinitif not in todo_verbs:
                                todo_verbs.append(infinitif)

        else:
            print("*********not found %s" % w)
            not_found.append(w)
        cnt += 1
        # print(infos)
        # print("################")
        if cnt % 100 == 0:
            tmp_save(found, verbs, not_found, todo_verbs, remains_clone, last_words)
            last_words = []
            print("mot numéro %d : %s" % (cnt, w))
        print("####################")
        time.sleep(random.randrange(3000) / 1000)
    tmp_save(found, verbs, not_found, todo_verbs, remains_clone, last_words)







# creates verbes structure from wikipedia
def make_verb_list(verb_list=None):
    def save(verbs, errors):
        f = open('data/verbes_struct.dmp', 'wb')
        pickle.dump(verbs,f)
        f.close()
        f = open('data/verbes_struct_errors.dmp', 'wb')
        pickle.dump(errors,f)
        f.close()
    errors = []
    if verb_list is None:
        f = open('data/liste_verbes_1979.dmp', "rb")
        verb_list = pickle.load(f)
        f.close()
    verbs = {}
    if os.path.isfile("data/verbes_struct.dmp"):
        f = open("data/verbes_struct.dmp", "rb")
        verbs = pickle.load(f)
        f.close()
        for v in verbs:
            if v in verb_list:
                verb_list.remove(v)

    if os.path.isfile("data/verbes_struct_errors.dmp"):
        f = open("data/verbes_struct_errors.dmp", "rb")
        errors = pickle.load(f)
        f.close()
        for v in errors:
            if v in verb_list:
                verb_list.remove(v)
    c = 0
    for v in verb_list:
        try:
            verbs[v] = extract_verb_info_wiki(v)
        except:
            errors.append(v)
            print("error : %s" % v)
            continue
        print (v)
        c += 1
        if c % 10 == 0:
            save(verbs, errors)
            print("tmp save %d" % c)
        time.sleep(random.randrange(3000) / 1000)
    save(verbs, errors)


def verb_info_all_words(v_i):
    ret = []
    for m in v_i['modes']:
        for t in v_i['modes'][m]:
            for d in v_i['modes'][m][t]:
                ret.append(d)
    ret.append(v_i['participes']['Pr'])
    for p in v_i['participes']['Pa']:
        ret.append(v_i['participes']['Pa'][p])
    ret = list(set(ret))
    ret.sort()
    return ret

def ffff(verbes_struct):
    verbes_list = []
    c = 0
    for v in verbes_struct:
        try:
            verbes_list += verb_info_all_words(verbes_struct[v])
            c += 1
        except:
            pass
    print(c)
    return verbes_list
