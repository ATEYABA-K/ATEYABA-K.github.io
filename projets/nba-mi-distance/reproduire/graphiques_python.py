"""Redessine les graphiques de l'étude « Le tir que la NBA a arrêté de financer » à partir des CSV de ce dossier.
Usage : pip install pandas matplotlib  puis  python graphiques_python.py  -> fichiers PNG ici."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ICI = Path(__file__).parent
lire = lambda nom: pd.read_csv(ICI / nom, sep=";")
ORANGE, BLEU, GRIS = "#d9542b", "#1F3864", "#8fa0c2"
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})

# 1. Part des tirs par grande zone
p = lire("parts_par_zone.csv")
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(p.saison, (p["Sous le panier"] + p["Raquette"]) * 100, "--", color=GRIS, label="Près du panier")
ax.plot(p.saison, (p["3 pts dans le coin"] + p["3 pts dans l'axe"]) * 100, color=BLEU, lw=2.5, label="3 points")
ax.plot(p.saison, p["Mi-distance"] * 100, color=ORANGE, lw=2.5, label="Mi-distance")
ax.set(title="Part des tirs NBA par zone (%)"); ax.legend(frameon=False)
ax.set_xticks(p.saison[::4]); fig.tight_layout(); fig.savefig(ICI / "1_parts.png", dpi=150)

# 2. Rendement par zone : première vs dernière saison
r = lire("rendement_par_zone.csv").set_index("saison")
fig, ax = plt.subplots(figsize=(8, 5))
r.iloc[[0, -1]].T.plot.barh(ax=ax, color=[GRIS, ORANGE])
ax.axvline(1, color="#333", ls="--"); ax.set(title="Points rapportés par tir, selon la zone", xlabel="Points par tir")
fig.tight_layout(); fig.savefig(ICI / "2_rendement.png", dpi=150)

# 3. Corrélation équipe par équipe
c = lire("correlation_equipes.csv")
fig, ax = plt.subplots(figsize=(9, 4))
ax.bar(c.saison, c.correlation, color=[ORANGE if v > 0 else BLEU for v in c.correlation])
ax.axhline(0, color="#333", lw=1); ax.set_xticks(c.saison[::4])
ax.set(title="Corrélation entre part de mi-distance et rendement des équipes")
fig.tight_layout(); fig.savefig(ICI / "3_correlation.png", dpi=150)

# 4. La carte des tirs, première et dernière saison
t = lire("terrain.csv")
fig, axes = plt.subplots(1, 2, figsize=(11, 5.5))
for ax, s in zip(axes, [t.saison.iloc[0], t.saison.iloc[-1]]):
    d = t[t.saison == s]
    ax.scatter(d.x_pieds, d.y_pieds, s=d.part_des_tirs * 6000, c=d.points_par_tir, cmap="coolwarm", vmin=.65, vmax=1.35, marker="s")
    ax.set(title=s, xlim=(-25, 25), ylim=(0, 32), aspect="equal"); ax.axis("off")
fig.suptitle("Où l'on tire (taille) et ce que ça rapporte (couleur)"); fig.tight_layout(); fig.savefig(ICI / "4_terrain.png", dpi=150)
print("PNG écrits dans", ICI)
