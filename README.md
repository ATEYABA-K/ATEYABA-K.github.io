# Portfolio — Alvin Kouadio

**→ https://ateyaba-k.github.io**

Alternance 12 mois · Data Analyst / Business Analyst · Master Marketing Digital, Big Data & IA (INSEEC).

## Les deux études phares

| Étude | Données | Ce qu'on peut faire sur la page |
|---|---|---|
| [Le bookmaker gagne toujours. Même au MMA.](https://ateyaba-k.github.io/projets/ufc-paris.html) | 6 916 combats UFC et leurs cotes, 70,5 Md€ de paris sportifs (ARJEL/ANJ) | Simulateur « battez le bookmaker », calculatrice de marge |
| [Le tir que la NBA a arrêté de financer](https://ateyaba-k.github.io/projets/nba-mi-distance.html) | 4,4 millions de tirs NBA, 2003-04 à 2024-25 | Terrain animé saison par saison |

## Tout est reproductible

Chaque étude a son dossier `projets/<étude>/` :

- `analyse.py` refait tous les calculs depuis les données brutes et écrit `resultats.json` ;
- `reproduire/` contient un CSV par graphique (Power BI, Excel, Python), un classeur Excel avec les graphiques en natif et de vraies formules, et `graphiques_python.py` qui redessine tout ;
- `outils/reproduire.py` régénère ces fichiers.

## Le site

HTML, CSS et JavaScript écrits à la main, sans framework. Le fond de chaque page est un nuage de points interactif (`assets/fond.js`) : une régression est calculée en direct sous la souris.
