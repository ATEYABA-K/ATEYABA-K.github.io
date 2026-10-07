"""
Le mi-distance, ou comment la NBA a coupé son canal le moins rentable.

Chaque tir est traité comme un investissement : une possession dépensée, des points rapportés.
On mesure le rendement de chaque zone du terrain, saison par saison, puis on décompose
la hausse d'efficacité de la ligue entre "on tire mieux" et "on tire au bon endroit".

Données : tous les tirs de saison régulière NBA, 2003-04 à 2024-25 (source NBA.com),
compilés par le dépôt public DomSamangy/NBA_Shots_04_25.

Usage : python analyse.py   -> écrit resultats.json et terrain.json à côté du script.
"""
import io
import json
import zipfile
from pathlib import Path
from urllib.request import urlopen

import numpy as np
import pandas as pd

SOURCE = "https://raw.githubusercontent.com/DomSamangy/NBA_Shots_04_25/main/NBA_{}_Shots.csv.zip"
SAISONS = range(2004, 2026)  # 2004 = saison 2003-04
ICI = Path(__file__).parent
CACHE = ICI / "donnees"  # téléchargées une fois, ignorées par git

ZONES = {  # zone officielle NBA -> nos 5 "canaux"
    "Restricted Area": "Sous le panier",
    "In The Paint (Non-RA)": "Raquette",
    "Mid-Range": "Mi-distance",
    "Left Corner 3": "3 pts dans le coin",
    "Right Corner 3": "3 pts dans le coin",
    "Above the Break 3": "3 pts dans l'axe",
}
ORDRE = ["Sous le panier", "Raquette", "Mi-distance", "3 pts dans le coin", "3 pts dans l'axe"]
COLONNES = ["SEASON_1", "TEAM_NAME", "SHOT_MADE", "SHOT_TYPE", "BASIC_ZONE", "LOC_X", "LOC_Y"]


def charger(annee):
    CACHE.mkdir(exist_ok=True)
    fichier = CACHE / f"NBA_{annee}_Shots.csv.zip"
    if not fichier.exists():
        fichier.write_bytes(urlopen(SOURCE.format(annee)).read())
    with zipfile.ZipFile(fichier) as z:
        nom = next(n for n in z.namelist() if n.endswith(".csv") and not n.startswith("__MACOSX"))
        return pd.read_csv(z.open(nom), usecols=COLONNES)


tirs = pd.concat([charger(a) for a in SAISONS], ignore_index=True)
tirs = tirs[tirs.BASIC_ZONE.isin(ZONES)]  # on écarte les tirs du milieu de terrain (fin de quart-temps)
tirs["zone"] = tirs.BASIC_ZONE.map(ZONES)
tirs["points"] = np.where(tirs.SHOT_MADE, np.where(tirs.SHOT_TYPE.str.startswith("3"), 3, 2), 0)
tirs = tirs.rename(columns={"SEASON_1": "saison", "TEAM_NAME": "equipe"})
print(f"{len(tirs):,} tirs chargés")

# 1. Part de chaque zone et rendement (points par tir), saison par saison ----
par_zone = tirs.groupby(["saison", "zone"]).agg(tirs=("points", "size"), points=("points", "sum"))
par_zone["part"] = par_zone.tirs / par_zone.groupby(level="saison").tirs.transform("sum")
par_zone["rendement"] = par_zone.points / par_zone.tirs
part = par_zone.part.unstack()[ORDRE]
rendement = par_zone.rendement.unstack()[ORDRE]
global_ = tirs.groupby("saison").points.mean()

# 2. Décomposition : mieux tirer, ou tirer au bon endroit ? ---------------
# Effet mix = on garde l'adresse de 2004 et on applique la répartition de 2025.
# Effet adresse = on garde la répartition de 2004 et on applique l'adresse de 2025.
a, b = SAISONS[0], SAISONS[-1]
effet_mix = float(((part.loc[b] - part.loc[a]) * rendement.loc[a]).sum())
effet_adresse = float((part.loc[a] * (rendement.loc[b] - rendement.loc[a])).sum())
interaction = float(((part.loc[b] - part.loc[a]) * (rendement.loc[b] - rendement.loc[a])).sum())
hausse = float(global_.loc[b] - global_.loc[a])

# 3. Équipes : moins de mi-distance = meilleur rendement ? -----------------
equipes = tirs.groupby(["saison", "equipe"]).agg(
    mi_distance=("zone", lambda z: (z == "Mi-distance").mean()), rendement=("points", "mean"))
correlation = equipes.groupby("saison").apply(lambda g: g.mi_distance.corr(g.rendement)).round(2)
pionnier = equipes.mi_distance.groupby("saison").idxmin().map(lambda x: x[1])

# 4. Grille du terrain pour la carte interactive ---------------------------
# Cases de 2 pieds sur la moitié de terrain utile (jusqu'à 32 pieds du fond).
dans = tirs[(tirs.LOC_Y < 32) & (tirs.LOC_X.abs() < 25)].copy()
dans["cx"] = ((dans.LOC_X + 25) // 2).astype(int)
dans["cy"] = (dans.LOC_Y // 2).astype(int)
grille = dans.groupby(["saison", "cy", "cx"]).agg(n=("points", "size"), pts=("points", "sum")).reset_index()
grille["part"] = grille.n / grille.groupby("saison").n.transform("sum")
terrain = {
    "cellule_pieds": 2, "colonnes": 25, "lignes": 16,
    "saisons": {int(s): [[int(r.cy), int(r.cx), round(r.part * 1000, 2), round(r.pts / r.n, 2)]
                         for r in g.itertuples() if r.n >= 30]
                for s, g in grille.groupby("saison")},
}

saison = lambda s: f"{s - 1}-{str(s)[2:]}"
sortie = {
    "periode": f"{saison(a)} à {saison(b)}",
    "tirs": int(len(tirs)),
    "part_par_zone": {saison(s): part.loc[s].round(3).to_dict() for s in SAISONS},
    "rendement_par_zone": {saison(s): rendement.loc[s].round(3).to_dict() for s in SAISONS},
    "rendement_global": {saison(s): round(float(v), 3) for s, v in global_.items()},
    "decomposition": {"hausse": round(hausse, 3), "effet_mix": round(effet_mix, 3),
                      "effet_adresse": round(effet_adresse, 3), "interaction": round(interaction, 3)},
    "correlation_mi_distance_rendement": {saison(s): float(v) for s, v in correlation.items()},
    "equipe_avec_le_moins_de_mi_distance": {saison(s): e for s, e in pionnier.items()},
}
(ICI / "resultats.json").write_text(json.dumps(sortie, ensure_ascii=False, indent=2))
(ICI / "terrain.json").write_text(json.dumps(terrain, separators=(",", ":")))
print(json.dumps({k: v for k, v in sortie.items() if k not in ("part_par_zone", "rendement_par_zone")},
                 ensure_ascii=False, indent=1))
