# Le bookmaker gagne toujours. Même au MMA.

Le MMA est légal en compétition en France depuis 2020, l'UFC passe par Paris chaque année depuis 2022,
et les paris sportifs en ligne ont atteint 10,3 milliards d'euros de mises en 2024 (ANJ).
Cette étude reprend les cotes de 6 916 combats UFC (2010-2026) pour voir qui gagne vraiment.

**L'étude complète :** https://ateyaba-k.github.io/projets/ufc-paris.html

## Résultats

- Le favori gagne 66,6 % des combats ; les cotes sont très bien calibrées.
- Marge médiane du bookmaker : 3,7 % par combat.
- Rendement moyen : −2,9 % en jouant toujours le favori, −7,6 % toujours l'outsider, −30 % sur les cotes au-dessus de 5.
- Seuls les très gros favoris (cote < 1,30) sont légèrement positifs (+1,6 % ± 2,3 %) : biais favori-outsider, non significatif.
- Sur 10 000 parieurs simulés (100 paris de 10 €, camp au hasard), 69 % finissent perdants.

## L'argent du marché français (paris sportifs en ligne, 2010-2025)

- 70,5 Md€ misés, 58,6 Md€ revenus aux parieurs, 11,9 Md€ gardés par les opérateurs (17 %).
- Corrélation mises / argent gardé : r = 0,997 (en partie mécanique : gardé = mises − gains).
- La part gardée baisse doucement avec le temps (r = −0,78), de environ 20 % à 15,3 % en 2025.
- Simulation : plus on parie, plus on perd (r = −0,39 entre nombre de paris et bilan).

Sources : rapports ARJEL (2010-2018) et ANJ (2020-2025). Mises 2019 déduites ; PBJ 2024 révisé par l'ANJ.

## Graphiques

Tous les graphiques de l'étude sont faits dans Excel, à partir des résultats calculés par `analyse.py`. Ils sont dans `excel/graphiques/`.

## Calcul des données

`analyse.py` (Python) télécharge les données brutes et calcule `resultats.json`. Les graphiques sont ensuite construits dans Excel.


## Données

- Cotes et résultats : [shortlikeafox/ultimate_ufc_dataset](https://github.com/shortlikeafox/ultimate_ufc_dataset) (Ultimate UFC Dataset, Kaggle).
- Événements : [Greco1899/scrape_ufc_stats](https://github.com/Greco1899/scrape_ufc_stats) (ufcstats.com).
- Contexte : ANJ, bilan du marché des jeux d'argent 2024 ; ministère des Sports (légalisation du MMA, 2020).

Jouer comporte des risques : endettement, dépendance… Appelez le 09 74 75 13 13 (appel non surtaxé).
