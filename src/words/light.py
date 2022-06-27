import unidecode
# this module probably not used

class Node(object):
    def __init__(self, cw="", data=[]):
        self.cw = cw
        self.data = []
        self.children = {}

    def child(self, w):
        if w not in self.children:
            return None
        return self.children[w]

    def addWord(self, cw, data=None):
        f = self.search(cw)
        n = f._addWord(cw[len(f.cw):])
        n.data.append(data)
        return n

    def _addWord(self, cw):
        """Create nodes recursively"""
        if cw == '':
            return self
        if not cw[0] in self.children:
            self.children[cw[0]] = Node(self.cw+cw[0])
        return self.children[cw[0]]._addWord(cw[1:])

    def search(self, cw):
        """Search for cw from this node
        Return False if cw can't write a word from here, else return the
        cw node"""
        if len(cw) == 0:
            return self
        if not cw[0] in self.children:
            return self
        return self.children[cw[0]].search(cw[1:])

    def __repr__(self):
        if self.data is not None:
            return "<%s %d %d>" % (self.cw, len(self.data), len(self.children))
        return "<%s %d %d>" % (self.cw, 0, len(self.children))


class Index_Light:
    def __init__(self):
        self.root_node = Node()

    def addWord(self, word):
        cw = getCanonicForm(word)
        node = self.root_node.addWord(cw, word)
        return node

    def search(self, w):
        cw = getCanonicForm(w)
        node = self.root_node.search(cw)
        if node.cw == cw:
            return node
        return None

    def search_anagramms(self, word, keep_accents=False):
        fifo = [(self.root_node, getCanonicForm(word))]
        # list of Node
        ret = set()
        while len(fifo) > 0:
            s = fifo.pop()
            cn = s[0]
            cw = s[1]
            # if len(cn.data) > 0:
                # ret.add(cn)
            for i in range(0, len(cw)):
                if i > 0 and cw[i-1] == cw[i]:
                    continue
                child = cn.child(cw[i])
                to_find = cw[:i] + cw[i+1:]
                if child is not None:
                    if len(to_find) > 0:
                        fifo.append((child, to_find))
                    if len(child.data) > 0:
                        ret.add(child)
        # list of words as str
        words = []
        for n in ret:
            words += n.data
        if keep_accents:
            cw = getCanonicForm(word, True)
            return [w for w in words if can_write(cw, getCanonicForm(w, True))]
        return words


#########################################
# helpers
#########################################

def can_write(cw1, cw2):
    """Return true if all characters of cw2 are in cw1"""
    i = 0
    i_max = len(cw1)
    founds = 0
    for c in cw2:
        found = False
        while i < i_max:
            if cw1[i] == c:
                found = True
                founds += 1
                # print "found " + c
                break
            else:
                i += 1
        if founds == len(cw2):
            return True
        if not found:
            return False
        else:
            i += 1
        if i >= i_max:
            return False
    return True


def getCanonicForm(word, keep_accents=False):
    """Return canonical version of word"""

    def sanitize_word(word, keep_accents=False):
        word = word.lower()
        if not keep_accents:
            word = unidecode.unidecode(word)
        word = word.replace(" ", "")
        word = word.replace("\t", "")
        word = word.replace("\n", "")
        word = word.replace("-", "")
        return word

    word = sanitize_word(word, keep_accents)
    s1 = {}
    for c in word:
        if c in s1:
            s1[c] = s1[c] + 1
        else:
            s1[c] = 1
    ret_string = ""
    keys = list(s1.keys())
    keys.sort()
    for c in keys:
        ret_string += (c * s1[c])
    return ret_string


def list_utf_file(fname):
    wl = []
    with open(fname) as f:
        for l in f.readlines():
            wl.append(l[:-1])
    return wl


def difference(cw1, cw2):
    """Return cw2 - cw1"""
    i = 0
    result = ""
    if cw1 == '':
        return cw2
    for c in cw1:
        while not cw2[i] == c:
            result += cw2[i]
            i += 1
            if i >= len(cw2):
                break
        i += 1
    while i < len(cw2):
        result += cw2[i]
        i += 1
    return result


#########################################
# test
#########################################

def simple_test():
    def test_index_search(idx, word):
        print("search '%s' word:" % word)
        print(idx.search(word))

    def test_anagramm_search(idx, word, keep_accents=False):
        print("search '%s' anagramms(keep_accents=%s):" % (word, keep_accents))
        print(idx.search_anagramms(word, keep_accents))
    words = ["mare", "maré", 'mari', 'marie', 'ami', 'marié', "mariée", "mat", 'rame', 'rami']
    idx = Index_Light()
    for w in words:
        idx.addWord(w)
    test_index_search(idx, "rami")
    test_anagramm_search(idx, "marie", False)
    test_anagramm_search(idx, "marie", True)
    test_anagramm_search(idx, "marié", True)
    return idx

#########################################
# flask
#########################################

from flask import Flask, request, render_template, make_response
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import unquote
import pickle

#MAXIFLEMME
app = Flask(__name__)
f = open("data/small_index.dmp", "rb")
idx = None
idx = pickle.load(f)
f.close()

@app.route('/anagrammes/')
def anagrammes():
    def default_val(val, default):
        if val is None:
            return default
        return val

    def set_cookies(resp, phrase, mots_choisis, reste, display="list", keep_accents="False"):
        if phrase is not None:
            resp.set_cookie("phrase", phrase)
        if mots_choisis is not None:
            resp.set_cookie('words', ','.join(mots_choisis))
        if reste is not None:
            resp.set_cookie("reste", reste)
        if display is not None:
            resp.set_cookie("display", display, max_age=90 * 60 * 60 * 24)
        if keep_accents is not None:
            resp.set_cookie("keep_accents", str(keep_accents), max_age=90 * 60 * 60 * 24)

    global idx
    phrase = request.args.get("phrase")
    new_word = request.args.get("add")
    remove = request.args.get("remove")
    mots_choisis = default_val(request.cookies.get("words"), [])
    error_word = request.args.get("error_word")
    display = default_val(request.args.get('display'), request.cookies.get('display'))
    keep_accents = default_val(request.args.get('keep_accents'), request.cookies.get('keep_accents'))
    reste = None
    resp = None
    cookie_trafic = 0

    if keep_accents == "True":
        keep_accents = True
    elif keep_accents == 'False':
        keep_accents = False
    else:
        # cookie trafiqué
        cookie_trafic += 1
        pass
    if display not in ['list', 'table']:
        if display is not None:
            # cookie trafiqué
            cookie_trafic += 1
            pass
        display = "list"

    if phrase is None:
        phrase = request.cookies.get('phrase')
    else:
        # nouvelle phrase
        mots_choisis = []

    if phrase is None:
        resp = make_response(render_template('anagrammes.html', display=display))
        set_cookies(resp, None, None, None, display, keep_accents)
        return resp

    if not mots_choisis == []:
        mots_choisis = mots_choisis.split(",")
        if len(mots_choisis) > 0 and mots_choisis[0] == '':
            mots_choisis = mots_choisis[1:]
    if remove is not None:
        try:
            widx = mots_choisis.index(remove)
            del mots_choisis[widx]
        except ValueError:

            pass

    if new_word is not None:
        reste = difference(getCanonicForm("".join(mots_choisis), keep_accents), getCanonicForm(phrase))
        cw_new = getCanonicForm(new_word, keep_accents)
        if not can_write(reste, cw_new):
            error_word = new_word
            reste = difference(getCanonicForm("".join(mots_choisis), keep_accents), getCanonicForm(phrase))
        else:
            mots_choisis.append(new_word)
            print("reste: %s" % reste)
            print("cw_new: %s" % cw_new)
            reste = difference(cw_new, reste)
    else:
        cw_choisis = getCanonicForm("".join(mots_choisis), keep_accents)
        if not can_write(getCanonicForm(phrase, keep_accents), cw_choisis):
            #cookie trafiqué
            cookie_trafic += 1
            print('cw_choisis: ' + cw_choisis)
            print("phrase: %s" % phrase)
            mots_choisis = []
            cw_choisis = ""

        reste = difference(cw_choisis, getCanonicForm(phrase))
        print("reste:" + reste)
    # liste de tuples:
    # pour chaque mot on associe les lettres restantes
    results = None
    anagramms = []
    if reste is not None:
        results = idx.search_anagramms(reste, keep_accents)
        results.sort()
        for w in results:
            anagramms.append((w, difference(getCanonicForm(w, keep_accents), reste)))

    if phrase is None:
        resp = make_response(render_template('anagrammes.html', display=display))
    else:
        resp = make_response(render_template('anagrammes.html', anagramms=anagramms, reste=reste, words=mots_choisis, phrase=phrase, error_word=error_word, display=display))
        set_cookies(resp, phrase, mots_choisis, reste, display, keep_accents)
    return resp
