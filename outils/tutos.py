"""
Écrit les tutoriels pas à pas de chaque étude, en deux versions identiques :
  - projets/<étude>/TUTO.md          (lisible sur GitHub et dans n'importe quel éditeur)
  - projets/<étude>-tuto.html        (la même chose, mise en page sur le site)
Les formules sont écrites pour Excel en français (séparateur « ; »), avec le nom anglais entre parenthèses.
Usage : python outils/tutos.py
"""
import html
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

COMMUN_DEBUT = [
    "Téléchargez le fichier **exercice** et ouvrez-le dans Excel. Les cellules **jaunes** sont à remplir, les graphiques sont à construire.",
    "Le fichier **corrigé** contient la version finie : c'est de là que viennent les graphiques du site. Ouvrez-le à côté pour comparer.",
    "Les formules sont écrites pour Excel en français : les arguments sont séparés par `;`. En anglais, remplacez `;` par `,` et utilisez le nom entre parenthèses.",
    "Recopier une formule vers le bas : sélectionnez la cellule, puis double-cliquez sur le petit carré en bas à droite.",
]
COMMUN_EXPORT = [
    "Cliquez sur le bord du graphique pour le sélectionner, puis clic droit → **Enregistrer en tant qu'image…** → format **PNG**.",
    "Pour une diapo : clic droit → **Copier**, puis **Collage spécial → Image** dans PowerPoint.",
]
COULEURS = "Les couleurs du portfolio : bleu `#1F3864`, orange `#D9542B`, gris `#8FA0C2`. Pour les appliquer : clic droit sur une série → **Mettre en forme une série de données** → pot de peinture **Remplissage et trait** → **Remplissage uni** → **Couleur** → **Autres couleurs** → onglet **Personnalisées** → champ **Hex**."

TUTOS = {
    "ufc-paris": {
        "titre": "Le bookmaker gagne toujours. Même au MMA.",
        "fichier": "ufc-paris",
        "duree": "1 h 30 environ",
        "apprend": ["formules simples et recopie", "SIERREUR, SOMME, COEFFICIENT.CORRELATION", "histogramme empilé", "colorier une seule barre",
                    "nuage de points avec une 2ᵉ série", "barres d'erreur personnalisées", "simulation avec ALEA.ENTRE.BORNES et INDEX", "Power BI : import CSV"],
        "etapes": [
            {"titre": "Où va l'argent des paris sportifs", "onglet": "Argent", "image": "G1-argent.png",
             "objectif": "Calculer ce qui revient aux parieurs et ce que gardent les opérateurs, puis le montrer en histogramme empilé.",
             "points": [
                 ("1.1 Revenu aux parieurs", ["En **D5**, tapez la formule ci-dessous, puis recopiez-la jusqu'à **D20**."], [("D5", "=B5-C5", None)]),
                 ("1.2 Part gardée", ["En **E5**, la part de chaque euro misé que gardent les opérateurs. SIERREUR évite une erreur si la mise vaut 0.",
                                      "Recopiez jusqu'à **E20**, et mettez la colonne au format **Pourcentage** (Accueil → Nombre → %)."],
                  [("E5", "=SIERREUR(C5/B5;0)", "IFERROR")]),
                 ("1.3 En milliards, pour le graphique", ["En **F5** et **G5**, divisez par 1 000. Recopiez jusqu'à la ligne 20."],
                  [("F5", "=D5/1000", None), ("G5", "=C5/1000", None)]),
                 ("1.4 Les totaux et la corrélation", ["Ligne 21 : les totaux. Recopiez la formule de B21 vers C21 et D21.", "En **E23**, la corrélation entre les mises et l'argent gardé."],
                  [("B21", "=SOMME(B5:B20)", "SUM"), ("E21", "=C21/B21", None), ("E23", "=COEFFICIENT.CORRELATION(B5:B20;C5:C20)", "CORREL")]),
                 ("1.5 Le graphique", ["Sélectionnez **A4:A20**, puis maintenez **Ctrl** et sélectionnez **F4:G20**.",
                                       "**Insertion** → **Graphiques** → icône histogramme → **Histogramme empilé**.",
                                       "Couleurs : « Revenu » en bleu, « Gardé » en orange. Dans **Options des séries**, mettez **Largeur de l'intervalle** à 55 %.",
                                       "Cliquez sur le titre pour l'écrire. Bouton **+** à côté du graphique → **Légende** → **En bas**."], []),
             ],
             "verifier": "Total misé en B21 : **70 517** M€. Part gardée en E21 : **16,9 %**. Corrélation en E23 : **0,997**."},
            {"titre": "La popularité du MMA", "onglet": "Evenements", "image": "G2-evenements.png",
             "objectif": "Un histogramme simple, avec les années où le MMA est légal en France mises en avant.",
             "points": [
                 ("2.1 Le graphique", ["Sélectionnez **A4:B29** → **Insertion** → **Histogramme groupé**. Supprimez la légende (cliquez dessus, touche **Suppr**).",
                                       "Mettez toute la série en gris `#8FA0C2`."], []),
                 ("2.2 Colorier une seule barre", ["Cliquez une fois sur une barre : toute la série est sélectionnée. **Cliquez une deuxième fois** sur la barre 2020 : elle seule reste sélectionnée.",
                                                   "Clic droit → **Mettre en forme le point de données** → orange `#D9542B`. Recommencez pour 2021 à 2025."], []),
             ],
             "verifier": "Les barres 2020 à 2025 sont orange, toutes autour de 42 événements par an."},
            {"titre": "Les bookmakers voient-ils juste ?", "onglet": "Calibration", "image": "G3-calibration.png",
             "objectif": "Comparer la probabilité annoncée par la cote au taux de victoire réel, avec une diagonale « cote parfaite ».",
             "points": [
                 ("3.1 La diagonale", ["En **D5**, recopiez simplement la probabilité annoncée. Recopiez jusqu'à **D12**."], [("D5", "=A5", None)]),
                 ("3.2 Le nuage de points", ["Sélectionnez **A4:B12** → **Insertion** → **Nuage de points (X, Y)** → **Nuage de points avec lignes droites et marqueurs**."], []),
                 ("3.3 Ajouter la diagonale", ["Clic droit sur le graphique → **Sélectionner des données** → **Ajouter**.",
                                               "Nom : `Cote parfaite`. Valeurs X : **A5:A12**. Valeurs Y : **D5:D12**. OK.",
                                               "Mettez cette série en pointillés gris, sans marqueurs (**Remplissage et trait** → **Trait** → **Type de tiret**, puis **Marqueur** → **Aucun**).",
                                               "Clic droit sur chaque axe → **Mettre en forme l'axe** → Minimum 0, Maximum 1, Nombre au format **Pourcentage**."], []),
             ],
             "verifier": "Les points orange suivent la diagonale à quelques points près : les cotes sont justes."},
            {"titre": "Ce que rapporte 1 € misé", "onglet": "Rendement", "image": "G4-rendement.png",
             "objectif": "Un histogramme avec des valeurs négatives, des couleurs selon le résultat, et la marge d'erreur.",
             "points": [
                 ("4.1 Le graphique", ["Sélectionnez **A4:B10** → **Insertion** → **Histogramme groupé**. Supprimez la légende.",
                                       "Clic droit sur l'axe horizontal → **Mettre en forme l'axe** → **Étiquettes** → Position **Bas** : les noms de tranches passent sous le graphique."], []),
                 ("4.2 Les couleurs", ["Comme à l'étape 2.2 : barre « < 1,30 » en bleu, « 1,30-1,60 », « 1,60-2 » et « 2-3 » en gris, « 3-5 » et « > 5 » en orange."], []),
                 ("4.3 Les barres d'erreur", ["Bouton **+** → **Barres d'erreur** → **Autres options**.",
                                              "**Valeur d'erreur** → **Personnalisée** → **Spécifier une valeur**.",
                                              "Valeur positive : sélectionnez **C5:C10**. Valeur négative : sélectionnez **C5:C10** aussi."], []),
             ],
             "verifier": "La barre « > 5 » descend à **−30 %**. La barre « < 1,30 » est à +1,6 %, mais sa barre d'erreur passe sous zéro : le gain n'est pas sûr."},
            {"titre": "Le simulateur de parieur", "onglet": "Simulateur", "image": "G5-simulateur.png",
             "objectif": "Simuler 100 paris sur de vrais combats tirés au hasard. Chaque appui sur F9 crée un nouveau parieur.",
             "points": [
                 ("5.1 Tirer un combat au hasard", ["L'onglet **Combats** contient 6 916 combats, des lignes 5 à 6920. En **B7** :"],
                  [("B7", "=ALEA.ENTRE.BORNES(5;6920)", "RANDBETWEEN")]),
                 ("5.2 Choisir un camp", ["Une chance sur deux pour chaque camp :"], [("C7", '=SI(ALEA()<0,5;"rouge";"bleu")', "IF, RAND")]),
                 ("5.3 Aller chercher la cote et le résultat", ["INDEX va lire la cellule de la ligne tirée dans l'onglet Combats."],
                  [("D7", '=SI(C7="rouge";INDEX(Combats!A:A;B7);INDEX(Combats!B:B;B7))', "INDEX"),
                   ("E7", '=SI(C7="rouge";INDEX(Combats!C:C;B7)=1;INDEX(Combats!C:C;B7)=0)', None)]),
                 ("5.4 Le gain et la cagnotte", ["Le `$` bloque la référence à la mise quand on recopie (touche **F4** pour l'ajouter).",
                                                 "Recopiez **B7:H7** jusqu'à la ligne **106**, puis en **F4** affichez le bilan."],
                  [("F7", "=SI(E7;$C$4*(D7-1);-$C$4)", None), ("H7", "=H6+F7", None), ("F4", "=H106", None)]),
                 ("5.5 La courbe", ["Sélectionnez **H5:H106** → **Insertion** → **Courbes**. Couleur orange.",
                                    "Appuyez sur **F9** : tout est retiré au hasard, la courbe change. Comptez combien de fois vous finissez au-dessus de zéro."], []),
             ],
             "verifier": "Sur 10 appuis sur F9, vous devriez finir positif environ 3 fois. C'est le chiffre de l'étude : 31 % de gagnants."},
            {"titre": "La calculatrice de marge", "onglet": "Calculatrice", "image": "calculatrice.png",
             "objectif": "Retrouver la marge du bookmaker à partir de deux cotes. Une cote, c'est une probabilité déguisée : 1 / cote.",
             "points": [
                 ("6.1 Les formules", ["Les cellules **B4** et **B5** (jaunes vives) contiennent les deux cotes. Tout le reste en découle."],
                  [("B7", "=1/B4", None), ("B8", "=1/B5", None), ("B9", "=B7+B8", None), ("B10", "=B9-1", None), ("B11", "=100*B10/B9", None)]),
                 ("6.2 Jouer avec", ["Mettez B7 à B10 au format **Pourcentage**. Changez les cotes : avec 1,90 et 1,90, la marge tombe à 5,3 %."], []),
             ],
             "verifier": "Avec 1,77 et 2,02 : total **106,0 %**, marge **6,0 %**, le bookmaker garde **5,66 €** sur 100 €."},
            {"titre": "1 000 parieurs simulés dans Excel", "onglet": "Paris, 1000 parieurs, Distribution", "image": "G6-distribution.png",
             "objectif": "Simuler 1 000 parieurs qui font chacun 100 paris de 10 €, puis compter combien finissent gagnants. C'est une simulation de Monte-Carlo, entièrement en formules.",
             "points": [
                 ("7.1 Le gain de chaque pari possible", ["Onglet **Paris** : chaque camp de chaque combat est un pari possible (13 832 lignes). En **C5**, puis double-clic pour recopier :"],
                  [("C5", "=SI(B5=1;10*(A5-1);-10)", "IF")]),
                 ("7.2 Tirer 100 paris par parieur", ["Onglet **1000 parieurs** : en **B5**, un pari tiré au hasard. Recopiez vers la droite jusqu'à **CW5** (100 colonnes), puis vers le bas jusqu'à la ligne **1004**.",
                                                     "En **CX5**, le bilan du parieur, recopié jusqu'en bas. Excel recalcule 100 000 tirages : c'est normal que ça prenne une seconde."],
                  [("B5", "=INDEX(Paris!$C$5:$C$13836;ALEA.ENTRE.BORNES(1;13832))", "INDEX, RANDBETWEEN"), ("CX5", "=SOMME(B5:CW5)", "SUM")]),
                 ("7.3 Compter et tracer", ["Onglet **Distribution** : on compte les parieurs dans chaque tranche de 50 €. Recopiez C5 jusqu'à C26.",
                                            "Puis l'histogramme : sélectionnez **A4:A26** et **C4:C26** (Ctrl) → **Histogramme groupé**. Tranches négatives en orange, positives en bleu (étape 2.2). Largeur de l'intervalle : 15 %."],
                  [("C5", "=NB.SI.ENS('1000 parieurs'!$CX$5:$CX$1004;\">=\"&A5;'1000 parieurs'!$CX$5:$CX$1004;\"<\"&B5)", "COUNTIFS"),
                   ("C28", "=NB.SI('1000 parieurs'!CX5:CX1004;\">0\")/1000", "COUNTIF"), ("C29", "=MEDIANE('1000 parieurs'!CX5:CX1004)", "MEDIAN")]),
             ],
             "verifier": "Entre **27 et 35 %** de gagnants selon le tirage (F9 pour relancer). Le chiffre de l'étude, 31 %, est la moyenne sur 10 000 parieurs."},
        ],
        "powerbi": [
            ("argent.csv", "Histogramme empilé", "Axe X : `annee` · Axe Y : `redistribue_meur` puis `garde_meur`"),
            ("evenements_ufc.csv", "Histogramme groupé", "Axe X : `annee` · Axe Y : `evenements`"),
            ("calibration.csv", "Nuage de points", "Axe X : `proba_annoncee` · Axe Y : `taux_victoire_reel` · Taille : `combattants`"),
            ("rendement_par_cote.csv", "Histogramme groupé", "Axe X : `tranche_cote` · Axe Y : `rendement` (format %)"),
        ],
    },
    "nba-mi-distance": {
        "titre": "Le tir que la NBA a arrêté de financer",
        "fichier": "nba-mi-distance",
        "duree": "1 h environ",
        "apprend": ["additionner des colonnes", "graphique en courbes à plusieurs séries", "barres horizontales comparées",
                    "SOMMEPROD : la décomposition mix / performance", "« Inverser si négatif » pour colorer les barres", "carte de chaleur avec la mise en forme conditionnelle", "Power BI : import CSV"],
        "etapes": [
            {"titre": "Le budget change de canal", "onglet": "Parts", "image": "G1-parts.png",
             "objectif": "Regrouper les 5 zones en 3 grandes zones, puis tracer leur évolution sur 22 saisons.",
             "points": [
                 ("1.1 Les grandes zones", ["En **G5**, **H5** et **I5**, puis recopiez les trois jusqu'à la ligne **26**."],
                  [("G5", "=B5+C5", None), ("H5", "=E5+F5", None), ("I5", "=D5", None)]),
                 ("1.2 Le graphique", ["Sélectionnez **A4:A26**, maintenez **Ctrl** et sélectionnez **G4:I26**.",
                                       "**Insertion** → **Courbes**. Couleurs : « Près du panier » en gris pointillé, « 3 points » en bleu, « Mi-distance » en orange, épaisseur 2,75 pt.",
                                       "Axe vertical : Minimum 0, Maximum 0,55, format %."], []),
             ],
             "verifier": "Les courbes orange et bleue se croisent en 2014-15. Le mi-distance finit à **9,8 %**."},
            {"titre": "Cinq canaux, cinq rendements", "onglet": "Rendement", "image": "G2-rendement.png",
             "objectif": "Comparer le rendement de chaque zone entre la première et la dernière saison.",
             "points": [
                 ("2.1 Le petit tableau", ["En **H4:J9** : une ligne par zone, la première saison (ligne 5) et la dernière (ligne 26).",
                                           "Même logique pour chaque zone, en changeant de colonne : Raquette = colonne C, Mi-distance = D, coin = E, axe = F."],
                  [("I5", "=B5", None), ("J5", "=B26", None), ("I6", "=C5", None), ("J6", "=C26", None)]),
                 ("2.2 Le graphique", ["Sélectionnez **H4:J9** → **Insertion** → **Barres groupées**.",
                                       "Clic droit sur l'axe des zones → **Mettre en forme l'axe** → cochez **Catégories en ordre inverse**.",
                                       "2003-04 en gris, 2024-25 en orange. Sur la série orange : bouton **+** → **Étiquettes de données**."], []),
             ],
             "verifier": "Mi-distance : **0,83** point par tir, contre **1,16** pour le 3 points dans le coin."},
            {"titre": "Mieux tirer, ou tirer au bon endroit ?", "onglet": "Decomposition", "image": None,
             "objectif": "Séparer deux effets : les joueurs sont plus adroits (effet adresse), ou ils tirent depuis de meilleures zones (effet mix). C'est la même méthode qu'en analyse de mix marketing.",
             "points": [
                 ("3.1 Rapatrier les chiffres", ["Ligne 5 (Sous le panier) : parts et rendements de la première et de la dernière saison.",
                                                 "Lignes 6 à 9 : même chose en décalant d'une colonne (C, D, E, F)."],
                  [("B5", "=Parts!B5", None), ("C5", "=Parts!B26", None), ("D5", "=Rendement!B5", None), ("E5", "=Rendement!B26", None)]),
                 ("3.2 SOMMEPROD", ["SOMMEPROD multiplie deux colonnes ligne par ligne, puis additionne. Part × rendement, zone par zone = rendement global."],
                  [("B12", "=SOMMEPROD(B5:B9;D5:D9)", "SUMPRODUCT"), ("B13", "=SOMMEPROD(C5:C9;E5:E9)", None), ("B14", "=B13-B12", None)]),
                 ("3.3 Les trois effets", ["Effet mix : nouvelle répartition, ancienne adresse. Effet adresse : ancienne répartition, nouvelle adresse."],
                  [("B15", "=SOMMEPROD(C5:C9-B5:B9;D5:D9)", None), ("B16", "=SOMMEPROD(B5:B9;E5:E9-D5:D9)", None),
                   ("B17", "=SOMMEPROD(C5:C9-B5:B9;E5:E9-D5:D9)", None), ("B18", "=B15/B14", None), ("B19", "=ARRONDI(B15+B16+B17-B14;10)", "ROUND")]),
             ],
             "verifier": "B15 (effet mix) ≈ **0,054** et B18 ≈ **37 %**. B19 doit afficher **0** : les trois effets additionnés redonnent la hausse totale."},
            {"titre": "Quand tout le monde quitte un canal", "onglet": "Correlation", "image": "G3-correlation.png",
             "objectif": "Un histogramme avec les valeurs négatives et positives de couleurs différentes, en une seule manipulation.",
             "points": [
                 ("4.1 Le graphique", ["Sélectionnez **A4:B26** → **Insertion** → **Histogramme groupé**. Supprimez la légende.",
                                       "Clic droit sur l'axe horizontal → **Mettre en forme l'axe** → **Étiquettes** → Position **Bas**."], []),
                 ("4.2 « Inverser si négatif »", ["Clic droit sur les barres → **Mettre en forme une série de données** → **Remplissage uni**, couleur orange.",
                                                  "Cochez **Inverser si négatif** : une deuxième couleur apparaît, choisissez le bleu. Les barres sous zéro passent en bleu."], []),
             ],
             "verifier": "Bleu jusqu'en 2019-20 environ, puis des barres orange : le lien s'inverse."},
            {"titre": "La carte du terrain", "onglet": "Terrain 2004 et Terrain 2025", "image": None,
             "objectif": "Transformer un tableau de chiffres en carte de chaleur : on voit d'où les joueurs tirent.",
             "points": [
                 ("5.1 Mise en forme conditionnelle", ["Sélectionnez **B5:Z20**.",
                                                       "**Accueil** → **Mise en forme conditionnelle** → **Nuances de couleurs** → **Autres règles**.",
                                                       "Style : **Échelle à trois couleurs**. Minimum : Nombre `0`, blanc. Point milieu : Nombre `10`, `#F4B183`. Maximum : Nombre `40`, `#C0392B`.",
                                                       "Pourquoi un maximum fixe à 40 et pas « valeur la plus élevée » ? Pour que les deux saisons aient la même échelle de couleurs. Sinon, la comparaison ment.",
                                                       "Faites pareil sur l'autre onglet, puis comparez les deux : la zone entre la raquette et la ligne à 3 points se vide."], []),
             ],
             "verifier": "En 2025, les cases rouges sont sous le panier et sur la ligne à 3 points. Presque plus rien entre les deux.",
             "images": ["terrain-2004.png", "terrain-2025.png"]},
        ],
        "powerbi": [
            ("parts_par_zone.csv", "Graphique en courbes", "Axe X : `saison` · Axe Y : `Mi-distance`, `3 pts dans le coin`, `3 pts dans l'axe`"),
            ("rendement_par_zone.csv", "Graphique à barres groupées", "Filtrez les saisons 2003-04 et 2024-25, puis zones en axe"),
            ("correlation_equipes.csv", "Histogramme groupé", "Axe X : `saison` · Axe Y : `correlation`"),
            ("terrain.csv", "Nuage de points", "Axe X : `x_pieds` · Axe Y : `y_pieds` · Taille : `part_des_tirs` · Axe de lecture : `saison` (le terrain s'anime)"),
        ],
    },
}


def md_inline(t):
    return t


def html_inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    return t


def ecrire_md(cle, T):
    x = f"excel/{T['fichier']}"
    L = [f"# Tuto : {T['titre']}", "",
         f"Refaire tous les graphiques de l'étude dans Excel, étape par étape. Durée : {T['duree']}.", "",
         "**Les fichiers**", "",
         f"- [`{x}-exercice.xlsx`]({x}-exercice.xlsx) : les données, rien n'est fait. C'est celui-là qu'on remplit.",
         f"- [`{x}-corrige.xlsx`]({x}-corrige.xlsx) : la version finie, celle des graphiques du site.",
         "- [`excel/csv/`](excel/csv) : les mêmes données en CSV, pour Power BI.",
         "- [`excel/graphiques/`](excel/graphiques) : les graphiques exportés depuis le corrigé.", "",
         *([f"Le projet d'origine : {T['depot']}", ""] if T.get("depot") else []),
         "**Ce que vous allez pratiquer** : " + " · ".join(T["apprend"]) + ".", "",
         "## Avant de commencer", ""] + [f"- {l}" for l in COMMUN_DEBUT] + ["", f"> {COULEURS}", ""]
    for n, e in enumerate(T["etapes"], 1):
        L += [f"## Étape {n} : {e['titre']}", "", f"*Onglet : {e['onglet']}.* {e['objectif']}", ""]
        for sous, lignes, formules in e["points"]:
            L += [f"### {sous}", ""] + [f"- {l}" for l in lignes] + [""]
            if formules:
                L += ["| Cellule | Formule (Excel en français) | En anglais |", "|---|---|---|"]
                L += [f"| {c} | `{f}` | {en or '—'} |" for c, f, en in formules] + [""]
        L += [f"**✅ Vérifiez :** {e['verifier']}", ""]
        for im in ([e["image"]] if e["image"] else []) + e.get("images", []):
            L += [f"![Résultat attendu](excel/graphiques/{im})", ""]
    L += ["## Exporter un graphique", ""] + [f"- {l}" for l in COMMUN_EXPORT] + [""]
    L += ["## La même chose dans Power BI", "",
          "**Accueil** → **Obtenir des données** → **Texte/CSV** → choisissez le fichier → vérifiez que le délimiteur est **Point-virgule** → **Charger**.", "",
          "| Fichier | Visuel | Champs |", "|---|---|---|"]
    L += [f"| `{f}` | {v} | {c} |" for f, v, c in T["powerbi"]] + [""]
    L += ["Si les décimales s'affichent mal : **Transformer les données** → sélectionnez la colonne → **Type de données** → **Nombre décimal** → **Utilisation des paramètres régionaux** → Anglais (États-Unis).", ""]
    (RACINE / "projets" / cle / "TUTO.md").write_text("\n".join(L))


def ecrire_html(cle, T):
    x = f"{cle}/excel/{T['fichier']}"
    corps = []
    corps.append(f'''<div class="tuto-files">
      <a class="tool-file" href="{x}-exercice.xlsx" download><b>Exercice</b><span>{T['fichier']}-exercice.xlsx, les données, rien n'est fait</span></a>
      <a class="tool-file" href="{x}-corrige.xlsx" download><b>Corrigé</b><span>{T['fichier']}-corrige.xlsx, la version finie, celle du site</span></a>
      <a class="tool-file" href="https://github.com/ATEYABA-K/ATEYABA-K.github.io/tree/main/projets/{cle}/excel/csv" target="_blank" rel="noopener"><b>CSV pour Power BI</b><span>un fichier par graphique ↗</span></a>
    </div>
    <p class="tuto-learn"><b>Ce que vous allez pratiquer :</b> {html_inline(" · ".join(T["apprend"]))}.</p>
    <h2 class="h"><span class="step">00 · Avant de commencer</span>Trois réglages</h2>
    <ul class="plain">{"".join(f"<li>{html_inline(l)}</li>" for l in COMMUN_DEBUT)}</ul>
    <div class="callout"><p>{html_inline(COULEURS)}</p></div>''')
    for n, e in enumerate(T["etapes"], 1):
        bloc = [f'<h2 class="h" id="etape-{n}"><span class="step">{n:02d} · Onglet {html.escape(e["onglet"])}</span>{html.escape(e["titre"])}</h2>',
                f"<p>{html_inline(e['objectif'])}</p>"]
        for sous, lignes, formules in e["points"]:
            bloc.append(f'<h3 class="tuto-sub">{html.escape(sous)}</h3><ol class="tuto-steps">{"".join(f"<li>{html_inline(l)}</li>" for l in lignes)}</ol>')
            if formules:
                rows = "".join(f'<tr><td class="mono">{c}</td><td><code>{html.escape(f)}</code></td><td>{en or "—"}</td></tr>' for c, f, en in formules)
                bloc.append(f'<div class="tuto-table"><table><thead><tr><th>Cellule</th><th>Formule (Excel en français)</th><th>En anglais</th></tr></thead><tbody>{rows}</tbody></table></div>')
        bloc.append(f'<p class="tuto-check">✅ <b>Vérifiez :</b> {html_inline(e["verifier"])}</p>')
        for im in e.get("images", []):
            bloc.append(f'<figure class="chart xl"><img src="{cle}/excel/graphiques/{im}" alt="Résultat attendu" loading="lazy"><p class="src">Résultat attendu, exporté du fichier corrigé.</p></figure>')
        if e["image"]:
            bloc.append(f'<figure class="chart xl"><img src="{cle}/excel/graphiques/{e["image"]}" alt="Résultat attendu : {html.escape(e["titre"])}" loading="lazy"><p class="src">Résultat attendu, exporté du fichier corrigé.</p></figure>')
        corps.append("\n".join(bloc))
    corps.append(f'''<h2 class="h"><span class="step">Bonus</span>Exporter un graphique</h2>
    <ul class="plain">{"".join(f"<li>{html_inline(l)}</li>" for l in COMMUN_EXPORT)}</ul>
    <h2 class="h"><span class="step">Bonus</span>La même chose dans Power BI</h2>
    <p><strong>Accueil</strong> → <strong>Obtenir des données</strong> → <strong>Texte/CSV</strong> → choisissez le fichier → délimiteur <strong>Point-virgule</strong> → <strong>Charger</strong>.</p>
    <div class="tuto-table"><table><thead><tr><th>Fichier</th><th>Visuel</th><th>Champs</th></tr></thead><tbody>
    {"".join(f"<tr><td><a href='{cle}/excel/csv/{f}' download><code>{f}</code></a></td><td>{v}</td><td>{html_inline(c)}</td></tr>" for f, v, c in T["powerbi"])}
    </tbody></table></div>
    <p style="color:var(--ink-soft); font-size:.92rem">Si les décimales s'affichent mal : <strong>Transformer les données</strong> → colonne → <strong>Type de données</strong> → <strong>Nombre décimal</strong> → <strong>Utilisation des paramètres régionaux</strong> → Anglais (États-Unis).</p>''')
    page = f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tuto Excel · {html.escape(T["titre"])} · Alvin Kouadio</title>
<meta name="description" content="Refaire pas à pas dans Excel tous les graphiques de l'étude « {html.escape(T['titre'])} » : fichier exercice, corrigé, formules et Power BI.">
<meta name="theme-color" content="#14171c">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='32' fill='%231F3864'/%3E%3Ctext x='32' y='42' font-family='Georgia,serif' font-size='28' fill='white' text-anchor='middle'%3EAK%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400;1,9..144,600&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/style.css">
<script>try{{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
</head>
<body>
<div class="progress-read" aria-hidden="true"></div>
<canvas id="bg" aria-hidden="true"></canvas>
<div class="topbar">
  <div class="wrap">
    <a class="brand" href="../index.html">Alvin Kouadio<span>.</span></a>
    <div class="nav-right"><nav class="nav-links">
      <a href="../index.html#projets">Projets</a>
      <a href="../maintenant.html">Maintenant</a>
      <a href="../index.html#contact">Contact</a>
    </nav>
    {(RACINE / "outils/bouton-theme.html").read_text().strip()}</div>
  </div>
</div>
<div class="wrap">
<article class="article">
  <a class="back" href="{T.get('retour', cle + '.html')}">← {T.get('retour_label', "Retour à l'étude")}</a>
  <p class="eyebrow"><b>Tuto {T.get('outil', 'Excel')}</b> · {T["duree"]}</p>
  <h1>Refaire {T.get('quoi', "l'étude")} <em class="mark">dans {T.get('outil', 'Excel')}.</em></h1>
  <p class="kicker">« {html.escape(T["titre"])} » : chaque graphique de l'étude, clic par clic, avec les formules. Ouvrez l'exercice et suivez.</p>
  {"".join(corps)}
</article>
  <footer>
    <span>Alvin Kouadio · Nanterre, Île-de-France</span>
    <span><a href="{T.get('retour', cle + '.html')}">{T.get('retour_label', "Retour à l'étude")}</a></span>
  </footer>
</div>
<script src="../assets/fond.js"></script>
<script src="../assets/site.js"></script>
</body>
</html>
'''
    (RACINE / "projets" / f"{cle}-tuto.html").write_text(page)


from tutos_projets import TUTOS_PROJETS  # noqa: E402

TUTOS.update(TUTOS_PROJETS)

if __name__ == "__main__":
    for cle, T in TUTOS.items():
        ecrire_md(cle, T)
        ecrire_html(cle, T)
        print(cle, "ok")
