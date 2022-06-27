import pickle
import time
import os.path
import random
import re


from shutil import copyfile

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet

from words_tuple import word_t, word_info_t, desinences_t, flex_adj
from verb import Verb_info
from cw import binary_search

# extrait les infos du mot w depuis une page wiktionnary
def extract_infos(w, all_champs_lex=[]):
    # TODO prepare w (unicode, espaces, accents)
    page = requests.get("https://fr.wiktionary.org/wiki/%s" % w)
    # page = requests.get("http://192.168.43.125:8181/wiktionary_fr_all_nopic_2020-10/A/%s" % w)
    soup = BeautifulSoup(page.content, "html.parser")
    categram_spans = soup.find_all("span", class_="titredef", id=re.compile('^fr-'))
    infos = []
    regex_nature = re.compile('[1-9]')
    print(1)
    for c in categram_spans:
        print(c.text)
        s = c.find_next("span", class_="API", title="Prononciation API")
        if s is None:
            print('vide')
            return []
        nature = c['id'][3:regex_nature.search(c['id']).span()[0]-1]
        api = s.text[1:-1]
        champs_lex = set([x.text[1:-1] for x in c.find_next("ol").find_all("span", class_="term")])
        antonymes = [x.text for x in [x.find('a') for x in _extract_list_elements(c, "anto")] if x is not None]
        hyponymes = [x.text for x in [x.find('a') for x in _extract_list_elements(c, "hypo")] if x is not None]
        synonymes = [x.text for x in [x.find('a') for x in _extract_list_elements(c, "syno")] if x is not None]
