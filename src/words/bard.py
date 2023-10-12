import pickle
# class Node:
#     def __init__(self, path=''):
#         self.children = {}
#         self.endOfString = False
#         self.path = path

#     def insert(self, word):
#         current = self
#         i = 0
#         while i < len(word):
#             # Trouver la plus longue clé qui correspond au début du mot
#             keys = sorted([key for key in current.children if word.startswith(key)], key=len, reverse=True)
#             if keys:
#                 key = keys[0]
#                 current = current.children[key]
#                 i += len(key)
#             else:
#                 # Si aucune clé ne correspond, ajouter le reste du mot comme une nouvelle clé
#                 current.children[word[i:]] = Node(current.path + word[i:])
#                 break
#         if i == len(word):
#             current.endOfString = True

#     def search(self, word, exact=True):
#         current = self
#         i = 0
#         while i < len(word):
#             # Trouver la plus longue clé qui correspond au début du mot
#             keys = sorted([key for key in current.children if word[i:].startswith(key)], key=len, reverse=True)
#             if keys:
#                 key = keys[0]
#                 current = current.children[key]
#                 i += len(key)
#             else:
#                 return False if exact else current
#         return current if not exact or current.endOfString else False


# c'est un bon début, mais la fonction d'insertion est étrange. Il faut détecter si l'un des enfants et le mot 
# à insérer ont une partie commune. Dans ce cas, il faut créer un noeud intermédiaire et réinsérer les deux 
# autres noeuds

class Node:
    def __init__(self, path=''):
        self.children = {}
        self.endOfString = False
        self.path = path
        self.data=[]

    def insert(self, word):
        current = self.search(word,False)
        i = len(current.path)
        new_node=None
        # print(f"insert {word} found {current.path} reste {word[i:]}")
        for clef in current.children:
            j=0
            while j<len(clef) and i+j<len(word) and clef[j]==word[i+j]:
                j+=1
            if j>0:
                #on a trouvé une clef concordante. il faut splitter
                # assert j<len(clef) , f"{clef} {word[:i+j]}"
                if j<len(clef):
                    # print(f"split ok")
                    #création noeud intermédiaire
                    interm=Node(word[:i+j])
                    # print(f"interm: {interm}")
                    #on lui greffe ses fils
                    interm.children[clef[j:]] = current.children[clef]
                    new_node = Node(word)
                    interm.children[word[i+j:]] = new_node
                    # on remplace la branche dans le noeud parent
                    current.children[clef[:j]] = interm
                    del current.children[clef]
                    return new_node
                else:
                    #ici, le noeud intermédiaire est le nouveau node
                    interm=Node(word)
                    interm.children[clef[j:]]=current.children[clef]
                    current.children[clef[:j]] = interm
                    del current.children[clef]
                    return interm
        #si on est ici, aucune clé ne concordait, il faut juste faire pousser une feuille
        if len(current.path)==len(word):
            # print("le mot existe déjà")
            return current
        new_node =Node(word)
        try:
            current.children[word   [len(current.path):]]=new_node
        except TypeError as e:
            print(f"{type(word)} {word}")
            raise e
        return new_node
        

    def search(self, word, exact=True):
        current = self
        i = 0
        while i < len(word):
            next=False
            for clef in current.children:
                j=0
                # print(f"test {clef} {word[:i]}")
                while j<len(clef) and i+j<len(word) and clef[j]==word[i+j]:
                    j+=1
                if j == len(clef):
                    #continuer la recherche dans le prochain node
                    i += j
                    current = current.children[clef]
                    # print(f"ok {clef} {current.path}")
                    next=True
                    break
            if not next:
                return current if not exact or current.path==word else False
        return current if not exact or current.path==word else False

    def __repr__(self):
        return f"<{self.path} {len(self.data)}, {len(self.children)}>"



# peux-tu réécrire la fonction insert de façon à ce qu'elle utilise la fonction search pour trouver le noeud 
# le plus proche du mot à insérer ?
# class Node:
#     def __init__(self, path=''):
#         self.children = {}
#         self.endOfString = False
#         self.path = path

#     def insert(self, word):
#         # Trouver le nœud le plus proche du mot à insérer
#         node = self.search(word, exact=False)
#         print(f"insere {word} trouvé {node.path}")
#         i = len(node.path)
#         while i < len(word):
#             # Ajouter le reste du mot comme une nouvelle clé
#             node.children[word[i:]] = Node(node.path + word[i:])
#             node = node.children[word[i:]]
#             i += len(word[i:])
#         node.endOfString = True

#     def search(self, word, exact=True):
#         current = self
#         i = 0
#         while i < len(word):
#             # Trouver la plus longue clé qui correspond au début du mot
#             keys = sorted([key for key in current.children if word[i:].startswith(key)], key=len, reverse=True)
#             if keys:
#                 key = keys[0]
#                 current = current.children[key]
#                 i += len(key)
#             else:
#                 return False if exact else current
#         return current if not exact or current.endOfString else False



# class Node:
#     def __init__(self, path=''):
#         self.children = {}
#         self.endOfString = False
#         self.path = path

#     def insert(self, word):
#         # Trouver le nœud le plus proche du mot à insérer
#         node = self.search(word, exact=False)
#         i = len(node.path)
#         while i < len(word):
#             # Ajouter le reste du mot comme une nouvelle clé
#             node.children[word[i:]] = Node(node.path + word[i:])
#             node = node.children[word[i:]]
#             i += len(word[i:])
#         node.endOfString = True

#     def search(self, word, exact=True):
#         current = self
#         i = 0
#         while i < len(word):
#             # Trouver la première clé qui correspond au début du mot
#             for key in current.children:
#                 if word[i:].startswith(key):
#                     current = current.children[key]
#                     i += len(key)
#                     break
#             else:
#                 return False if exact else current
#         return current if not exact or current.endOfString else False


root=Node()
root.insert("banque")
root.insert("banc")
root.insert("banques")
root.insert("banquets")
root.insert("banquet")

"""
Ce code ne fonctionne pas, le problème est plus complexe. Il faut distinguer trois cas:

"""


"""
Un arbre lexicographique en python.
Chaque noeud a une propriété path dont la valeur est le chemin parcouru dans l'arbre por atteindre ce noeud.
Le path de la racine est le mot vide ""
Les nodes intermédiaires ne sont pas construits. 
Un exemple concret: on part d'un arbre vide. 
Si j'insère le mot "banque", alors le résultat attendu est
la création d'un noeud de path "banque" qui sera inséré à la racine à la clé "banque". 
Si ensuite j'ajoute le mot "banc", alors, il faut détecter le fils "banque", créer un noeud intermédiaire "ban", 
lui greffer le noeud "banque" à la clé "que", créer un node "banc", le greffer au neud "ban" à la clé "c",
supprimer le fils "banque" de la racine (en effet, il est maintenant un fils du node "ban")
et greffer le node "ban" à la clé "ban" du node racine. 
Peux-tu modifier le code pour qu'il se comporte suivant cet exemple ?

"""


def test():
    f=open("data/gramm.dmp", "rb")
    gramm=pickle.load(f)
    f.close()

    # f=open("data/gnode_tree.dmp", "rb")
    # root=pickle.load(f)
    # f.close()
    root = Node()
    # GNODE_DEBUG=True
    CNT=0
    print("debut")
    for x in gramm:
        for y in gramm[x]:
            CNT+=1
            if CNT%500==0:
                print(f"{CNT} {y.mot}")
            # assert isinstance(y, str), f"{type(y)}"
            try:
                w=root.insert(y.mot)
            except AssertionError as e:
                print(y)
                print(y.mot)
                raise e
            w.data.append(y)
    return (gramm, root)