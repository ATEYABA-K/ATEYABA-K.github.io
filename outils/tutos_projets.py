"""Tutos des 8 projets courts du portfolio (même format que les tutos des études, voir tutos.py)."""

GH = "https://github.com/ATEYABA-K/"


def projet(depot, **k):
    return {"retour": GH + depot, "retour_label": "Retour au projet sur GitHub", "depot": GH + depot, "quoi": "les graphiques du projet", **k}


TUTOS_PROJETS = {
    "churn-telco": projet(
        "analyse-churn-telco", titre="Où se concentre le risque de départ client ?", fichier="churn-telco", duree="45 min",
        apprend=["SI imbriqués", "tableau croisé dynamique", "NB.SI et NB.SI.ENS", "histogramme avec étiquettes"],
        etapes=[
            {"titre": "Classer les clients par ancienneté", "onglet": "Clients", "image": None,
             "objectif": "7 043 clients. On range chacun dans une tranche d'ancienneté pour pouvoir comparer.",
             "points": [("1.1 La tranche", ["En **F5**, puis double-clic sur la poignée : Excel recopie jusqu'à la ligne 7047."],
                         [("F5", '=SI(B5<=12;"0-12 mois";SI(B5<=24;"13-24 mois";SI(B5<=48;"25-48 mois";"49 mois et +")))', "IF")])],
             "verifier": "Le client de la ligne 5 (ancienneté 1 mois) est en « 0-12 mois »."},
            {"titre": "Calculer les taux de départ", "onglet": "Analyse", "image": None,
             "objectif": "Deux méthodes, au choix. La première est la plus rapide, la seconde se met à jour toute seule.",
             "points": [
                 ("2.1 Méthode rapide : le tableau croisé dynamique", [
                     "Onglet **Clients** : cliquez dans le tableau → **Insertion** → **Tableau croisé dynamique** → **Nouvelle feuille de calcul**.",
                     "Glissez **Contrat** dans **Lignes**, **Churn** dans **Colonnes**, **Client** dans **Valeurs** (Excel compte les clients).",
                     "Clic droit sur un nombre → **Afficher les valeurs** → **% du total de la ligne**. La colonne « Yes » donne le taux de départ."], []),
                 ("2.2 Méthode formules (celle du corrigé)", [
                     "Onglet **Analyse**, tableau du contrat (lignes 5 à 7). Recopiez vers le bas.",
                     "Même chose pour l'ancienneté (lignes 11 à 14, colonne **F** des clients) et l'internet (lignes 18 à 20, colonne **C**)."],
                  [("B5", "=NB.SI(Clients!$D$5:$D$7047;A5)", "COUNTIF"),
                   ("C5", '=NB.SI.ENS(Clients!$D$5:$D$7047;A5;Clients!$E$5:$E$7047;"Yes")', "COUNTIFS"),
                   ("D5", "=C5/B5", None),
                   ("D23", '=NB.SI(Clients!$E$5:$E$7047;"Yes")/NBVAL(Clients!$E$5:$E$7047)', "COUNTA")]),
             ],
             "verifier": "Mensuel **42,7 %**, 1 an **11,3 %**, 2 ans **2,8 %** : 15 fois plus de départs sans engagement. Global : **26,5 %**."},
            {"titre": "Les trois graphiques", "onglet": "Analyse", "image": "G1-contrat.png", "images": ["G2-anciennete.png", "G3-internet.png"],
             "objectif": "Un histogramme par segment, avec le taux affiché sur chaque barre.",
             "points": [("3.1 Le graphique", [
                 "Sélectionnez **A4:A7**, maintenez **Ctrl**, sélectionnez **D4:D7** → **Insertion** → **Histogramme groupé**.",
                 "Bouton **+** → **Étiquettes de données**. Supprimez la légende. Barre la plus risquée en orange (clic, puis deuxième clic sur la barre).",
                 "Recommencez avec **A10:A14 + D10:D14** (ancienneté) et **A17:A20 + D17:D20** (internet)."], [])],
             "verifier": "Ancienneté : de **47,4 %** la première année à **9,5 %** au-delà de 4 ans. Fibre : **41,9 %**."},
        ],
        powerbi=[("clients.csv", "Histogramme groupé", "Axe X : `contrat` · Valeurs : `client` (Nombre) · Légende : `churn`, puis « Afficher en % du total de la catégorie »")]),

    "sql-musique": projet(
        "analyse-sql-ventes-musique", titre="Analyse SQL des ventes d'un magasin de musique", fichier="sql-musique", duree="1 h",
        outil="SQL + Excel", quoi="l'analyse",
        apprend=["DB Browser for SQLite (gratuit)", "jointures, GROUP BY, fonctions fenêtre", "coller un résultat SQL dans Excel", "barres horizontales", "un axe qui part de 0"],
        etapes=[
            {"titre": "Lancer les requêtes SQL", "onglet": "Requetes", "image": None,
             "objectif": "La base est un fichier SQLite. On l'interroge avec un outil gratuit, puis on récupère le résultat dans Excel.",
             "points": [("1.1 L'outil", [
                 "Installez **DB Browser for SQLite** (sqlitebrowser.org, gratuit, Windows et Mac).",
                 "Téléchargez `chinook.db` dans le dépôt GitHub du projet. Dans DB Browser : **Ouvrir une base de données** → `chinook.db`."], []),
                 ("1.2 Exécuter", [
                     "Onglet **Exécuter le SQL** → collez une requête de l'onglet **Requetes** du fichier Excel → **Ctrl + Entrée**.",
                     "Dans le résultat : **Ctrl + A** puis **Ctrl + C**. Dans Excel, cliquez en **A5** de l'onglet correspondant (Genres, Cumul, Clients) → **Ctrl + V**.",
                     "Pour le total du magasin, lancez aussi : `SELECT ROUND(SUM(Total), 2) FROM Invoice;` et collez le résultat en **G2** de l'onglet Genres."], [])],
             "verifier": "Onglet Genres : 10 lignes, le Rock en premier avec **826,65 €**. Total en G2 : **2 328,60 €**."},
            {"titre": "Le poids du Rock", "onglet": "Genres", "image": "G1-genres.png",
             "objectif": "Quelle part du chiffre d'affaires total fait chaque genre ? Le `$` bloque le total quand on recopie.",
             "points": [("2.1 La part", ["En **D5**, puis recopiez jusqu'à **D14**. Format **Pourcentage**."], [("D5", "=B5/$G$2", None)]),
                        ("2.2 Le graphique", ["Sélectionnez **A4:B14** → **Insertion** → **Barres groupées**.",
                                              "Clic droit sur l'axe des genres → **Mettre en forme l'axe** → **Catégories en ordre inverse** (le Rock passe en haut).",
                                              "Rock en orange, le reste en gris. Étiquettes de données."], [])],
             "verifier": "Le Rock pèse **35,5 %** du chiffre d'affaires à lui seul."},
            {"titre": "Le cumul et les meilleurs clients", "onglet": "Cumul et Clients", "image": "G2-cumul.png", "images": ["G3-clients.png"],
             "objectif": "Une courbe pour la tendance, des barres pour le classement, et un piège à éviter.",
             "points": [("3.1 La courbe", ["Onglet **Cumul** : sélectionnez **A4:A64**, Ctrl, **C4:C64** → **Insertion** → **Courbes**."], []),
                        ("3.2 Les clients et le piège de l'axe", [
                            "Onglet **Clients** : **A4:A14** + **C4:C14** → **Barres groupées**, catégories en ordre inverse.",
                            "Excel fait partir l'axe à 38 € : les écarts paraissent énormes alors qu'ils sont de quelques euros. Clic droit sur l'axe → **Minimum** = `0`."], [])],
             "verifier": "Cumul final : **2 328,60 €**. Avec l'axe à 0, on voit que les 10 meilleurs clients pèsent presque pareil (42 à 50 €)."},
        ],
        powerbi=[("genres.csv", "Graphique à barres groupées", "Axe Y : `genre` · Axe X : `ca_total`"),
                 ("cumul.csv", "Graphique en courbes", "Axe X : `mois` · Axe Y : `ca_cumule`")]),

    "scoring-b2b": projet(
        "scoring-prospects-b2b", titre="Scoring de propension B2B : qui appeler en premier ?", fichier="scoring-b2b", duree="20 min",
        apprend=["moyenne pondérée avec SOMMEPROD", "référence absolue $", "lire un lift"],
        etapes=[
            {"titre": "Le lift par décile", "onglet": "Deciles", "image": "G1-lift.png",
             "objectif": "Le modèle (en Python, dans le dépôt) a classé les prospects en 10 groupes. Le lift dit combien de fois chaque groupe convertit mieux que la moyenne.",
             "points": [("1.1 Le taux moyen", ["Moyenne pondérée par le nombre de prospects de chaque décile :"],
                         [("E2", "=SOMMEPROD(B5:B14;C5:C14)/SOMME(C5:C14)", "SUMPRODUCT")]),
                        ("1.2 Le lift", ["En **D5**, puis recopiez jusqu'à **D14**."], [("D5", "=B5/$E$2", None)]),
                        ("1.3 Le graphique", ["**A4:A14** + **D4:D14** (Ctrl) → **Histogramme groupé**. D1 et D2 en bleu (au-dessus de 1), le reste en gris. Étiquettes de données."], [])],
             "verifier": "Taux moyen **11,3 %**. D1 : lift **4,7** (les 10 % les mieux notés convertissent 4,7 fois plus). Dès D3, on passe sous 1."},
        ],
        powerbi=[("deciles.csv", "Histogramme groupé", "Axe X : `decile` · Axe Y : mesure DAX `Lift = AVERAGE(deciles[taux_conversion]) / 0.1127`")]),

    "ia-pme": projet(
        "adoption-ia-pme-france", titre="Adoption de l'IA par les entreprises françaises", fichier="ia-pme", duree="20 min",
        apprend=["histogramme groupé à plusieurs séries", "calcul d'écart en points", "Looker Studio (gratuit)"],
        etapes=[
            {"titre": "L'écart entre grandes et petites entreprises", "onglet": "Donnees", "image": "G1-adoption.png",
             "objectif": "Les PME rattrapent-elles les grands groupes ? On mesure l'écart en points de pourcentage.",
             "points": [("1.1 L'écart", ["En **B9**, recopiez vers C9 et D9."], [("B9", "=(B7-B5)*100", None)]),
                        ("1.2 Le graphique", ["Sélectionnez **A4:D7** → **Insertion** → **Histogramme groupé**. Excel fait une série par année.",
                                              "Couleurs du plus clair (2023) au plus foncé (2025). Étiquettes de données."], [])],
             "verifier": "Écart : **16** points en 2023, **24** en 2024, **43** en 2025. Il se creuse."},
            {"titre": "Le même graphique dans Looker Studio", "onglet": "csv/adoption_ia.csv", "image": None,
             "objectif": "Looker Studio est gratuit avec un compte Google. C'est l'outil du tableau de bord d'origine de ce projet.",
             "points": [("2.1 En ligne", ["lookerstudio.google.com → **Créer** → **Rapport** → **Importer un fichier** → `adoption_ia.csv`.",
                                          "**Ajouter un graphique** → **Histogramme**. Dimension : `taille`. Dimension de répartition : `annee`. Métrique : `part` (format %).",
                                          "Le tableau de bord d'origine : datastudio.google.com/reporting/80b607fa-71f1-461c-b5ae-30e91c213f86"], [])],
             "verifier": "Le même histogramme qu'Excel, partageable par un simple lien."},
        ],
        powerbi=[("adoption_ia.csv", "Histogramme groupé", "Axe X : `taille` · Légende : `annee` · Axe Y : `part`")]),

    "reporting-insee": projet(
        "automatisation-reporting-insee", titre="Automatisation d'un reporting Insee", fichier="reporting-insee", duree="30 min",
        apprend=["courbes avec marqueurs", "Power Query : un import qui s'actualise", "Actualiser tout"],
        etapes=[
            {"titre": "La progression de 2023 à 2025", "onglet": "Donnees", "image": "G1-evolution.png",
             "objectif": "Dans le projet, un robot télécharge et nettoie le fichier Insee chaque mois. Ici, on fait le graphique du reporting.",
             "points": [("1.1 La progression", ["En **B9**, recopiez vers C9 et D9."], [("B9", "=(B7-B5)*100", None)]),
                        ("1.2 Le graphique", ["**A4:D7** → **Insertion** → **Courbes avec marqueurs**. 250+ en orange. Étiquettes de données."], [])],
             "verifier": "Progression : **+10** points (10-49), **+21** (50-249), **+37** (250 et plus)."},
            {"titre": "Automatiser sans coder : Power Query", "onglet": "csv/adoption_ia.csv", "image": None,
             "objectif": "L'équivalent Excel du robot : un import qui se met à jour en un clic quand le fichier change.",
             "points": [("2.1 L'import", ["Classeur vide → **Données** → **À partir d'un fichier texte/CSV** → `adoption_ia.csv` → **Charger**.",
                                          "Faites le graphique à partir de ce tableau (étape 1.2)."], []),
                        ("2.2 La mise à jour", ["Remplacez le CSV par une version plus récente, même nom, même dossier.",
                                                "**Données** → **Actualiser tout** : le tableau et le graphique se mettent à jour seuls."], [])],
             "verifier": "Modifiez une valeur dans le CSV, actualisez : le graphique bouge sans rien refaire."},
        ],
        powerbi=[("adoption_ia.csv", "Graphique en courbes", "Axe X : `annee` · Légende : `taille` · Axe Y : `part` · puis **Actualiser** quand le fichier change")]),

    "ipc-france": projet(
        "analyse-ipc-france-covid", titre="Évolution des prix à la consommation en France", fichier="ipc-france", duree="40 min",
        apprend=["rebaser une série à 100", "référence mixte (B$17)", "déflater un salaire", "courbes sur 91 mois"],
        etapes=[
            {"titre": "Rebaser les prix à 100 en janvier 2020", "onglet": "Donnees", "image": "G1-prix.png",
             "objectif": "Les indices n'ont pas le même point de départ. On les ramène tous à 100 en janvier 2020 (ligne 17, en bleu clair) pour comparer leur évolution.",
             "points": [("1.1 La formule", ["En **F5**. Le `$` devant 17 bloque la ligne de janvier 2020, mais laisse la colonne libre.",
                                            "Recopiez vers la droite jusqu'à **H5** (alimentation, énergie), puis tout vers le bas jusqu'à la ligne 95."],
                         [("F5", "=B5/B$17*100", None)]),
                        ("1.2 Le graphique", ["**A4:A95** + **F4:H95** (Ctrl) → **Courbes**. Axe vertical : minimum 80."], [])],
             "verifier": "Ligne 17 : les trois valent **100**. En juillet 2026 : global **117,8**, alimentation **125,7**, énergie **143,3**."},
            {"titre": "Le Smic a-t-il suivi les prix ?", "onglet": "Donnees", "image": "G2-smic.png",
             "objectif": "Pouvoir d'achat = évolution du Smic divisée par évolution des prix. Au-dessus de 100, le Smic a gagné sur les prix.",
             "points": [("2.1 La formule", ["En **I5**, recopiez jusqu'à la ligne 95."], [("I5", "=(E5/E$17)/(B5/B$17)*100", None)]),
                        ("2.2 Le graphique", ["**A4:A95** + **I4:I95** → **Courbes**. Axe vertical : de 96 à 106."], [])],
             "verifier": "De **100,3** en janvier 2019 à **103,0** en juillet 2026 : le Smic a un peu gagné sur les prix."},
        ],
        powerbi=[("ipc_smic.csv", "Graphique en courbes", "Axe X : `mois` · Axe Y : `ipc_global`, `ipc_alimentation`, `ipc_energie` (rebaser avec une mesure DAX)")]),

    "cadrage-gantt": projet(
        "note-cadrage-scoring-ia-pme", titre="Note de cadrage : le planning en diagramme de Gantt", fichier="cadrage-gantt", duree="20 min",
        quoi="le planning du projet",
        apprend=["diagramme de Gantt dans Excel", "barres empilées", "série invisible", "axe en ordre inverse"],
        etapes=[
            {"titre": "Le diagramme de Gantt", "onglet": "Jalons", "image": "G1-gantt.png",
             "objectif": "Excel n'a pas de bouton « Gantt ». L'astuce : des barres empilées, dont la première (la semaine de début) est rendue invisible.",
             "points": [("1.1 La durée", ["En **D5**, recopiez jusqu'à **D10**. Le +1 compte la semaine de fin."], [("D5", "=C5-B5+1", None)]),
                        ("1.2 Les barres", ["Sélectionnez **A4:B10**, Ctrl, **D4:D10** → **Insertion** → **Barres empilées**."], []),
                        ("1.3 L'astuce", ["Clic sur la série « Semaine de début » → **Remplissage** → **Aucun remplissage**. Elle disparaît, les durées flottent au bon endroit.",
                                          "Axe des jalons : **Catégories en ordre inverse**. Axe des semaines : minimum 0, maximum 26, unité principale 2.",
                                          "Le bilan à 3 mois en orange : c'est le jalon isolé, loin après les autres."], [])],
             "verifier": "« Données consolidées » dure **3** semaines (S1 à S3). Le projet s'étale de S0 à S24."},
        ],
        powerbi=[("jalons.csv", "Graphique à barres empilées", "Axe Y : `jalon` · Axe X : `semaine_debut` (transparent) puis une mesure durée")]),

    "suivi-projet": projet(
        "suivi-projet-dashboard-kpi", titre="Suivre un projet après l'avoir cadré", fichier="suivi-projet", duree="30 min",
        quoi="le suivi du projet",
        apprend=["SI", "NB.SI, NBVAL, SOMME.SI", "indicateurs de pilotage", "histogramme prévu / réel"],
        etapes=[
            {"titre": "Les indicateurs de la semaine 14", "onglet": "Suivi", "image": None,
             "objectif": "Où en est le projet ? Combien de jalons finis, en retard, et le budget tient-il ?",
             "points": [("1.1 L'écart par jalon", ["En **E5**, recopiez jusqu'à **E10**. Si rien n'est encore dépensé, l'écart vaut 0."], [("E5", "=SI(D5=0;0;D5-C5)", "IF")]),
                        ("1.2 Les indicateurs", ["De **E14** à **E19** :"],
                         [("E14", '=NB.SI(B5:B10;"Terminé")', "COUNTIF"), ("E15", '=NB.SI(B5:B10;"En retard")', None),
                          ("E16", '=NB.SI(B5:B10;"Terminé")/NBVAL(B5:B10)', "COUNTA"), ("E17", '=SOMME.SI(D5:D10;">0";C5:C10)', "SUMIF"),
                          ("E18", "=SOMME(D5:D10)", "SUM"), ("E19", "=E18/E17-1", None)])],
             "verifier": "**3** jalons terminés, **1** en retard, avancement **50 %**, écart budgétaire **−1,9 %**."},
            {"titre": "Budget prévu contre réel", "onglet": "Suivi", "image": "G1-budget.png",
             "objectif": "Le −1,9 % global cache un dépassement : le graphique le montre.",
             "points": [("2.1 Le graphique", ["**A4:A10** + **C4:D10** (Ctrl) → **Histogramme groupé**. Prévu en gris, réel en bleu.",
                                              "La barre réelle de « Données consolidées » en orange : +15 % sur ce seul jalon."], [])],
             "verifier": "Données consolidées : **9 200 €** dépensés pour **8 000 €** prévus."},
        ],
        powerbi=[("suivi_jalons.csv", "Histogramme groupé", "Axe X : `jalon` · Axe Y : `budget_prevu` et `budget_reel`")]),
}
