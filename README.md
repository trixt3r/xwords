# xwords

Big todo list:

liste 1: à faire pour que ça devienne pleinement fonctionnel:
  - l'application flask doit utiliser le serveur (server.py)
  - contrepeteries: options "keep_accents": o ouvert/fermé, é/è, etc
  - server.py: implémenter le passage et respect des options de recherche: mot exact/keep_accents
  - masse de tests, notamment sur le mode contrepeteries: est ce qu'on oublie pas des mots ? et surtout, est ce qu'il n'y a pas des mots faux-positifs ?

liste 1 prime: améliorer le dictionnaire
  - améliorer le wiki crawler: traquer les bugs en examinant les mots qui ont planté l'algo
  - améliorer le wiki crawler: système de report automatique des erreurs. Por chaque mot ayant planté, indiqué, même vaguement, la raison du plantage: pas de API, pas de désinences, etc
  - terminer le scan de la liste de mots jusqu'à Z
  - cleaner la grammaire:
    - rechercher tous les adjectifs qui ont été mal entrés (problème avec les désinences)
    - rechercher
    - gérer les verbes uniquement personnels
  - système permettant de construire automatiquement l'API d'un mot manquant (notamment pour tous les mots dérivés d'un autre à l'aide d'un préfixe ou d'un suffixe, qui ne sont pas suffisamment renseignés dans wiktionary) à adosser à un système permettant de mettre à jour wiktionary pour ces entrées manquantes (à terme: un wiki bot, dans un premier temps: tenir à jour une liste des entrées wiki défaillantes)


liste 2: pour améliorer l'expérience utilisateur
  - système de compte, sauvegarde et partage des recherches
  - better UI, html/CSS
  - système de report des erreurs détectés par l'utilisateur: faux positifs, mots inconnus
  - scan recherche automatique des mots inconnus
  - gestion des langues étrangères
  - intégrer système de tag des champs lexicaux, étoffer, permettre à l'user d'étoffer



liste 4: amélioration de l'expérience développeur (y'a du boulot)
  - masse de commentaires manquants
  - code dupliqué ou inutile
  - un peu de refactoring: noms de classe, fichiers, package
  - implémentation:
    - beaucoup de gains mémoire possible:
      - éviter tous les noeuds intermédiaires inutiles (ne contenant pas de données) normalement c'est simple mais je me suis cassé les dents là dessus
      - optimiser les genre/nombre/champs lexicaux/etc par des ints au lieu de string ?
  - il manque plein de trucs dans cette listen
