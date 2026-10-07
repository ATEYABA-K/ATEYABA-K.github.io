# Le tir que la NBA a arrêté de financer

Chaque tir est traité comme un investissement : une possession dépensée, des points rapportés.
Sur 4,4 millions de tirs (2003-04 à 2024-25), je mesure le rendement de chaque zone du terrain
et la façon dont les équipes ont réalloué leurs tirs.

**L'étude interactive :** https://ateyaba-k.github.io/projets/nba-mi-distance.html

## Résultats

- Le mi-distance est passé de 36 % à 10 % des tirs ; le 3 points de 18 % à 42 %.
- Il rapporte environ 0,8 point par tir, moins que n'importe quel 3 points, chaque saison sans exception.
- Sur les +0,145 point par tir gagnés par la ligue, 0,053 (37 %) viennent du seul déplacement des tirs.
- Jusqu'en 2015, moins de mi-distance = équipe plus efficace (corrélation ≈ −0,4). Depuis 2019, le lien a disparu.

## Refaire les graphiques (Excel)

Tous les graphiques de l'étude sont faits dans Excel. Le tuto pas à pas est dans [TUTO.md](TUTO.md).

- `excel/nba-mi-distance-exercice.xlsx` : les données, rien n'est fait — pour s'entraîner.
- `excel/nba-mi-distance-corrige.xlsx` : la version finie (formules + graphiques).
- `excel/graphiques/` : les graphiques exportés depuis le corrigé (ceux du site).
- `excel/csv/` : les données pour Power BI.

## Calcul des données

`analyse.py` (Python) télécharge les données brutes et calcule `resultats.json`. `outils/excel.py` construit ensuite les fichiers Excel, et `outils/tutos.py` les tutos.


## Données

Tous les tirs de saison régulière (NBA.com), compilés par
[DomSamangy/NBA_Shots_04_25](https://github.com/DomSamangy/NBA_Shots_04_25). Lancers francs non inclus.
