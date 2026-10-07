"""
Sur un ring, on gagne aux points. Mais lesquels ?
Ce que les juges de l'UFC récompensent vraiment quand un combat va à la décision.

Données : statistiques officielles ufcstats.com, compilées par le dépôt public
Greco1899/scrape_ufc_stats (un CSV par table, mis à jour chaque semaine).

Usage : python analyse.py   -> écrit resultats.json à côté du script.
"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SOURCE = "https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/main/"
DEBUT = 2001  # règles unifiées adoptées par l'UFC fin 2000 : on compare ce qui est comparable
ICI = Path(__file__).parent


def charger(nom):
    df = pd.read_csv(SOURCE + nom)
    for c in df.columns:
        if df[c].dtype == object or str(df[c].dtype).startswith("str"):
            df[c] = df[c].astype(str).str.strip()
    return df


def reussis(x):
    """'16 of 40' -> 16 (coups réussis)."""
    m = re.match(r"(\d+) of (\d+)", str(x))
    return int(m[1]) if m else np.nan


def secondes(x):
    """'2:11' -> 131."""
    m = re.match(r"(\d+):(\d+)", str(x))
    return int(m[1]) * 60 + int(m[2]) if m else np.nan


# 1. Chargement -------------------------------------------------------------
resultats = charger("ufc_fight_results.csv")
stats = charger("ufc_fight_stats.csv")
events = charger("ufc_event_details.csv")

resultats = resultats.merge(events[["EVENT", "DATE"]], on="EVENT", how="left")
resultats["annee"] = pd.to_datetime(resultats["DATE"], format="%B %d, %Y").dt.year
resultats = resultats[resultats["annee"] >= DEBUT]

# 2. Stats par combattant et par combat (les CSV sont par round) -------------
stats["frappes"] = stats["SIG.STR."].map(reussis)
stats["amenees"] = stats["TD"].map(reussis)
stats["controle"] = stats["CTRL"].map(secondes)
for c in ["KD", "SUB.ATT"]:
    stats[c] = pd.to_numeric(stats[c], errors="coerce")
stats = stats.rename(columns={"KD": "knockdowns", "SUB.ATT": "soumissions"})
VARIABLES = ["frappes", "amenees", "controle", "knockdowns", "soumissions"]
par_combat = stats.groupby(["EVENT", "BOUT", "FIGHTER"])[VARIABLES].sum(min_count=1).reset_index()

# 3. Vainqueur / perdant ----------------------------------------------------
resultats[["A", "B"]] = resultats["BOUT"].str.split(" vs. ", n=1, expand=True)
resultats["vainqueur"] = np.select(
    [resultats.OUTCOME == "W/L", resultats.OUTCOME == "L/W"], [resultats.A, resultats.B], None)
resultats["perdant"] = np.select(
    [resultats.OUTCOME == "W/L", resultats.OUTCOME == "L/W"], [resultats.B, resultats.A], None)
resultats["decision"] = resultats["METHOD"].str.startswith("Decision")

dec = resultats[resultats.decision & resultats.vainqueur.notna()]
v = par_combat.rename(columns={"FIGHTER": "vainqueur", **{c: "v_" + c for c in VARIABLES}})
p = par_combat.rename(columns={"FIGHTER": "perdant", **{c: "p_" + c for c in VARIABLES}})
dec = dec.merge(v, on=["EVENT", "BOUT", "vainqueur"]).merge(p, on=["EVENT", "BOUT", "perdant"])
ecart = pd.DataFrame({c: dec["v_" + c] - dec["p_" + c] for c in VARIABLES}).fillna(0)

# 4. Combien de combats vont aux juges ? ------------------------------------
periodes = pd.cut(resultats["annee"], [2000, 2008, 2016, 2100], labels=["2001-2008", "2009-2016", "2017-2026"])
part_decisions = resultats.groupby(periodes, observed=True)["decision"].mean().round(3).to_dict()

# 5. Le vainqueur a-t-il porté plus de frappes ? ----------------------------
moins_de_frappes = ecart["frappes"] < 0
contre_courant = ecart[moins_de_frappes]
compense = {
    "plus_de_controle": round((contre_courant.controle > 0).mean(), 3),
    "plus_d_amenees": round((contre_courant.amenees > 0).mean(), 3),
    "controle_ou_amenees": round(((contre_courant.controle > 0) | (contre_courant.amenees > 0)).mean(), 3),
    "plus_de_knockdowns": round((contre_courant.knockdowns > 0).mean(), 3),
    "rien_de_tout_ca": round(((contre_courant.controle <= 0) & (contre_courant.amenees <= 0)
                              & (contre_courant.knockdowns <= 0)).mean(), 3),
}

# 6. Plus le combat est serré, plus c'est pile ou face -----------------------
total = (dec["v_frappes"] + dec["p_frappes"]).clip(lower=1)
ecart_relatif = (ecart["frappes"] / total).abs()
tranches = pd.cut(ecart_relatif, [0, .05, .10, .20, 1], right=False,
                  labels=["moins de 5 %", "5 à 10 %", "10 à 20 %", "plus de 20 %"])
serre = (ecart["frappes"] > 0).groupby(tranches, observed=True).agg(["mean", "size"])
serre = {k: {"vainqueur_a_plus_frappe": round(r["mean"], 3), "combats": int(r["size"])} for k, r in serre.iterrows()}

par_methode = {m: round((ecart["frappes"][dec.METHOD == m] < 0).mean(), 3)
               for m in ["Decision - Unanimous", "Decision - Split"]}

# 7. Modèle : quelles stats prédisent la décision ? -------------------------
# On présente chaque combat dans un ordre aléatoire (A-B ou B-A) pour que le modèle
# ne puisse pas "tricher" en apprenant que le premier est toujours le vainqueur.
rng = np.random.default_rng(42)
inverse = rng.random(len(ecart)) < .5
X = ecart.copy()
X[inverse] *= -1
y = (~inverse).astype(int)
cv = StratifiedKFold(5, shuffle=True, random_state=42)


def precision(colonnes):
    modele = make_pipeline(StandardScaler(), LogisticRegression())
    return round(cross_val_score(modele, X[colonnes], y, cv=cv).mean(), 3)


precision_seule = {c: precision([c]) for c in VARIABLES}
precision_tout = precision(VARIABLES)
modele = make_pipeline(StandardScaler(), LogisticRegression()).fit(X[VARIABLES], y)
poids = dict(zip(VARIABLES, modele[-1].coef_[0].round(2).tolist()))

sortie = {
    "periode": f"{DEBUT}-{int(resultats.annee.max())}",
    "combats": int(len(resultats)),
    "decisions_analysees": int(len(dec)),
    "part_des_combats_aux_decisions": part_decisions,
    "vainqueur_moins_de_frappes": round(moins_de_frappes.mean(), 3),
    "vainqueur_moins_de_frappes_n": int(moins_de_frappes.sum()),
    "ce_qui_compense": compense,
    "selon_ecart_de_frappes": serre,
    "vainqueur_moins_de_frappes_par_methode": par_methode,
    "precision_une_stat": precision_seule,
    "precision_cinq_stats": precision_tout,
    "poids_standardises": poids,
}
(ICI / "resultats.json").write_text(json.dumps(sortie, ensure_ascii=False, indent=2))
print(json.dumps(sortie, ensure_ascii=False, indent=2))
