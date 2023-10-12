import sys
import os
import socket
# import pickle

from flask import Flask, request, render_template, make_response
# from flask_sqlalchemy import SQLAlchemy
# from urllib.parse import unquote


sys.path.insert(0, '../words')

from words.cw import difference, getCanonicForm, phon_getCanonicForm, can_write
from words import ResultSet
from words import client


# MAXIFLEMME
# template_dir = os.path.abspath('../words/templates')
# app = Flask(__name__, template_folder=template_dir)
app = Flask(__name__)

server_adress = "127.0.0.1"
# print("config port:" % app.config['server_port'])
server_port = 12346
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((server_adress, server_port))
# with open("data/test_index.dmp", "rb") as f:
#     idx = pickle.load(f)

# with open("data/test_phon_index.dmp", "rb") as f:
#     phon_idx = pickle.load(f)
#
# with open("data/gramm.dmp", "rb") as f:
#     gramm = pickle.load(f)


@app.template_test("none")
def is_flex(v: str):
    return v.startswith("flex-")


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
        print("display: *%s*" % display)
        resp.set_cookie("display", display, max_age=90 * 60 * 60 * 24)
    if keep_accents is not None:
        resp.set_cookie("keep_accents", str(keep_accents), max_age=90 * 60 * 60 * 24)


def get_session_values(request):
    phrase = request.args.get("phrase")
    new_word = request.args.get("add")
    remove = request.args.get("remove")
    cookie_trafic = 0
    mots_choisis = default_val(request.cookies.get("words"), [])
    error_word = request.args.get("error_word")
    display = default_val(request.args.get('display'), request.cookies.get('display'))
    keep_accents = bool(default_val(request.args.get('keep_accents'), request.cookies.get('keep_accents')))
    contrepetri = bool(default_val(request.args.get('contrepetri'), request.cookies.get('contrepetri')))
    anagr_mode = bool(default_val(default_val("A",request.args.get('anagr_mode')), request.cookies.get('anagr_mode')))

    if display not in ['list', 'table']:
        if display is not None:
            # cookie trafiqué
            cookie_trafic += 1
            pass
        display = "table"

    if phrase is None:
        phrase = request.cookies.get('phrase')
    else:
        mots_choisis = []

    return (phrase, new_word,  remove, mots_choisis, error_word, display, keep_accents, cookie_trafic, contrepetri, anagr_mode)


@app.route("/")
def index():
    resp = make_response(render_template('index.html'))
    return resp


@app.route("/anagrammes")
def anagrammes():
    global idx
    phrase, new_word,  remove, mots_choisis, error_word, display, keep_accents, cookie_trafic, contrepetri, anagr_mode = get_session_values(request)
    reste = None
    resp = None
    if phrase is None:
        resp = make_response(render_template('anagrammes.html', display=display))
        set_cookies(resp, None, None, None, display, keep_accents)
        return resp

    # reconstituer la liste des mots choisis
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
            # print("reste: %s" % reste)
            # print("cw_new: %s" % cw_new)
            reste = difference(cw_new, reste)
    else:
        cw_choisis = getCanonicForm("".join(mots_choisis), keep_accents)
        if not can_write(getCanonicForm(phrase, keep_accents), cw_choisis):
            # cookie trafiqué
            cookie_trafic += 1
            # print('cw_choisis: ' + cw_choisis)
            # print("phrase: %s" % phrase)
            mots_choisis = []
            cw_choisis = ""

        reste = difference(cw_choisis, getCanonicForm(phrase))
        # print("reste:" + reste)
    # liste de tuples:
    # pour chaque mot on associe les lettres restantes
    results = None
    anagramms = []
    if reste is not None:
        results = client.exec_anagramm_request(reste, keep_accents, False)
        # results = idx.search_anagrammes(reste, keep_accents)
        # nice hack but problem has to be solved
        unique = []
        for w in results.items:
            if (w.mot, w.nature) not in unique:
                unique.append((w.mot, w.nature))
                try:
                    anagramms.append((w, difference(getCanonicForm(w.mot, keep_accents), reste)))
                except Exception as e:
                    print("keep_accents: " + str(keep_accents))
                    print("w:")
                    print(w)
                    print("reste: %s" % reste)
                    raise e
                    pass
    if phrase is None:
        resp = make_response(render_template('anagrammes.html', display=display))
    else:
        # print('########################')
        # print(anagramms)
        # print('########################')
        resp = make_response(render_template('anagrammes.html', natures=list(set([w.nature for w in results.items])), anagramms=anagramms, reste=reste, words=mots_choisis, phrase=phrase, error_word=error_word, display=display))
        set_cookies(resp, phrase, mots_choisis, reste, display, keep_accents)
    return resp


@app.route('/contrepeteries')
def contrepeteries():
    global phon_idx
    phrase, new_word, remove, mots_choisis, error_word, display, keep_accents, cookie_trafic, contrepetri,mode = get_session_values(request)
    #todo: nice hack but...
    display="table"
    print("##phrase= %s"%phrase)
    if phrase is None:
        resp = make_response(render_template('contrepetri.html', display=display))
        set_cookies(resp, None, None, None, display, keep_accents)
        return resp
    request_resp = client.exec_request(phrase, 1, keep_accents)
    _found = []
    ambigus = []
    not_found = []
    if isinstance(request_resp, tuple):
        _found = request_resp[0]
        not_found = request_resp[1]
        ambigus = request_resp[2]
    else:
        _found = [x for x in request_resp.items]
    print("##################$$$$$$$$$$$$$$$$$$$$")
    print(_found)
    print("#$")
    lemmes = []
    request_canon = phon_getCanonicForm(request_resp.request)
    for w in _found:
        print("***************")
        print(w)
        print(w.api)
        print(request_resp)
        print("###############")
        lemmes.append((w, difference(phon_getCanonicForm(w.api), request_canon)))
    # _found, ambigus, not_found = scan_sentence_for_api(phrase, gramm)
    reste = phon_getCanonicForm(request_resp.request)
    print("2 reste:")
    print(reste)
    print("found: ")
    print(_found)
    print("ambigüs: ")
    print(ambigus)
    print('not found:')
    print(not_found)
    print('reste:')
    print(reste)
    print('########################')
    print(_found)
    print('########################')
    resp = make_response(render_template('contrepetri.html', lemmes=lemmes, reste="".join(reste), mode="phon", ambiguous=ambigus, unknown=not_found, display=display))
    set_cookies(resp, None, None, None, display, keep_accents)
    return resp
    return None


if __name__ == "__main__":
    print('ooooooooooo')
    if len(sys.argv) == 2:
        app.config['server_port'] = sys.argv[1]
    else:
        app.config['server_port'] = "12346"
    app.run()
