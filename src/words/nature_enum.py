from enum import EnumMeta, IntEnum

    

def enum_property(enum_cls, aliases=None):
    def decorator(getter):
        attr_name = f"_{getter.__name__}"

        def setter(self, value):
            if isinstance(value, enum_cls):
                setattr(self, attr_name, value)
            elif isinstance(value, str):
                try:
                    enum_value = enum_cls[value.upper()]
                    setattr(self, attr_name, enum_value)
                except KeyError:
                    raise ValueError(f"Valeur '{value}' invalide. Attendu: {list(enum_cls.__members__.keys())}")
            else:
                raise TypeError(f"Type '{type(value).__name__}' non supporté. Utilisez str ou {enum_cls.__name__}")

        def deleter(self):
            setattr(self, attr_name, None)

        return property(getter, setter, deleter, f"Propriété liée à {enum_cls.__name__}")
    return decorator



Couleur = IntEnum('Couleur',{
    'ROUGE': 1,
    'VERT': 2,
    'BLEU': 3,
    'is_primary': lambda self: self in (self.ROUGE, self.BLEU)
})

# class Couleur(IntEnum):
#     ROUGE = 1
#     VERT = 2
#     BLEU = 3

couleur_aliases = {
    "r": Couleur.ROUGE,
    "v": Couleur.VERT,
    "b": Couleur.BLEU,
    "rouge": Couleur.ROUGE,
    "vert": Couleur.VERT,
    "bleu": Couleur.BLEU
}


class TrucColoré:
    def __init__(self):
        self._couleur = None

    @enum_property(Couleur, aliases=couleur_aliases)
    def couleur(self):
        return self._couleur


# natures = {'pronom-rel', 'flex-verb', 'nom', 'flex-art-déf', 'var-typo', 'adj-dém', 'part', 'flex-art-indéf', 'flex-adj-pos', 'adj-indéf', 'prénom', 'nom-pr', 'pronom-pers', 'adj', 'adv', 'verb', 'art-part', 'flex-adj', 'flex-adj-indéf', 'onoma', 'adj-int', 'conj-coord', 'flex-adj-dém', 'adv-int', 'flex-nom', 'interj', 'symb', 'flex-pronom-dém', 'adv-rel', 'suf', 'pronom-dém', 'flex-pronom-rel', 'flex-pronom-pers', 'phr', 'flex-prép', 'lettre', 'adj-num', 'pronom-int', 'prép', 'flex-pronom-int', 'adj-rel', 'adj-pos', 'flex-adv', 'pronom', 'nom-fam', 'pronom-indéf', 'flex-pronom-indéf', 'art-indéf', 'flex-adj-int', 'art-déf', 'conj'}

# nature_tokens=set([x for nat in natures for x in nat.split("-")])
# NatTok=IntEnum("NatTok", {tok.upper(): idx for idx, tok in enumerate(sorted(nature_tokens))})


# # comment faire si je souhaite aussi définir des méthodes spécifiques pour la classe générée ?
# # Excellente question, Vincent. Pour créer un IntEnum à la volée avec des méthodes personnalisées, tu peux utiliser la fonction EnumMeta indirectement via type() ou en sous-classant dynamiquement. Voici plusieurs approches selon ton besoin :

# # Méthode 1 : Utiliser type() avec une base IntEnum
# # Tu peux injecter des méthodes dans la classe générée comme ceci :



# def create_enum_with_methods(name, members=None, methods=None):
#     methods = methods or {}
#     return EnumMeta(name, (IntEnum,), {**members, **methods})



# # ✅ Exemple d’usage
# # python
# def is_primary(self):
#     return self in (self.ROUGE, self.BLEU)

# Couleur = create_enum_with_methods(
#     "Couleur",
#     {"ROUGE": 1, "VERT": 2, "BLEU": 3},
#     {"is_primary": is_primary}
# )

# print(Couleur.ROUGE.is_primary())  # True
# print(Couleur.VERT.is_primary())   # False
# # 🧩 Méthode 2 : Créer une sous-classe à la volée
# # Si tu veux plus de contrôle, tu peux définir une classe dans une fonction :

# # python
# def make_enum():
#     class Couleur(IntEnum):
#         ROUGE = 1
#         VERT = 2
#         BLEU = 3

#         def is_primary(self):
#             return self in (self.ROUGE, self.BLEU)

#     return Couleur

# Couleur = make_enum()
# 🧩 Méthode 3 : Utiliser EnumMeta directement (avancé)
# python
# from enum import EnumMeta, IntEnum

# Couleur = IntEnum('Couleur',{
#     'ROUGE': 1,
#     'VERT': 2,
#     'BLEU': 3,
#     'is_primary': lambda self: self in (self.ROUGE, self.BLEU)
# })
# 🧠 Notes
# Tu peux aussi injecter des @classmethod, des @staticmethod, ou des propriétés.

# Pour des méthodes plus complexes, il est souvent plus lisible de définir une vraie classe dans une fonction.

