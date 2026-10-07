"""Redessine les graphiques de l'étude « Le bookmaker gagne toujours » à partir des CSV de ce dossier.
Usage : pip install pandas matplotlib  puis  python graphiques_python.py  -> fichiers PNG ici."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ICI = Path(__file__).parent
lire = lambda nom: pd.read_csv(ICI / nom, sep=";")
ORANGE, BLEU, GRIS = "#d9542b", "#1F3864", "#8fa0c2"
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})

# 1. Où va l'argent : colonnes empilées
a = lire("argent.csv")
fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(a.annee, a.redistribue_meur / 1000, color=BLEU, label="Revenu aux parieurs")
ax.bar(a.annee, a.garde_meur / 1000, bottom=a.redistribue_meur / 1000, color=ORANGE, label="Gardé par les opérateurs")
ax.set(title="Paris sportifs en ligne en France (Md€)", ylabel="Md€"); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(ICI / "1_argent.png", dpi=150)
print("Corrélation mises / argent gardé :", round(np.corrcoef(a.mises_meur, a.garde_meur)[0, 1], 3))

# 2. Événements UFC par année
e = lire("evenements_ufc.csv")
fig, ax = plt.subplots(figsize=(9, 4))
ax.bar(e.annee, e.evenements, color=[ORANGE if y >= 2020 else GRIS for y in e.annee])
ax.set(title="Événements UFC par année (orange : MMA légal en France)")
fig.tight_layout(); fig.savefig(ICI / "2_evenements.png", dpi=150)

# 3. Calibration des cotes
c = lire("calibration.csv")
fig, ax = plt.subplots(figsize=(6, 6))
ax.plot([0, 1], [0, 1], "--", color="#888", label="Cote parfaite")
ax.plot(c.proba_annoncee, c.taux_victoire_reel, "o-", color=ORANGE, label="Réel")
ax.set(title="Les bookmakers voient juste", xlabel="Probabilité annoncée", ylabel="Taux de victoire réel")
ax.legend(frameon=False); fig.tight_layout(); fig.savefig(ICI / "3_calibration.png", dpi=150)

# 4. Rendement par tranche de cote, avec la marge d'erreur
r = lire("rendement_par_cote.csv")
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(r.tranche_cote, r.rendement * 100, yerr=r.marge_erreur_95 * 100, capsize=4,
       color=[BLEU if v > 0 else ORANGE if v < -.1 else GRIS for v in r.rendement])
ax.axhline(0, color="#333", lw=1); ax.set(title="Rendement moyen d'un pari selon la cote (%)", xlabel="Cote")
fig.tight_layout(); fig.savefig(ICI / "4_rendement.png", dpi=150)

# 5. Simulation : 1 000 parieurs, 100 paris de 10 € au hasard
k = lire("combats.csv")
cotes = np.concatenate([k.cote_rouge, k.cote_bleu]); gagne = np.concatenate([k.rouge_gagne == 1, k.rouge_gagne == 0])
rng = np.random.default_rng(); i = rng.integers(0, len(cotes), (1000, 100))
bilans = np.where(gagne[i], 10 * (cotes[i] - 1), -10).sum(axis=1)
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(bilans, bins=30, color=GRIS); ax.axvline(0, color="#333", ls="--")
ax.set(title=f"1 000 parieurs, 100 paris : {(bilans > 0).mean():.0%} finissent gagnants", xlabel="Bilan (€)")
fig.tight_layout(); fig.savefig(ICI / "5_simulation.png", dpi=150)
print("PNG écrits dans", ICI)
