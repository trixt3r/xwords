import re
import warnings




WIKTIONARY_ZIM = "wiktionary_fr_all_maxi_2024-06"

BASE_URL = f"http://127.0.0.1:8080/viewer#{WIKTIONARY_ZIM}/A/"
BASE_URL=f"http://127.0.0.1:8080/content/{WIKTIONARY_ZIM}/A/"
BASE_VERB_URL = f"http://127.0.0.1:8080/content/{WIKTIONARY_ZIM}/A/Conjugaison%3Afran%C3%A7ais/"

class ExtractException(Exception):
    """Custom exception for extraction errors in kiwix_crawler."""
    pass

def extract_api(text):
    if text.startswith("Prononciation") or text.startswith("\\Prononciation"):
        return "?"
    indices = [i for i, ch in enumerate(text) if ch == "\\"]
    # 'indices' contains each index where '\' appears in text
    # if len(indices) < 2:
    #     raise ExtractException(f"API mal formée dans le texte: {text}")
    if len(indices) > 2:
        warnings.warn(f"Multiple possible pronunciations found in text: {text} defaulting to first one.")
        text = text[indices[0]:indices[1]+1]
    return text.strip("\\").replace(".)",").").replace("ɡ","g")


#NOTE on ne vérifie pas l'auxiliaire
def compare_verb_info(v1, v2):
    if not v1["Part"] == v2["Part"]:
        print(f"différence de participe: {v1['Part']} vs {v2['Part']}")
        return False

    for mode in ["Indicatif", "Subjonctif", "Conditionnel", "Impératif"]:
        for temps in v1[mode]:
            if not temps in v2[mode]:
                print(f"temps {temps} manquant dans v2")
                return False
            d1 = v1[mode][temps]
            d2 = v2[mode][temps]
            if len(d1) != len(d2):
                print(f"différence de longueur pour {mode} {temps}: {len(d1)} vs {len(d2)}")
                return False
            for i in range(len(d1)):
                if d1[i][0] != d2[i][0]:
                    print(f"différence d'orthographe pour {mode} {temps} pronom {i}: {d1[i][0]} vs {d2[i][0]}")
                    return False
                if d1[i][1] != d2[i][1]:
                    print(f"différence d'API pour {mode} {temps} pronom {i}: {d1[i][1]} vs {d2[i][1]}")
                    return False
    return True


def extract_conjug_types(soup):
    # Select all divs where id matches "mb0bt" followed by an integer
    divs = soup.find_all("div", id=re.compile(r"^mb0bt\d+$"))
    # print(f"Found {len(divs)} divs with id matching 'mb0bt' followed by an integer.")
    to_ret=[]
    i=1
    for div in divs:
        a_tag = div.find("a")
        if a_tag:
            if a_tag.text.startswith("Conjugaison "):
                to_ret.append((a_tag.text[12:],i))
            else:
                to_ret.append((a_tag.text,i))
        i += 1
            # print(a_tag.text.strip())
    return to_ret

def extract_verbe_group(soup):
    # TODO on trouvera cette table pour chaque onglet de forme de conjugaison
    tables = soup.find_all("table", class_="wikitable")
    group = None
    conju = None
    for table in tables:
        if table.tbody.tr.th.text.strip() == "Conjugaison en français":
            rows = table.tbody.find_all("tr")
            assert len(rows)==3
            line = rows[2].td.text.strip().lower()
            anchors = rows[2].td.find_all("a")
            for a in anchors:
                t = a.text.strip().lower()
                if t.endswith("groupe"):
                    if not t.find("premier") == -1:
                        group = 1
                    elif not t.find("deuxième") == -1:
                        group = 2
                    elif not t.find("troisième") == -1:
                        group = 3
                    else:
                        raise ExtractException("pas trouvé le groupe du verbe")
                idx1 = line.find("{{")
                idx2 = line.find("}}")
                if idx1>=0 and idx2 >= 0:
                    conju = line[idx1+2:idx2]
                    pass
            # print(line)
    return(group, conju)


def search_gcd(wlist:list):
    ''' Return greatest comon prefix of all words in list'''
    def check_candidat(wlist, candidat):
        for w in wlist:
            if not w.startswith(candidat):
                return False
        return True
    min_len = min([len(w) for w in wlist])
    min_w = list(set([w[:min_len] for w in wlist]))
    while min_len > 0 and len(min_w) > 1:
        min_len -= 1
        min_w = list(set([w[:min_len] for w in wlist]))
    if min_len == 0 or len(min_w) == 0:
        return ""
    return min_w[0]