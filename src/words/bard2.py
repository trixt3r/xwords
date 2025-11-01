# 05/12/24, je me lance dans un debug de ça. 
# j'ai une piste prometteuse, mais je fais une copie au cas où

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
    def __init__(self, path='', parent=None):
        self.children = {}
        self.endOfString = False
        self.path = path
        self.data = [path]

    def insert(self, data):
        current = self.search(data, False)
        i = len(current.path)
        new_node = None
        # print(f"insert {word} found {current.path} reste {word[i:]}")
        for clef in current.children:
            j = 0
            while j<len(clef) and i+j<len(data) and clef[j]==data[i+j]:
                j += 1
            if j>0:
                #   on a trouvé une clef concordante. il faut forker
                # exemple: le mot "banques" existe, et on insère "banquets"
                # assert j<len(clef) , f"{clef} {word[:i+j]}"
                if j<len(clef):
                    # print(f"split ok")
                    #création noeud intermédiaire
                    interm=Node(data[:i+j])
                    # print(f"interm: {interm}")
                    #on lui greffe ses fils
                    interm.children[clef[j:]] = current.children[clef]
                    new_node = Node(data)
                    interm.children[data[i+j:]] = new_node
                    # on remplace la branche dans le noeud parent
                    current.children[clef[:j]] = interm
                    del current.children[clef]
                    # print(f"{word} SORTIE A")
                    return new_node
                else:
                    # ici, le noeud intermédiaire est le nouveau node
                    # (le nouveau mot est un sous-mot d'un mot existant)
                    interm = Node(data)
                    interm.children[clef[j:]] = current.children[clef]
                    current.children[clef[:j]] = interm
                    del current.children[clef]
                    # print(f"{word} SORTIE B")
                    return interm
                
        # si on est ici, aucune clé ne concordait, il faut juste faire pousser une feuille ??!
        if len(current.path)==len(data):
            print(f"le mot {data} existe déjà - sortie C")
            return current
        new_node =Node(data)

        try:
            current.children[data   [len(current.path):]]=new_node
        except TypeError as e:
            print(f"{type(data)} {data}")
            raise e
        # print(f"{word} sortie D")
        return new_node
        

    def search(self, key, exact=True):
        current = self
        i = 0
        while i < len(key):
            next=False
            for clef in current.children:
                j=0
                # print(f"test {clef} {word[:i]}")
                while j<len(clef) and i+j<len(key) and clef[j]==key[i+j]:
                    j+=1
                if j == len(clef):
                    #continuer la recherche dans le prochain node
                    i += j
                    current = current.children[clef]
                    # print(f"ok {clef} {current.path}")
                    next=True
                    break
            if not next:
                return current if not exact or current.path==key else False
        return current if not exact or current.path==key else False

    def get_key(self, obj):
        return None

    def __repr__(self):
        return f"<{self.path} {len(self.data)}, {len(self.children)}>"


# """
# la meme modifiée
# """

# class DynamicClassFactory:
#     def __init__(self, base_class):
#         self.base_class = base_class
#         self.created_classes = {}

#     def create_subclass(self, custom_method):
#         method_name = custom_method.__name__
#         if method_name not in self.created_classes:
#             class_name = f"DynamicSubClass_{method_name}"
#             new_class = type(class_name, (self.base_class,), {method_name: custom_method})
#             self.created_classes[method_name] = new_class
#         return self.created_classes[method_name]

# # Créer une instance de la fabrique
# factory = DynamicClassFactory(Node)

# def get_ort_key(self, obj):
#     return obj.word

# def get_api_key(self, obj):
#     return obj.api

# OrtTree = factory.create_subclass(get_ort_key)
# ApiTree = factory.create_subclass(get_api_key)


# class GData:
#     def __init__(self, f1:str, f2:int):
#         self.f1=f1
#         self.f2=f2
#     pass

# class BaseClass:
#     def search(self, path:str):
#         pass
#     def insert(self, obj:GData):
#         pass
#     def method1(self):
#         return "Base method1"

#     def get_key(self, obj:GData):
#         return obj.f2        

#     def create_new_instance(self):
#         # Utiliser type(self) pour obtenir la classe de l'instance actuelle
#         return type(self)()

# # Créer une instance de la fabrique
# factory = DynamicClassFactory(BaseClass)

# # Définir une méthode personnalisée
# def custom_method1(self):
#     return "Custom method1"

# # Créer une sous-classe avec la méthode personnalisée
# SubClass = factory.create_subclass(custom_method1)
# instance = SubClass()
# print(instance.method1())  # Output: Custom method1
# print(instance.method2())  # Output: Base method2

# # Créer une nouvelle instance de la même sous-classe dynamiquement
# new_instance = instance.create_new_instance()
# print(new_instance.method1())  # Output: Custom method1
# print(new_instance.method2())  # Output: Base method2



#     # class Node:
#     # def __init__(self, path='', parent=None):
#     #     self.children = {}
#     #     self.endOfString = False
#     #     self.path = path
#     #     self.data = [path]

#     # def insert(self, word):
#     #     current = self.search(word, False)
#     #     i = len(current.path)
#     #     new_node = None
#     #     # print(f"insert {word} found {current.path} reste {word[i:]}")
#     #     for clef in current.children:
#     #         j = 0
#     #         while j<len(clef) and i+j<len(word) and clef[j]==word[i+j]:
#     #             j += 1
#     #         if j>0:
#     #             #   on a trouvé une clef concordante. il faut forker
#     #             # exemple: le mot "banques" existe, et on insère "banquets"
#     #             # assert j<len(clef) , f"{clef} {word[:i+j]}"
#     #             if j<len(clef):
#     #                 # print(f"split ok")
#     #                 #création noeud intermédiaire
#     #                 interm=Node(word[:i+j])
#     #                 # print(f"interm: {interm}")
#     #                 #on lui greffe ses fils
#     #                 interm.children[clef[j:]] = current.children[clef]
#     #                 new_node = Node(word)
#     #                 interm.children[word[i+j:]] = new_node
#     #                 # on remplace la branche dans le noeud parent
#     #                 current.children[clef[:j]] = interm
#     #                 del current.children[clef]
#     #                 # print(f"{word} SORTIE A")
#     #                 return new_node
#     #             else:
#     #                 # ici, le noeud intermédiaire est le nouveau node
#     #                 # (le nouveau mot est un sous-mot d'un mot existant)
#     #                 interm = Node(word)
#     #                 interm.children[clef[j:]] = current.children[clef]
#     #                 current.children[clef[:j]] = interm
#     #                 del current.children[clef]
#     #                 # print(f"{word} SORTIE B")
#     #                 return interm
                
#     #     # si on est ici, aucune clé ne concordait, il faut juste faire pousser une feuille ??!
#     #     if len(current.path)==len(word):
#     #         print(f"le mot {word} existe déjà - sortie C")
#     #         return current
#     #     new_node =Node(word)

#     #     try:
#     #         current.children[word   [len(current.path):]]=new_node
#     #     except TypeError as e:
#     #         print(f"{type(word)} {word}")
#     #         raise e
#     #     # print(f"{word} sortie D")
#     #     return new_node
        

#     # def search(self, word, exact=True):
#     #     current = self
#     #     i = 0
#     #     while i < len(word):
#     #         next=False
#     #         for clef in current.children:
#     #             j=0
#     #             # print(f"test {clef} {word[:i]}")
#     #             while j<len(clef) and i+j<len(word) and clef[j]==word[i+j]:
#     #                 j+=1
#     #             if j == len(clef):
#     #                 #continuer la recherche dans le prochain node
#     #                 i += j
#     #                 current = current.children[clef]
#     #                 # print(f"ok {clef} {current.path}")
#     #                 next=True
#     #                 break
#     #         if not next:
#     #             return current if not exact or current.path==word else False
#     #     return current if not exact or current.path==word else False

#     # def __repr__(self):
#     #     return f"<{self.path} {len(self.data)}, {len(self.children)}>"




def test1():
    root=Node()
    n = root.insert("banque")
    assert n==root.search("banque")
    assert root.search("banque").data[0]=="banque"
    n=root.insert("banc")


    n=root.insert("banques")

    # split requis

    n=root.insert("banquets")

    # juste mettre à jour les données du noeud
    # n = root.insert("banquet")
    # 
    return root

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


def test2():
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


# ####################################
# # search/get ==  __getitem__ et __setitem__
# """
# voici le code d'un arbre (GNode) qui stocke des objets de type GData
# on suppose que la fonction search et insert sont opérationnelles.
# """
# class GData:
#     def __init__(self, f1:str, f2:int):
#         self.f1 = f1
#         self.f2 = f2

# class GNode:
#     """
#         renvoie le noeud trouvé en suivant le chemin path
#     """
#     def search(self, path:str):
#         pass

#     """
#         insère un objet dans l'arbre. Le chemin auquel le'objet sera rangé correspond au champ f1 de GData
#     """
#     def insert(self, obj:GData):
#         pass

# # mettons que j'aie une classe en python avec plusieurs méthodes interdépendantes. J'aimerais pouvoir créer, à runtime,
# #des classes descendantes qui ne modifient qu'une de ces méthodes. Quel est le bon pattern ?

# class BaseClass:
#     def method1(self):
#         return "Base method1"

#     def method2(self):
#         return "Base method2"

# def create_dynamic_subclass(base_class, method_name, custom_method):
#     class_name = f"DynamicSubClass_{method_name}"
#     return type(class_name, (base_class,), {method_name: custom_method})

# # Exemple d'utilisation
# def custom_method1(self):
#     return "Custom method1"

# DynamicSubClass = create_dynamic_subclass(BaseClass, 'method1', custom_method1)
# instance = DynamicSubClass()
# print(instance.method1())  # Output: Custom method1
# print(instance.method2())  # Output: Base method2


# # peux tu créer une classe qui encapsule create_dynamic_subclass, pour garantir que pouyr chaque methode, la classe n'est construite qu'une fois.
# # Bien sûr! Voici une classe Python qui encapsule la fonction create_dynamic_subclass et garantit que chaque méthode est construite une seule 
# # fois pour chaque classe descendante :

# class DynamicClassFactory: 
#     def __init__(self, base_class):
#         self.base_class = base_class
#         self.created_classes = {}

#     def create_subclass(self, method_name, custom_method):
#         if method_name not in self.created_classes:
#             class_name = f"DynamicSubClass_{method_name}"
#             new_class = type(class_name, (self.base_class,), {method_name: custom_method})
#             self.created_classes[method_name] = new_class
#         return self.created_classes[method_name]

# # Exemple d'utilisation
# class BaseClass:
#     def method1(self):
#         return "Base method1"

#     def method2(self):
#         return "Base method2"

# # Créer une instance de la fabrique
# factory = DynamicClassFactory(BaseClass)

# # Définir une méthode personnalisée
# def custom_method1(self):
#     return "Custom method1"

# # Créer une sous-classe avec la méthode personnalisée
# SubClass = factory.create_subclass('method1', custom_method1)
# instance = SubClass()
# print(instance.method1())  # Output: Custom method1
# print(instance.method2())  # Output: Base method2

# # Réutiliser la même sous-classe pour la même méthode
# SameSubClass = factory.create_subclass('method1', custom_method1)
# print(SameSubClass is SubClass)  # Output: True



# ###########
# """
# si maintenant, je veux instancier, depuis une methode d'une de ces sous classes generees, un objet de même type ? Comme je ne connais pas encore 
# le nom de la classe quand je code, je dois pouvoir appeler le constructeur dynamiquement
# Pour instancier dynamiquement un objet de la même classe à partir d'une méthode d'une sous-classe générée, 
# vous pouvez utiliser la fonction 
#                                 type(self) pour obtenir la classe de l'instance actuelle. Voici comment vous pouvez le faire :
# """
# class DynamicClassFactory:
#     def __init__(self, base_class):
#         self.base_class = base_class
#         self.created_classes = {}

#     def create_subclass(self, method_name, custom_method):
#         if method_name not in self.created_classes:
#             class_name = f"DynamicSubClass_{method_name}"
#             new_class = type(class_name, (self.base_class,), {method_name: custom_method})
#             self.created_classes[method_name] = new_class
#         return self.created_classes[method_name]


# class BaseClass:

#     def method1(self):
#         return "Base method1"

#     def method2(self):
#         return "Base method2"

#     def create_new_instance(self):
#         # Utiliser type(self) pour obtenir la classe de l'instance actuelle
#         return type(self)()

# # Créer une instance de la fabrique
# factory = DynamicClassFactory(BaseClass)

# # Définir une méthode personnalisée
# def custom_method1(self):
#     return "Custom method1"

# # Créer une sous-classe avec la méthode personnalisée
# SubClass = factory.create_subclass('method1', custom_method1)
# instance = SubClass()
# print(instance.method1())  # Output: Custom method1
# print(instance.method2())  # Output: Base method2

# # Créer une nouvelle instance de la même sous-classe dynamiquement
# new_instance = instance.create_new_instance()
# print(new_instance.method1())  # Output: Custom method1
# print(new_instance.method2())  # Output: Base method2



##########################################      Below      ################################################
##########################################INUTILE PROBABLMENT################################################
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
