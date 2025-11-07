from scrapping import *

phrase = "Il est important de bien comprendre le fonctionnement des verbes transitifs et intransitifs en français."

mot_en = new_master_scrapper("en")
print(mot_en)

mot_est = new_master_scrapper("est")
print(mot_est)

mot_dans = new_master_scrapper("dans")
print(mot_dans)


mot_de = new_master_scrapper("de")
print(mot_de)

def process_phrase(phrase: str):
    tokened_phrase = []
    for word in phrase.strip().split():
        word = word.lower()
        try:
            result = new_master_scrapper(word)
            tokened_phrase.append([(word, r, 1/len(result)) for r in result])
            # if len(result)==1:
            #     result = result[0]
            # if len(result) == 1:
            #     # translate with a single result
            #     tokened_phrase.append([(mot, r, 1) for r in result])
            # else:
            #     tokened_phrase.append([(mot, r, 1/len(result)) for r in result])
        except Exception as e:
            print(f"Erreur lors de l'extraction pour {word}: {e}")
            tokened_phrase.append([(word, None, 1)])
    return tokened_phrase

p=process_phrase(phrase)
print ([len(w) for w in p])