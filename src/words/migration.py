# 05/12/2024
# Ma demande: (copilot)
# ecris une fonction python. Elle prend un ensemble d'objets en paramètre. Chacun de ces objets possède un champ nommé "lex", qui est un set de str.
#  La fonction doit collecter dans une liste l'ensemble des strings rencontrés dans chaque champ de chaque objet, ainsi que remplacer 
# la liste de str de chaque objet par la liste des index correspondants. Elle renvoie la liste collectée. 
# J'aimerais si possible que l'algo ne parcoure qu'une seule fois l'ensemble d'objets.

# réponse:
# Bien sûr! Voici une fonction Python qui répond à vos besoins. Cette fonction parcourt l'ensemble des objets une seule fois pour collecter les chaînes de caractères et remplacer les sets par les index correspondants :

def traiter_objets(objets):
    """
    Traite un ensemble d'objets pour collecter les strings et remplacer les sets par des index.
    
    :param objets: Ensemble d'objets, chacun ayant un champ 'lex' qui est un set de strings
    :return: Liste des strings collectés
    """
    # Liste pour collecter toutes les strings
    liste_strings = []
    # Dictionnaire pour stocker les index des strings
    index_dict = {}

    # Parcourir chaque objet une seule fois
    for obj in objets:
        # Liste pour stocker les index des strings pour l'objet actuel
        index_list = []
        for string in obj['lex']:
            if string not in index_dict:
                # Ajouter la string à la liste et au dictionnaire avec son index
                index_dict[string] = len(liste_strings)
                liste_strings.append(string)
            # Ajouter l'index de la string à la liste des index pour l'objet actuel
            index_list.append(index_dict[string])
        # Remplacer le set de strings par la liste des index
        obj['lex'] = index_list

    return liste_strings

# Exemple d'utilisation
objets = [
    {'lex': {'apple', 'banana', 'cherry'}},
    {'lex': {'banana', 'date', 'fig'}},
    {'lex': {'grape', 'apple', 'fig'}}
]

liste_strings = traiter_objets(objets)
print("Liste des strings collectés:", liste_strings)
print("Objets après traitement:", objets)
