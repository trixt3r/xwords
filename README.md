# xwords

1 - présentation
2 - implémentation
3 - fonctionnalités
4 - feuille de route
4.1 - implémentation
4.2 - fonctionnalités
5 - perspectives
6 - installation & usage

1 - présentation

Ceci est un petit soft que l'auteur a codé en plusieurs phases, s'étalant de 2013 à 2020. 
C'est la lecture du pendule de Foucault et son Aboulafia qui m'a inspiré.
Bien que fonctionnel, il faut plus y voir une pièce d'art ou d'artisanat.
En effet, le processus créatif m'a amené à revenir plusieurs fois sur la structure des données, (et donc adapter les algos),
à revoir mes exigences à la hausse niveau fonctionnalités, tout en gardant des bouts de code dupliqués dormants, donnant au tout
une allure génomique. Bref c'est programmé à la rash, pas de contrôle de version, pas de graphes uml, pas de diagramme gantt,
rien de tout ça, juste un cerveau qui se fait obéir.

2 - implémentation
Brièvement, voici les caractéristiques du produit:
il s'agit d'un soft en python qui permet de générer des anagrammes et des contrepèteries.
J'ai pas fait de recherche internet sur l'état de l'art, j'avais juste furieusement envie de coder ça.

La structure centrale c'est un arbre de hachage. La clé c'est ce que j'appelle la forme canonique d'un mot,
c'est à dire toutes les lettres du mot dans l'ordre alphabétique. Exemple: guignol devient ggilnou.
ça permet d'accélérer la recherche. La preuve est triviale.

Au départ j'avais une liste de mots au format txt et je faisais des anagrammes. 
Par la suite, remarquant que le problème des contrepèteries était le même j'ai voulu rajouter ça.
Pour que ce soit plus simple, j'ai écrit un crawler qui extrait de wikipedia le mot en phonétique.
Du coup je me suis dit, tant qu'à faire, on va extraire d'autres infos, le genre, le nombre, 
la nature (nom, verbe adverbe, etc) du mot, et en plus haut niveau, les relations à d'autres mots: antonymes, synonymes etc
en me disant, ça pourra toujours servir plus tard pour faire d'autres trucs intéressants. L'extraction c'est fait avec 
BeautifulSoup 4, de mémoire.

3 - Fonctionnalités
Dans les grandes lignes ça fonctionne même si c'est plein de bugs (voir section feuille de route).
Pour lancer le tout, il faut d'abord l'ancer le serveur de base de données (entièrement artisanal)
ensuite, c'est une appli web (Flask) qui demande au serveur d'exécuter la recherche avant d'afficher le résultat.
Pour javascript, j'utilise un peu de jQuery.

ça s'affiche sous forme de tableau, avec des colonnes pour le mot et les infos associées (genre, nombre, nature etc)
on peut trier sur plusieurs colonnes (par exemple, regrouper par nature puis par ordre alphabétique.) Pour cela, il suffit de déplacer
par D&D les options de recherche dans la liste au-dessus du tableau (éviter de cliquer sur les colonnes)

Quand on clique sur un mot il est "choisi", il apparaît dans une liste en haut, et tous les mots qui ne peuvent plus s'écrire 
avec les lettres restantes disparaissent du tableau. On peut aussi "déchoisir" un mot en cliquant sur la petite croix. on peut aussi les 
ordonner par drag&drop.

4 - feuille de route
4.1 implémentation
-Il y a pas mal de boulot. Enlever tout ce qui sert à rien. Faire fonctionner la version de l'arbre
qui zappe les noeuds intermédiaires vides (gain d'espace et de mémoire).
-Reprendre certaines parties qui sont codées avec les pieds.
-Améliorer les structures de données (utiliser des enum pour les caractéristiques d'un mot, par exemple)
-Intégrer le dictionnaire de verbes
-Améliorer le crawler (qui bugge pas mal, du coup le dictionnaire est plein de trous et de ratures)
-Améliorer la lisibilité du code, mettre des commentaires.

4.2 - fonctionnalités
-Rendre accessible dans flask la recherche sur les contrepétries. ça implique une page intermédiaire, pour la désambiguation (des mots
avec la même graphie mais des prononciations différentes: ex: "nous portions des portions de potage." ainsi que les mots dont
la prononciation n'est pas connue) ça, c'est le plus important.
-crawlage automatique sur wikipedia quand le mot est inconnu
-Rendre accessible le tri par méta données (champs synonymes, antonymes paronymes etc) à l'aide, par exemple d'un nuage de mots-clés.
-Prendre en compte les liaisons entre les mots dans la recherche phonétique.
-Un système de compte/session très simple, avec possibilité d'enregistrer les recherches complètes (phrase de départ, mots trouvés, reste)
-rendre accessible la fonction confusion d'accents (par exemple, possibilité de demander une recherche ou le son "é" et le son "è" sont considérés comme équivalents.)
C'est déjà codé, "il suffit de" le rendre accessible dans l'interface web. 

-Mise en page, rendre ça plus joli.
-Améliorer le crawler, faire un robot wikipedia qui (potentiellement) met à jour certaines données.
Je pense notamment à toutes les fiches incomplètes, (sur pas mal de mots composés par exemple, la fiche ne contient pas la phonétique.) 
Normalement c'est un taf pour de l'IA mais si personne s'y colle...

5 - Perspectives
Quand on regarde vers l'arrière, même si ça saute pas aux yeux, c'est évident que ce genre d'outil existe déjà. 
C'est pas grave, hein, ce qui est grave c'est que les sources n'aietn jamais été accessibles.
Vers l'avant, on a envie de dire: quand on aura un soft qui fonctionne bien, avec un dico qui tient la route, les possibilités sont infinies;
ça pourrait être sympa de scripter un petit truc qui mangerait du texte et générerait des anagrammes et des contrepétries tout seul,
en essayant de rester dans le contexte, ou en suivant un contexte cible (ex: le texte original parle de sport, 
les phrases générées parlent d'amour) Mais ça requiert déjà de faire de l'analyse syntaxique, pour générer des 
phrases qui tiennent la route au moins grammaticalement.
Un autre truc sympa, ce serait de faire une recherche phonétique de segments de phrase parallèles à la phrase.
(ex: tes laitues naissent-elles/télé thune Estelle)
Intégrer d'autres langues aussi, pas une mauvaise idée. Avec un lexique phonétique pour traduire les phonèmes étrangers en phonèmes français.

6 - installation et usage
Les paquets suivants sont requis: flask, unidecode, beautifulsoup 4, requests
ensuite, il faut lancer en premier le serveur "DB": python3 server.py
puis le serveur flask:
export FLASK_APP=flask_server
flask run

ensuite, on peut accéder à l'appli à l'URL suivante: 127.0.0.1:5000/anagrammes
