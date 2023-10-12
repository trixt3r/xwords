import sys
import os
import socket
# import pickle

from flask import Flask, request, render_template, make_response
# from flask_sqlalchemy import SQLAlchemy
# from urllib.parse import unquote


sys.path.insert(0, '../words')

from words.cw import difference, getCanonicForm, can_write
# from words import ResultSet
from words import client_light


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
    print('woohoo1')
    # reconstituer la liste des mots choisis
    if not mots_choisis == []:
        mots_choisis = mots_choisis.split(",")
        if len(mots_choisis) > 0 and mots_choisis[0] == '':
            mots_choisis = mots_choisis[1:]

    # delete chosen word; usually done in javascript
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
            # tentative de choix d'un mot qu'on ne peut écrire avec
            # les lettres restantes
            error_word = new_word
            reste = difference(getCanonicForm("".join(mots_choisis), keep_accents), getCanonicForm(phrase))
        else:
            # new word chosen
            # usually done in javascript
            mots_choisis.append(new_word)
            # print("reste: %s" % reste)
            # print("cw_new: %s" % cw_new)
            reste = difference(cw_new, reste)
    else:  #  no new word has been chosen
        # security check
        cw_choisis = getCanonicForm("".join(mots_choisis), keep_accents)
        if not can_write(getCanonicForm(phrase, keep_accents), cw_choisis):
            # cookie trafiqué
            # on supprime tous les mots choisis,
            # pour repartir de zéro avec la phrase de départ
            cookie_trafic += 1
            mots_choisis = []
            cw_choisis = ""

        reste = difference(cw_choisis, getCanonicForm(phrase))
        # print("reste:" + reste)
    # liste de tuples:
    # pour chaque mot on associe les lettres restantes
    anagramms = []
    if reste is not None:
        results = client_light.exec_anagramm_request(reste, keep_accents, False)
        for x in results:
            anagramms.append((x,difference(getCanonicForm(x),reste)))
    if phrase is None:
        resp = make_response(render_template('anagrammes.html', display=display))
    else:
        print('########################')
        print(anagramms)
        print('########################')
        resp = make_response(render_template('anagrammes.html', anagramms=anagramms, reste=reste, words=mots_choisis, phrase=phrase, error_word=error_word, display=display))
        set_cookies(resp, phrase, mots_choisis, reste, display, keep_accents)
    return resp


if __name__ == "__main__":
    print('ooooooooooo')
    if len(sys.argv) == 2:
        app.config['server_port'] = sys.argv[1]
    else:
        app.config['server_port'] = "12346"
    app.run()
