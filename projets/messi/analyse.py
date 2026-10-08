"""Messi est-il le meilleur joueur de l'histoire ? Calcul des résultats à partir de deux sources publiques.

1. Transfermarkt (jeu de données salimt/football-datasets, octobre 2025) : buts, passes décisives,
   penalties et matchs de chaque joueur, saison par saison, en club et en sélection.
2. StatsBomb (données ouvertes) : tous les tirs des matchs du FC Barcelone en Liga, de 2004-05 à 2020-21,
   avec leur probabilité de but (xG).

Utilisation : python analyse.py <perf.csv> <natperf.csv> <tirs.json>
Le fichier tirs.json est produit par telecharger_tirs.py.
"""
import json
import sys
from pathlib import Path

import pandas as pd

ICI = Path(__file__).resolve().parent
JOUEURS = {28003: "Messi", 8198: "Cristiano Ronaldo", 38253: "Lewandowski", 44352: "Suárez", 3455: "Ibrahimović",
           18922: "Benzema", 132098: "Kane", 342229: "Mbappé", 418560: "Haaland", 68290: "Neymar",
           148455: "Salah", 26399: "Agüero", 3207: "Henry", 3332: "Rooney"}
# Ballon d'Or remportés (France Football). Source : https://www.si.com/soccer/men-s-ballon-d-or-full-list-of-winners
BALLONS = {"Messi": [2009, 2010, 2011, 2012, 2015, 2019, 2021, 2023], "Cristiano Ronaldo": [2008, 2013, 2014, 2016, 2017],
           "Michel Platini": [1983, 1984, 1985], "Johan Cruyff": [1971, 1973, 1974], "Marco van Basten": [1988, 1989, 1992]}


def carriere(perf, natperf):
    p = pd.read_csv(perf, low_memory=False)
    p = p[p.player_id.isin(JOUEURS)].copy()
    p["nom"] = p.player_id.map(JOUEURS)
    club = p.groupby("nom").agg(matchs=("nb_on_pitch", "sum"), buts=("goals", "sum"),
                                passes=("assists", "sum"), penalties=("penalty_goals", "sum"))
    n = pd.read_csv(natperf)
    n = n[n.player_id.isin(JOUEURS)].copy()
    # La sélection A est la ligne avec le plus de matchs (les autres sont les équipes de jeunes).
    n = n.loc[n.groupby("player_id").matches.idxmax()]
    n["nom"] = n.player_id.map(JOUEURS)
    sel = n.set_index("nom")[["matches", "goals"]].rename(columns={"matches": "matchs_sel", "goals": "buts_sel"})
    t = club.join(sel).fillna(0)
    t["buts_total"] = t.buts + t.buts_sel
    t["buts_hors_pen"] = t.buts - t.penalties
    t["contrib_par_match"] = (t.buts_hors_pen + t.passes) / t.matchs
    # Saisons à 40 buts ou plus en club (toutes compétitions confondues). La Coupe du monde des clubs est notée
    # avec l'année de fin de saison : pour un club européen, « 2012 » correspond à la saison 2011-12.
    europe = set(p.loc[p.season_name.str.contains("/"), "team_id"])
    cdm = (p.competition_name == "Club World Cup") & p.team_id.isin(europe)
    an = p.loc[cdm, "season_name"].astype(int)
    p.loc[cdm, "season_name"] = [f"{(y - 1) % 100:02d}/{y % 100:02d}" for y in an]
    s = p.groupby(["nom", "season_name"]).goals.sum().reset_index()
    t["saisons_40"] = s[s.goals >= 40].groupby("nom").size().reindex(t.index).fillna(0)
    t["meilleure_saison"] = s.groupby("nom").goals.max()
    return t.sort_values("contrib_par_match", ascending=False)


def tirs(fichier):
    r = pd.DataFrame([x for x in json.load(open(fichier)) if "joueur" in x])
    r = r[r.type != "Penalty"].copy()
    r["but"] = r.resultat == "Goal"
    # Distance au but (StatsBomb : terrain de 120 x 80, but en x = 120, y = 40).
    r["dist"] = r["loc"].apply(lambda l: ((120 - l[0]) ** 2 + (40 - l[1]) ** 2) ** 0.5 * 0.9144)
    r["hors_surface"] = r["loc"].apply(lambda l: l[0] < 102 or l[1] < 18 or l[1] > 62)
    messi = r[r.joueur == "Lionel Andrés Messi Cuccittini"]
    saisons = messi.groupby("saison").agg(tirs=("but", "size"), buts=("but", "sum"), xg=("xg", "sum")).reset_index()
    joueurs = r.groupby("joueur").agg(tirs=("but", "size"), buts=("but", "sum"), xg=("xg", "sum"))
    joueurs = joueurs[joueurs.tirs >= 100]
    joueurs["ecart"] = joueurs.buts - joueurs.xg
    hs = messi[messi.hors_surface]
    autres_hs = r[(r.joueur != messi.joueur.iloc[0]) & r.hors_surface]
    return {
        "saisons": saisons.round(2).to_dict("records"),
        "messi": {"tirs": int(len(messi)), "buts": int(messi.but.sum()), "xg": round(float(messi.xg.sum()), 1)},
        "classement_ecart": joueurs.sort_values("ecart", ascending=False).head(10).round(1).reset_index().to_dict("records"),
        "nb_joueurs_100_tirs": int(len(joueurs)),
        "hors_surface": {"messi_tirs": int(len(hs)), "messi_buts": int(hs.but.sum()), "messi_xg": round(float(hs.xg.sum()), 1),
                         "messi_taux": round(float(hs.but.mean()) * 100, 1),
                         "autres_taux": round(float(autres_hs.but.mean()) * 100, 1)},
    }


if __name__ == "__main__":
    perf, natperf, fichier_tirs = sys.argv[1:4]
    c = carriere(perf, natperf)
    res = {"carriere": c.round(3).reset_index().to_dict("records"), "tirs": tirs(fichier_tirs), "ballons": BALLONS}
    (ICI / "resultats.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(c[["matchs", "buts_total", "buts_hors_pen", "passes", "contrib_par_match", "saisons_40", "meilleure_saison"]])
    print(json.dumps(res["tirs"]["messi"]), json.dumps(res["tirs"]["hors_surface"]))
