# Portfolio d'Alvin Kouadio

**→ https://ateyaba-k.github.io**

Alternance 12 mois · data analyst, chargé de projet digital · Master Marketing Digital, Big Data & IA (INSEEC).

## Les deux études phares

| Étude | Données | Dans Excel |
|---|---|---|
| [Le bookmaker gagne toujours. Même au MMA.](https://ateyaba-k.github.io/projets/ufc-paris.html) | 6 916 combats UFC et leurs cotes, 70,5 Md€ de paris sportifs (ARJEL/ANJ) | 1 000 parieurs simulés, calculatrice de marge |
| [Le tir que la NBA a arrêté de financer](https://ateyaba-k.github.io/projets/nba-mi-distance.html) | 4,4 millions de tirs NBA, 2003-04 à 2024-25 | Carte de chaleur du terrain, décomposition mix / adresse |

## Des graphiques faits dans Excel, et les tutos pour les refaire

Chaque étude a son dossier `projets/<étude>/` :

- `TUTO.md` : le tuto pas à pas (aussi en page sur le site) ;
- `excel/<étude>-exercice.xlsx` : les données, rien n'est fait ;
- `excel/<étude>-corrige.xlsx` : la version finie, d'où sortent les graphiques du site ;
- `excel/csv/` : les données pour Power BI ;
- `analyse.py` : le calcul des données brutes (Python).

Les huit projets plus courts (churn télécom, ventes de musique, scoring B2B, IA dans les PME, reporting Insee, inflation, cadrage et suivi de projet) ont le même type de dossier, sans `analyse.py` : leurs données viennent du dépôt GitHub d'origine.

## Le site

HTML, CSS et JavaScript écrits à la main, sans framework. Le fond de chaque page est un nuage de points interactif (`assets/fond.js`) : une régression est calculée en direct sous la souris.
