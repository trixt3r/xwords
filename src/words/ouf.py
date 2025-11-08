from scrapping import *



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

base = ["je", "pas"]
phrase = "Il est important de bien comprendre le fonctionnement des verbes transitifs et intransitifs en français."

mots_à_tester = ["b", "bien","de","carrément", "où", "que", "en", "est", "dans"]
mots_à_tester = [ "aux", "quel", "lequel", "duquel", "desquelles"]
mots_à_tester = ["je", "pas", "tout", "tous", "toutes",
                 "je", "tu", "il", "elle", "nous", "vous", "ils", "elles", "on", "eux",
                 "me", "te", "se", "le", "la", "les", "lui", "leur", "moi","toi", "y", "que", "qui", "à", "des", "le", "là", "ici", "cela", "celle", "celui", "ceux", "celles",
                 "dont", "où", "quand", "comment", "pourquoi", "ne", "pas", "plus", "moins", "du","au"]

mots_à_tester = ['du', 'au']

def test_extracting_words(mots_à_tester:list[str]):
    errors = []
    entries = {}
    for word in mots_à_tester:
        try:
            entry = new_master_scrapper(word)
            entries[word] = entry
            print(f"Mot: {word} -> Entries: {[e['nature'] for e in entry]}")
        except ExtractException as e:
            print(f"Erreur lors de l'extraction pour {word}: {e}")
            errors.append((word, str(e)))
    print(f"{len(errors)/len(mots_à_tester)*100}% d'erreurs")
    return entries, errors

entries, errors = test_extracting_words(mots_à_tester)
print(f"{len(entries)} sur {len(mots_à_tester)} mots extraits avec succès.")
print([k for k in mots_à_tester if k not in entries])
# p = process_phrase(phrase)
# print([len(w) for w in p])