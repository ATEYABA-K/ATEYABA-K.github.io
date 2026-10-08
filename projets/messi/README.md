# Messi est-il le meilleur joueur de l'histoire ?

Comparaison de Messi avec 13 grands attaquants, puis analyse de ses tirs en Liga.

**L'étude complète :** https://ateyaba-k.github.io/projets/messi.html

## Résultats

- En buts au total (club et sélection), Cristiano Ronaldo est devant : 937 contre 885.
- Sans les penalties et avec les passes décisives, Messi apporte 1,11 but ou passe par match de club, le meilleur chiffre des 14 joueurs (Mbappé 0,97, Ronaldo 0,85).
- En Liga, de 2004-05 à 2020-21, il marque 412 buts hors penalty pour 265,5 attendus (xG StatsBomb), soit +146,5, au-dessus de ses xG 16 saisons sur 17.
- Hors de la surface, il convertit 9,3 % de ses tirs, contre 3,6 % pour les autres joueurs des mêmes matchs.

## Fichiers

- `telecharger_tirs.py` : télécharge les tirs des matchs du Barça en Liga (StatsBomb, données ouvertes).
- `analyse.py` : calcule `resultats.json` à partir des données Transfermarkt et des tirs.
- `excel/graphiques/` : les graphiques du site, faits dans Excel.

## Données

- Transfermarkt : [salimt/football-datasets](https://github.com/salimt/football-datasets), octobre 2025.
- Tirs et xG : [StatsBomb open data](https://github.com/statsbomb/open-data).
- Ballons d'Or : France Football, liste publiée par [Sports Illustrated](https://www.si.com/soccer/men-s-ballon-d-or-full-list-of-winners).
