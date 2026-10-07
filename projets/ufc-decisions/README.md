# Sur un ring, on gagne aux points. Mais lesquels ?

Ce que les juges de l'UFC récompensent vraiment quand un combat va à la décision.

**L'étude complète, avec les graphiques :** https://ateyaba-k.github.io/projets/ufc-decisions.html

## Les résultats en bref

- 49 % des combats UFC finissent aux points depuis 2017 (32 % entre 2001 et 2008).
- Dans 21 % des 4 026 décisions analysées, le vainqueur a porté **moins** de frappes significatives.
- Dans 78 % de ces cas, il avait plus de temps de contrôle ou plus d'amenées au sol.
- Sous 5 % d'écart de frappes, la décision tombe à 51 % : du pile ou face.
- Avec cinq statistiques, une régression logistique prédit 84 % des décisions (validation croisée sur 5 blocs).

## Reproduire

```bash
pip install pandas numpy scikit-learn
python analyse.py
```

Le script télécharge les données, refait tous les calculs et réécrit `resultats.json`.

## Données

Statistiques officielles de [ufcstats.com](http://ufcstats.com), compilées par le dépôt public
[Greco1899/scrape_ufc_stats](https://github.com/Greco1899/scrape_ufc_stats). Période : 2001-2026 (règles unifiées).

## Limites

- Les juges notent round par round ; l'analyse agrège le combat entier. Prochaine étape : le niveau round.
- Corrélation, pas causalité.
- Les statistiques de frappes sont comptées à la main.
- Les critères de notation ont été précisés en 2017.
