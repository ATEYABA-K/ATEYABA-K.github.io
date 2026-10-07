"""
Le bookmaker gagne toujours. Même au MMA.

Le MMA est légal en compétition en France depuis 2020, les paris sportifs battent des records
chaque année. Ce script regarde ce que disent vraiment les cotes de l'UFC : à quel point les
bookmakers voient juste, ce qu'ils prélèvent au passage, et ce que deviennent les parieurs.

Données :
- Cotes et résultats de chaque combat UFC depuis 2010 : dépôt public shortlikeafox/ultimate_ufc_dataset
  (le "Ultimate UFC Dataset" de Kaggle).
- Événements UFC par année et par pays : dépôt public Greco1899/scrape_ufc_stats (ufcstats.com).

Usage : python analyse.py   -> écrit resultats.json et combats.json à côté du script.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

COTES = "https://raw.githubusercontent.com/shortlikeafox/ultimate_ufc_dataset/master/ufc-master.csv"
EVENEMENTS = "https://raw.githubusercontent.com/Greco1899/scrape_ufc_stats/main/ufc_event_details.csv"
ICI = Path(__file__).parent
MISE = 10  # euros par pari dans les simulations


def decimale(cote_us):
    """Cote américaine (-150 / +130) -> cote décimale européenne (1,67 / 2,30)."""
    return np.where(cote_us > 0, 1 + cote_us / 100, 1 + 100 / np.abs(cote_us))


# 1. Les combats et leurs cotes --------------------------------------------
c = pd.read_csv(COTES)
c = c[c.R_odds.notna() & c.B_odds.notna() & c.Winner.isin(["Red", "Blue"])].copy()
c["annee"] = pd.to_datetime(c.date).dt.year
c["cote_rouge"], c["cote_bleu"] = decimale(c.R_odds), decimale(c.B_odds)
c["rouge_gagne"] = c.Winner == "Red"
c = c[(c.cote_rouge > 1) & (c.cote_bleu > 1)]

# 2. La marge du bookmaker ---------------------------------------------------
# Avec des cotes "justes", 1/cote_rouge + 1/cote_bleu = 100 %. Tout ce qui dépasse, c'est sa marge.
c["marge"] = 1 / c.cote_rouge + 1 / c.cote_bleu - 1

# 3. Le favori gagne-t-il ? Les cotes sont-elles bien calibrées ? -----------
c["favori_rouge"] = c.cote_rouge < c.cote_bleu
egalite = c.cote_rouge == c.cote_bleu
favori_gagne = (c.favori_rouge == c.rouge_gagne)[~egalite]

# Chaque combattant devient une ligne : sa cote, et s'il a gagné.
paris = pd.concat([
    pd.DataFrame({"cote": c.cote_rouge, "gagne": c.rouge_gagne, "annee": c.annee,
                  "proba": (1 / c.cote_rouge) / (1 + c.marge)}),
    pd.DataFrame({"cote": c.cote_bleu, "gagne": ~c.rouge_gagne, "annee": c.annee,
                  "proba": (1 / c.cote_bleu) / (1 + c.marge)}),
])
tranches_p = pd.cut(paris.proba, np.arange(0, 1.01, .1))
calibration = paris.groupby(tranches_p, observed=True).agg(
    annoncee=("proba", "mean"), observee=("gagne", "mean"), n=("gagne", "size"))

# 4. Rendement d'un pari selon la cote --------------------------------------
# Miser 1 € sur chaque combattant d'une tranche de cotes : combien revient-il en moyenne ?
paris["retour"] = np.where(paris.gagne, paris.cote, 0)
bornes = [1, 1.3, 1.6, 2, 3, 5, 100]
noms = ["< 1,30", "1,30-1,60", "1,60-2", "2-3", "3-5", "> 5"]
tranches_c = pd.cut(paris.cote, bornes, labels=noms)
rendement = paris.groupby(tranches_c, observed=True).agg(
    rendement=("retour", lambda r: r.mean() - 1), victoires=("gagne", "mean"), n=("gagne", "size"))

strategies = {
    "Toujours le favori": np.where(c.favori_rouge, np.where(c.rouge_gagne, c.cote_rouge, 0),
                                   np.where(~c.rouge_gagne, c.cote_bleu, 0))[~egalite].mean() - 1,
    "Toujours l'outsider": np.where(c.favori_rouge, np.where(~c.rouge_gagne, c.cote_bleu, 0),
                                    np.where(c.rouge_gagne, c.cote_rouge, 0))[~egalite].mean() - 1,
    "Au hasard": paris.retour.mean() - 1,
}

# 5. Simulation : 10 000 parieurs, 100 paris chacun, un camp tiré au hasard -----
rng = np.random.default_rng(2026)
idx = rng.integers(0, len(c), size=(10_000, 100))
camp_rouge = rng.random((10_000, 100)) < .5
cotes = np.where(camp_rouge, c.cote_rouge.values[idx], c.cote_bleu.values[idx])
gagnes = np.where(camp_rouge, c.rouge_gagne.values[idx], ~c.rouge_gagne.values[idx])
bilan = (np.where(gagnes, cotes * MISE, 0) - MISE).sum(axis=1)

# 6. La popularité : événements UFC par an, et en France ---------------------
ev = pd.read_csv(EVENEMENTS)
ev["annee"] = pd.to_datetime(ev.DATE.str.strip(), format="%B %d, %Y").dt.year
en_france = ev[ev.LOCATION.str.contains("France", na=False)].sort_values("annee")
ev = ev[ev.annee <= 2025]  # 2026 n'est pas terminée

sortie = {
    "periode": f"{c.annee.min()}-{c.annee.max()}",
    "combats": int(len(c)),
    "marge_mediane": round(float(c.marge.median()), 4),
    "marge_par_annee": c.groupby("annee").marge.median().round(4).to_dict(),
    "favori_gagne": round(float(favori_gagne.mean()), 3),
    "favori_gagne_par_annee": (c.favori_rouge == c.rouge_gagne)[~egalite].groupby(c.annee[~egalite]).mean().round(3).to_dict(),
    "calibration": [{"annoncee": round(r.annoncee, 3), "observee": round(r.observee, 3), "n": int(r.n)}
                    for r in calibration.itertuples()],
    "rendement_par_cote": {k: {"rendement": round(r.rendement, 3), "victoires": round(r.victoires, 3), "n": int(r.n)}
                           for k, r in rendement.iterrows()},
    "strategies": {k: round(float(v), 3) for k, v in strategies.items()},
    # Marge d'erreur (IC à 95 %) du rendement par tranche : un rendement proche de 0 peut être du bruit.
    "rendement_par_cote_ic95": paris.groupby(tranches_c, observed=True).retour.agg(
        lambda r: round(float(1.96 * r.std() / np.sqrt(len(r))), 3)).to_dict(),
    "simulation": {"parieurs": 10_000, "paris": 100, "mise": MISE,
                   "part_gagnants": round(float((bilan > 0).mean()), 3),
                   "bilan_median": round(float(np.median(bilan)), 1),
                   "bilan_moyen": round(float(bilan.mean()), 1)},
    "evenements_ufc_par_annee": ev.groupby("annee").size().to_dict(),
    "evenements_en_france": en_france[["EVENT", "DATE"]].apply(lambda r: f"{r.EVENT.strip()} ({r.DATE.strip()})", axis=1).tolist(),
}
(ICI / "resultats.json").write_text(json.dumps(sortie, ensure_ascii=False, indent=2))
# Version compacte des combats pour le simulateur de la page : [cote rouge, cote bleu, rouge gagne, année]
compact = [[round(a, 2), round(b, 2), int(g), int(y)] for a, b, g, y in
           zip(c.cote_rouge, c.cote_bleu, c.rouge_gagne, c.annee)]
(ICI / "combats.json").write_text(json.dumps(compact, separators=(",", ":")))
print(json.dumps({k: v for k, v in sortie.items() if "par_annee" not in k}, ensure_ascii=False, indent=1))
