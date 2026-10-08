"""
Construit, pour chaque étude, les fichiers Excel du dossier projets/<étude>/excel/ :
  - <étude>-corrige.xlsx  : données, formules et graphiques finis (ce que montre le site)
  - <étude>-exercice.xlsx : les mêmes données, sans formules ni graphiques, pour s'entraîner avec TUTO.md
  - csv/                  : un CSV par graphique, pour Power BI
Puis exporte chaque graphique du corrigé en PNG (graphiques/), via LibreOffice.
Usage : python outils/excel.py
"""
import csv
import json
import subprocess
import tempfile
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.chart import BarChart, LineChart, Reference, ScatterChart, Series
from openpyxl.chart.data_source import NumDataSource, NumRef
from openpyxl.chart.error_bar import ErrorBars
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.marker import DataPoint, Marker
from openpyxl.chart.series import SeriesLabel
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.chart.text import RichText
from openpyxl.comments import Comment
from openpyxl.drawing.line import LineProperties
from openpyxl.drawing.text import CharacterProperties, Paragraph, ParagraphProperties
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from PIL import Image, ImageChops

RACINE = Path(__file__).resolve().parent.parent
BLEU, ORANGE, GRIS = "1F3864", "D9542B", "8FA0C2"
F = lambda **k: Font(name="Arial", **k)
ENTETE, JAUNE = PatternFill("solid", fgColor=BLEU), PatternFill("solid", fgColor="FFF2CC")


# ---------------------------------------------------------------- outils
def texte(taille=1000, gras=False, couleur="404040"):
    cp = CharacterProperties(sz=taille, b=gras, solidFill=couleur)
    return RichText(p=[Paragraph(pPr=ParagraphProperties(defRPr=cp), endParaRPr=cp)])


def styler(ch, titre, x=None, y=None, legende=True, num=None):
    ch.title = titre
    ch.title.tx.rich.p[0].pPr = ParagraphProperties(defRPr=CharacterProperties(sz=1400, b=True, solidFill="1B1F27"))
    ch.width, ch.height = 24, 13.5
    for ax, t in ((ch.x_axis, x), (ch.y_axis, y)):
        ax.delete = False
        ax.txPr = texte()
        if t:
            ax.title = t
        ax.graphicalProperties = GraphicalProperties(ln=LineProperties(solidFill="BFBFBF"))
    if ch.y_axis.majorGridlines is not None:
        ch.y_axis.majorGridlines.spPr = GraphicalProperties(ln=LineProperties(solidFill="EDEDED"))
    if num:
        ch.y_axis.numFmt = num
    if legende:
        ch.legend.position = "b"
        ch.legend.txPr = texte(1000)
    else:
        ch.legend = None
    return ch


def remplir(s, couleur):
    s.graphicalProperties.solidFill = couleur
    s.graphicalProperties.line.noFill = True


def point(idx, couleur):
    pt = DataPoint(idx=idx, invertIfNegative=False)
    pt.graphicalProperties.solidFill = couleur
    pt.graphicalProperties.line.noFill = True
    return pt


def etiquettes(s, fmt=None):
    s.dLbls = DataLabelList()
    s.dLbls.showVal = True
    for k in ("showSerName", "showCatName", "showLegendKey", "showPercent"):
        setattr(s.dLbls, k, False)
    s.dLbls.txPr = texte(900, True, "1B1F27")
    if fmt:
        s.dLbls.numFmt = fmt


def entetes(ws, ligne, noms, largeurs=None):
    for j, n in enumerate(noms, 1):
        c = ws.cell(row=ligne, column=j, value=n)
        c.font, c.fill = F(bold=True, color="FFFFFF"), ENTETE
        c.alignment = Alignment(wrap_text=True, vertical="center")
        ws.column_dimensions[get_column_letter(j)].width = (largeurs or {}).get(j, max(13, len(n) + 2))
    ws.row_dimensions[ligne].height = 32


def titre(ws, t, note, consigne=None):
    ws["A1"], ws["A1"].font = t, F(size=14, bold=True)
    ws["A2"], ws["A2"].font = note, F(italic=True, color="666666")
    if consigne:
        ws["A3"], ws["A3"].font = consigne, F(bold=True, color="7F6000")
        ws["A3"].fill = JAUNE


def a_faire(ws, plage):
    for ligne in ws[plage]:
        for c in ligne:
            c.fill = JAUNE


def page_image(ws, zone):
    """Règle l'impression d'un onglet pour l'exporter en image (une page, paysage, sans marges)."""
    ws.print_area = zone
    ws.page_setup.orientation = "landscape"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = ws.page_setup.fitToHeight = 1
    m = ws.page_margins
    m.left = m.right = m.top = m.bottom = 0.2
    m.header = m.footer = 0


def onglet_graphique(wb, nom, chart):
    g = wb.create_sheet(nom)
    g.add_chart(chart, "A1")
    g["O28"] = " "
    g.print_area = "A1:O28"
    g.page_setup.orientation = "landscape"
    g.sheet_properties.pageSetUpPr.fitToPage = True
    g.page_setup.fitToWidth = g.page_setup.fitToHeight = 1
    m = g.page_margins
    m.left = m.right = m.top = m.bottom = 0.2
    m.header = m.footer = 0
    g.sheet_view.showGridLines = False


def ecrire_csv(dossier, nom, entete, lignes):
    dossier.mkdir(parents=True, exist_ok=True)
    with open(dossier / nom, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(entete)
        w.writerows(lignes)


def lisez_moi(wb, lignes):
    ws = wb.active
    ws.title = "Lisez-moi"
    for i, l in enumerate(lignes, 1):
        ws.cell(row=i, column=1, value=l).font = F(size=14, bold=True) if i == 1 else F(bold=l == "Les onglets")
    ws.column_dimensions["A"].width = 130


def exporter_graphiques(xlsx, dossier, noms):
    """Exporte chaque onglet graphique du classeur en PNG (LibreOffice ouvre le .xlsx et l'imprime en PDF)."""
    dossier.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        wb = load_workbook(xlsx)
        for ws in wb.worksheets:
            if ws.title not in noms:
                ws.sheet_state = "hidden"
        wb.save(tmp / "export.xlsx")
        # Profil LibreOffice dédié, réglé en français : virgule décimale comme dans Excel en français.
        profil = tmp / "profil/user"
        profil.mkdir(parents=True)
        (profil / "registrymodifications.xcu").write_text(
            '<?xml version="1.0" encoding="UTF-8"?><oor:items xmlns:oor="http://openoffice.org/2001/registry" '
            'xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            '<item oor:path="/org.openoffice.Setup/L10N"><prop oor:name="ooSetupSystemLocale" oor:op="fuse"><value>fr-FR</value></prop></item>'
            '<item oor:path="/org.openoffice.Setup/L10N"><prop oor:name="ooLocale" oor:op="fuse"><value>fr-FR</value></prop></item>'
            '</oor:items>')
        subprocess.run(["soffice", f"-env:UserInstallation=file://{tmp / 'profil'}", "--headless", "--convert-to", "pdf",
                        "--outdir", str(tmp), str(tmp / "export.xlsx")], check=True, capture_output=True)
        subprocess.run(["pdftoppm", "-png", "-r", "170", str(tmp / "export.pdf"), str(tmp / "p")], check=True)
        pages = sorted(tmp.glob("p-*.png"))
        ordre = [ws.title for ws in wb.worksheets if ws.title in noms]
        assert len(pages) == len(ordre), (len(pages), ordre)
        for page, fichier in zip(pages, [noms[t] for t in ordre]):
            im = Image.open(page).convert("RGB")
            bbox = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
            im.crop(bbox).save(dossier / fichier, optimize=True)


# ============================================================== Étude 1
def paris(exercice):
    D = RACINE / "projets/ufc-paris"
    R = json.loads((D / "resultats.json").read_text())
    C = json.loads((D / "combats.json").read_text())
    CSV = D / "excel/csv"
    wb = Workbook()
    lisez_moi(wb, [
        "Le bookmaker gagne toujours. Même au MMA. · " + ("EXERCICE" if exercice else "CORRIGÉ"),
        "",
        "Exercice : les cellules jaunes sont à remplir, les graphiques à construire. Suivez TUTO.md (ou la page Tuto du site), étape par étape."
        if exercice else "Corrigé : toutes les formules sont en place, et chaque graphique a son onglet (G1 à G5). Ce sont ces graphiques qui sont sur le site.",
        "",
        "Les onglets",
        "• Argent : mises, gains redistribués, part gardée par les opérateurs (ARJEL / ANJ, 2010-2025).",
        "• Evenements : nombre d'événements UFC par année (ufcstats.com).",
        "• Calibration : probabilité annoncée par la cote vs taux de victoire réel.",
        "• Rendement : ce que rapporte 1 € misé, par tranche de cote.",
        "• Simulateur : un parieur, 100 paris sur de vrais combats tirés au hasard (F9 = nouveau parieur).",
        "• Combats : les 6 916 combats (cotes décimales, vainqueur) utilisés par le simulateur.",
        "",
        "Sources : Ultimate UFC Dataset (github.com/shortlikeafox/ultimate_ufc_dataset), ufcstats.com, rapports ARJEL et ANJ.",
    ])

    # --- Argent
    M = R["marche_francais"]["par_annee"]
    data = [[str(a), v["mises"], v["garde"]] for a, v in M.items()]
    ecrire_csv(CSV, "argent.csv", ["annee", "mises_meur", "garde_meur", "redistribue_meur"], [[a, m, g, m - g] for a, m, g in data])
    ws = wb.create_sheet("Argent")
    titre(ws, "Paris sportifs en ligne en France (millions d'euros)",
          "Sources : ARJEL (2010-2018), ANJ (2020-2025). 2019 : mises déduites de la hausse publiée en 2020. 2024 : chiffre révisé par l'ANJ.",
          "À faire : colonnes D à G (étapes 1.1 à 1.3), la corrélation (1.4) et le graphique (1.5)." if exercice else None)
    entetes(ws, 4, ["Année", "Mises (M€)", "Gardé par les opérateurs (M€)", "Revenu aux parieurs (M€)", "Part gardée",
                    "Revenu (Md€)", "Gardé (Md€)"], {3: 18, 4: 18})
    r0, fin = 5, 4 + len(data)
    for i, (a, m, g) in enumerate(data, r0):
        ws.cell(row=i, column=1, value=a)
        ws.cell(row=i, column=2, value=m).number_format = "#,##0"
        ws.cell(row=i, column=3, value=g).number_format = "#,##0"
        if not exercice:
            ws[f"D{i}"], ws[f"E{i}"], ws[f"F{i}"], ws[f"G{i}"] = f"=B{i}-C{i}", f"=IFERROR(C{i}/B{i},0)", f"=D{i}/1000", f"=C{i}/1000"
        ws[f"D{i}"].number_format, ws[f"E{i}"].number_format = "#,##0", "0.0%"
        ws[f"F{i}"].number_format = ws[f"G{i}"].number_format = "0.0"
    ws[f"A{fin + 1}"], ws[f"A{fin + 1}"].font = "Total", F(bold=True)
    ws[f"A{fin + 3}"], ws[f"A{fin + 3}"].font = "Corrélation mises / gardé :", F(bold=True)
    if exercice:
        a_faire(ws, f"D{r0}:G{fin}"); a_faire(ws, f"B{fin + 1}:E{fin + 1}"); a_faire(ws, f"E{fin + 3}:E{fin + 3}")
    else:
        for col in "BCD":
            ws[f"{col}{fin + 1}"], ws[f"{col}{fin + 1}"].number_format = f"=SUM({col}{r0}:{col}{fin})", "#,##0"
        ws[f"E{fin + 1}"], ws[f"E{fin + 1}"].number_format = f"=C{fin + 1}/B{fin + 1}", "0.0%"
        ws[f"E{fin + 3}"], ws[f"E{fin + 3}"].number_format = f"=CORREL(B{r0}:B{fin},C{r0}:C{fin})", "0.000"
        ch = BarChart()
        ch.type, ch.grouping, ch.overlap, ch.gapWidth = "col", "stacked", 100, 55
        ch.add_data(Reference(ws, min_col=6, max_col=7, min_row=4, max_row=fin), titles_from_data=True)
        ch.series[0].tx, ch.series[1].tx = SeriesLabel(v="Revenu aux parieurs"), SeriesLabel(v="Gardé par les opérateurs")
        ch.set_categories(Reference(ws, min_col=1, min_row=r0, max_row=fin))
        remplir(ch.series[0], BLEU); remplir(ch.series[1], ORANGE)
        onglet_graphique(wb, "G1 Argent", styler(ch, "Paris sportifs en ligne en France : où vont les mises (Md€)", num="0"))

    # --- Événements
    ev = [[str(a), v] for a, v in R["evenements_ufc_par_annee"].items() if int(a) >= 2001]
    ecrire_csv(CSV, "evenements_ufc.csv", ["annee", "evenements"], ev)
    ws = wb.create_sheet("Evenements")
    titre(ws, "Événements UFC organisés chaque année", "Source : ufcstats.com",
          "À faire : le graphique (étape 2), avec les années 2020 et suivantes en orange." if exercice else None)
    entetes(ws, 4, ["Année", "Événements"])
    for i, row in enumerate(ev, 5):
        ws.cell(row=i, column=1, value=row[0]); ws.cell(row=i, column=2, value=row[1])
    fin = 4 + len(ev)
    if not exercice:
        ch = BarChart(); ch.gapWidth = 40
        ch.add_data(Reference(ws, min_col=2, min_row=4, max_row=fin), titles_from_data=True)
        ch.set_categories(Reference(ws, min_col=1, min_row=5, max_row=fin))
        remplir(ch.series[0], GRIS)
        ch.series[0].dPt += [point(k, ORANGE) for k, row in enumerate(ev) if int(row[0]) >= 2020]
        ch.x_axis.tickLblSkip = 2
        onglet_graphique(wb, "G2 Evenements", styler(ch, "Événements UFC par année (orange : MMA légal en France)", legende=False))

    # --- Calibration
    cal = [[p["annoncee"], p["observee"], p["n"]] for p in R["calibration"] if p["n"] >= 100]
    ecrire_csv(CSV, "calibration.csv", ["proba_annoncee", "taux_victoire_reel", "combattants"], cal)
    ws = wb.create_sheet("Calibration")
    titre(ws, "Probabilité annoncée par la cote vs taux de victoire réel", "Source : Ultimate UFC Dataset, 2010-2026. Marge du bookmaker retirée.",
          "À faire : colonne D (diagonale), puis le nuage de points (étape 3)." if exercice else None)
    entetes(ws, 4, ["Probabilité annoncée", "Taux de victoire réel", "Combattants", "Cote parfaite"])
    for i, row in enumerate(cal, 5):
        for j, v in enumerate(row, 1):
            ws.cell(row=i, column=j, value=v).number_format = "0%" if j < 3 else "#,##0"
        ws[f"D{i}"].number_format = "0%"
        if not exercice:
            ws[f"D{i}"] = f"=A{i}"
    fin = 4 + len(cal)
    if exercice:
        a_faire(ws, f"D5:D{fin}")
    else:
        sc = ScatterChart(); sc.style = 13
        xs = Reference(ws, min_col=1, min_row=5, max_row=fin)
        s1 = Series(Reference(ws, min_col=4, min_row=5, max_row=fin), xs, title="Cote parfaite")
        s1.graphicalProperties.line.solidFill, s1.graphicalProperties.line.dashStyle, s1.graphicalProperties.line.width = GRIS, "dash", 19050
        s1.marker = Marker(symbol="none")
        s2 = Series(Reference(ws, min_col=2, min_row=5, max_row=fin), xs, title="Taux de victoire réel")
        s2.marker = Marker(symbol="circle", size=9)
        s2.marker.graphicalProperties = GraphicalProperties(solidFill=ORANGE, ln=LineProperties(solidFill=ORANGE))
        s2.graphicalProperties.line.solidFill, s2.graphicalProperties.line.width = ORANGE, 28575
        sc.series += [s1, s2]
        sc.x_axis.scaling.min = sc.y_axis.scaling.min = 0
        sc.x_axis.scaling.max = sc.y_axis.scaling.max = 1
        sc.x_axis.numFmt = "0%"
        s2.smooth = False
        sc.scatterStyle = "lineMarker"
        styler(sc, "Les bookmakers voient juste", "Probabilité annoncée par la cote", "Taux de victoire réel", num="0%")
        sc.x_axis.majorGridlines = None
        onglet_graphique(wb, "G3 Calibration", sc)

    # --- Rendement
    rd = [[k, v["rendement"], R["rendement_par_cote_ic95"][k], v["victoires"], v["n"]] for k, v in R["rendement_par_cote"].items()]
    ecrire_csv(CSV, "rendement_par_cote.csv", ["tranche_cote", "rendement", "marge_erreur_95", "taux_victoire", "paris"], rd)
    ws = wb.create_sheet("Rendement")
    titre(ws, "Rendement moyen d'un pari, par tranche de cote",
          "Source : Ultimate UFC Dataset. Rendement = gains / mises − 1, en misant 1 € sur chaque combattant de la tranche.",
          "À faire : le graphique (étape 4), avec les couleurs et les barres d'erreur." if exercice else None)
    entetes(ws, 4, ["Tranche de cote", "Rendement moyen", "Marge d'erreur (95 %)", "Taux de victoire", "Paris"])
    for i, row in enumerate(rd, 5):
        for j, (v, f) in enumerate(zip(row, (None, "0.0%", "0.0%", "0%", "#,##0")), 1):
            c = ws.cell(row=i, column=j, value=v)
            if f:
                c.number_format = f
    fin = 4 + len(rd)
    if not exercice:
        ch = BarChart(); ch.gapWidth = 45
        ch.add_data(Reference(ws, min_col=2, min_row=4, max_row=fin), titles_from_data=True)
        ch.set_categories(Reference(ws, min_col=1, min_row=5, max_row=fin))
        s = ch.series[0]; remplir(s, GRIS); s.invertIfNegative = False
        s.dPt += [point(k, BLEU if row[1] > 0 else (ORANGE if row[1] < -.1 else GRIS)) for k, row in enumerate(rd)]
        ref = f"'Rendement'!$C$5:$C${fin}"
        s.errBars = ErrorBars(errDir="y", errBarType="both", errValType="cust", noEndCap=False,
                              plus=NumDataSource(numRef=NumRef(f=ref)), minus=NumDataSource(numRef=NumRef(f=ref)))
        ch.x_axis.tickLblPos = "low"
        onglet_graphique(wb, "G4 Rendement", styler(ch, "Parier sur l'UFC : plus la cote est haute, plus on perd", "Cote du combattant",
                                                    "Rendement moyen d'un pari", legende=False, num="0%"))

    # --- Calculatrice de marge
    ws = wb.create_sheet("Calculatrice")
    titre(ws, "Calculatrice : la marge cachée dans deux cotes", "Changez les deux cotes jaunes : tout le reste se recalcule.",
          "À faire : les formules de B7 à B11 (étape 6)." if exercice else None)
    lignes_calc = [(4, "Cote du combattant A", 1.77, "0.00"), (5, "Cote du combattant B", 2.02, "0.00"),
                   (7, "Probabilité annoncée pour A", "=1/B4", "0.0%"), (8, "Probabilité annoncée pour B", "=1/B5", "0.0%"),
                   (9, "Total des deux probabilités", "=B7+B8", "0.0%"), (10, "Marge du bookmaker", "=B9-1", "0.0%"),
                   (11, "Sur 100 € misés, le bookmaker garde (€)", "=100*B10/B9", "0.00")]
    for r, lab, v, fmt in lignes_calc:
        ws[f"A{r}"], ws[f"A{r}"].font = lab, F(bold=r >= 9)
        c = ws[f"B{r}"]
        if r <= 5:
            c.value, c.font, c.fill = v, F(bold=True, color="0000FF", size=12), PatternFill("solid", fgColor="FFFF00")
        elif not exercice:
            c.value = v
        c.number_format = fmt
        if r >= 9:
            c.font = F(bold=True, size=12, color=ORANGE if r >= 10 else "1B1F27")
    ws["A13"], ws["A13"].font = "Exemple : Adesanya vs Pyfer, mars 2026 (cotes américaines −130 / +102).", F(italic=True, color="666666")
    ws.column_dimensions["A"].width, ws.column_dimensions["B"].width = 44, 14
    if exercice:
        a_faire(ws, "B7:B11")
    page_image(ws, "A1:D13")

    # --- Combats + Simulateur
    ecrire_csv(CSV, "combats.csv", ["cote_rouge", "cote_bleu", "rouge_gagne", "annee"], C)
    wc = wb.create_sheet("Combats")
    titre(wc, "Les combats UFC et leurs cotes (décimales)", "Source : Ultimate UFC Dataset, 2010-2026.")
    entetes(wc, 4, ["Cote rouge", "Cote bleu", "Rouge gagne (1 = oui)", "Année"])
    for i, row in enumerate(C, 5):
        for j, v in enumerate(row, 1):
            wc.cell(row=i, column=j, value=v)
    NB = len(C)
    ws = wb.create_sheet("Simulateur", 2)
    titre(ws, "Simulateur : un parieur, 100 paris, touche F9 pour relancer",
          "Chaque ligne tire un vrai combat au hasard (onglet Combats), choisit un camp au hasard et applique la vraie cote et le vrai résultat.",
          "À faire : les formules des colonnes B à F et H (étape 5), puis la courbe de la cagnotte." if exercice else None)
    ws["A4"], ws["A4"].font = "Mise par pari (€) :", F(bold=True)
    ws["C4"], ws["C4"].font, ws["C4"].fill = 10, F(bold=True, color="0000FF"), PatternFill("solid", fgColor="FFFF00")
    ws["C4"].comment = Comment("Modifiez la mise ici.", "Alvin")
    ws["E4"], ws["E4"].font = "Bilan final :", F(bold=True)
    entetes(ws, 5, ["Pari n°", "Ligne du combat", "Camp", "Cote", "Gagné ?", "Gain (€)", "", "Cagnotte (€)"],
            {1: 9, 2: 15, 3: 9, 4: 9, 5: 10, 6: 11, 7: 3, 8: 14})
    ws["G5"].fill = PatternFill(fill_type=None)
    ws["A6"], ws["H6"] = 0, 0
    for i in range(7, 107):
        ws[f"A{i}"] = i - 6
        if not exercice:
            ws[f"B{i}"] = f"=RANDBETWEEN(5,{4 + NB})"
            ws[f"C{i}"] = '=IF(RAND()<0.5,"rouge","bleu")'
            ws[f"D{i}"] = f'=IF(C{i}="rouge",INDEX(Combats!A:A,B{i}),INDEX(Combats!B:B,B{i}))'
            ws[f"E{i}"] = f'=IF(C{i}="rouge",INDEX(Combats!C:C,B{i})=1,INDEX(Combats!C:C,B{i})=0)'
            ws[f"F{i}"] = f"=IF(E{i},$C$4*(D{i}-1),-$C$4)"
            ws[f"H{i}"] = f"=H{i - 1}+F{i}"
        ws[f"F{i}"].number_format = ws[f"H{i}"].number_format = "#,##0.00"
    if exercice:
        a_faire(ws, "B7:F106"); a_faire(ws, "H7:H106")
    else:
        ws["F4"], ws["F4"].number_format, ws["F4"].font = "=H106", '+#,##0 "€";-#,##0 "€"', F(bold=True)
        lc = LineChart()
        lc.add_data(Reference(ws, min_col=8, min_row=5, max_row=106), titles_from_data=True)
        lc.set_categories(Reference(ws, min_col=1, min_row=6, max_row=106))
        lc.series[0].graphicalProperties.line.solidFill, lc.series[0].graphicalProperties.line.width = ORANGE, 28575
        lc.series[0].smooth = False
        lc.x_axis.tickLblSkip = 10
        lc.x_axis.tickLblPos = "low"
        onglet_graphique(wb, "G5 Simulateur", styler(lc, "La cagnotte d'un parieur, pari après pari (F9 = un nouveau parieur)", "Pari n°", "€", legende=False))

    # --- 1 000 parieurs : chaque côté de chaque combat devient un pari possible, avec son gain pour 10 €
    wp = wb.create_sheet("Paris")
    titre(wp, "Tous les paris possibles (les deux camps de chaque combat)", "Gain = ce que rapporte un pari de 10 € : 10 × (cote − 1) s'il gagne, −10 sinon.",
          "À faire : la colonne C (étape 7.1)." if exercice else None)
    entetes(wp, 4, ["Cote", "Gagné (1 = oui)", "Gain pour 10 € (€)"])
    paris_possibles = [(cr, g) for cr, cb, g, _ in C] + [(cb, 1 - g) for cr, cb, g, _ in C]
    for i, (cote, g) in enumerate(paris_possibles, 5):
        wp.cell(row=i, column=1, value=cote); wp.cell(row=i, column=2, value=g)
        if not exercice:
            wp.cell(row=i, column=3, value=f"=IF(B{i}=1,10*(A{i}-1),-10)").number_format = "0.00"
    NP = len(paris_possibles)
    if exercice:
        a_faire(wp, "C5:C12")
    wm = wb.create_sheet("1000 parieurs")
    titre(wm, "1 000 parieurs, 100 paris chacun (F9 = on recommence)", "Chaque case tire un pari au hasard dans l'onglet Paris. Colonne CX : le bilan de chaque parieur.",
          "À faire : la formule de B5, recopiée sur 100 colonnes et 1 000 lignes, puis la colonne CX (étape 7.2)." if exercice else None)
    wm["A4"], wm["CX4"] = "Parieur", "Bilan (€)"
    for c in ("A4", "CX4"):
        wm[c].font, wm[c].fill = F(bold=True, color="FFFFFF"), ENTETE
    for j in range(2, 102):
        wm.cell(row=4, column=j, value=j - 1).font = F(bold=True, size=8)
    for i in range(5, 1005):
        wm.cell(row=i, column=1, value=i - 4)
        if not exercice:
            for j in range(2, 102):
                wm.cell(row=i, column=j, value=f"=INDEX(Paris!$C$5:$C${4 + NP},RANDBETWEEN(1,{NP}))")
            wm.cell(row=i, column=102, value=f"=SUM(B{i}:CW{i})").number_format = "0"
    if exercice:
        a_faire(wm, "B5:F7"); a_faire(wm, "CX5:CX7")
    wd = wb.create_sheet("Distribution")
    titre(wd, "Combien de parieurs finissent gagnants ?", "On compte les bilans par tranche de 50 € (NB.SI.ENS).",
          "À faire : les colonnes C et les indicateurs (étape 7.3), puis l'histogramme." if exercice else None)
    entetes(wd, 4, ["De (€)", "À (€)", "Parieurs", "Tranche"], {4: 16})
    bornes = list(range(-600, 551, 50))
    for k, b in enumerate(bornes[:-1]):
        i = 5 + k
        wd.cell(row=i, column=1, value=b); wd.cell(row=i, column=2, value=bornes[k + 1])
        wd.cell(row=i, column=4, value=f"{b} à {bornes[k + 1]}")
        if not exercice:
            wd.cell(row=i, column=3, value=f"=COUNTIFS('1000 parieurs'!$CX$5:$CX$1004,\">=\"&A{i},'1000 parieurs'!$CX$5:$CX$1004,\"<\"&B{i})")
    fin_d = 4 + len(bornes) - 1
    for r, lab, f, fmt in ((fin_d + 2, "Parieurs gagnants", "=COUNTIF('1000 parieurs'!CX5:CX1004,\">0\")/1000", "0%"),
                           (fin_d + 3, "Bilan médian (€)", "=MEDIAN('1000 parieurs'!CX5:CX1004)", "0"),
                           (fin_d + 4, "Le plus chanceux (€)", "=MAX('1000 parieurs'!CX5:CX1004)", "0")):
        wd[f"A{r}"], wd[f"A{r}"].font = lab, F(bold=True)
        wd[f"C{r}"].number_format = fmt
        if not exercice:
            wd[f"C{r}"] = f
    if exercice:
        a_faire(wd, f"C5:C{fin_d}"); a_faire(wd, f"C{fin_d + 2}:C{fin_d + 4}")
    else:
        ch = BarChart(); ch.gapWidth = 15
        ch.add_data(Reference(wd, min_col=3, min_row=4, max_row=fin_d), titles_from_data=True)
        ch.set_categories(Reference(wd, min_col=1, min_row=5, max_row=fin_d))
        remplir(ch.series[0], BLEU)
        ch.series[0].dPt += [point(k, ORANGE) for k, b in enumerate(bornes[:-1]) if bornes[k + 1] <= 0]
        ch.x_axis.tickLblSkip = 2
        onglet_graphique(wb, "G6 Distribution", styler(ch, "1 000 parieurs, 100 paris de 10 € : orange = perdants, bleu = gagnants", "Bilan final (€, début de tranche)", "Parieurs", legende=False))
    return wb


# ============================================================== Étude 2
def nba(exercice):
    D = RACINE / "projets/nba-mi-distance"
    R = json.loads((D / "resultats.json").read_text())
    T = json.loads((D / "terrain.json").read_text())
    ZONES = ["Sous le panier", "Raquette", "Mi-distance", "3 pts dans le coin", "3 pts dans l'axe"]
    S = list(R["part_par_zone"])
    CSV = D / "excel/csv"
    wb = Workbook()
    lisez_moi(wb, [
        "Le tir que la NBA a arrêté de financer · " + ("EXERCICE" if exercice else "CORRIGÉ"),
        "",
        "Exercice : les cellules jaunes sont à remplir, les graphiques à construire. Suivez TUTO.md (ou la page Tuto du site), étape par étape."
        if exercice else "Corrigé : toutes les formules sont en place, et chaque graphique a son onglet (G1 à G3). Ce sont ces graphiques qui sont sur le site.",
        "",
        "Les onglets",
        "• Parts : part des tirs par zone, saison par saison, et les trois grandes zones (formules).",
        "• Rendement : points rapportés par tir, par zone et par saison.",
        "• Decomposition : « mieux tirer ou tirer au bon endroit ? », entièrement en formules (SOMMEPROD).",
        "• Correlation : lien entre part de mi-distance d'une équipe et son rendement, saison par saison.",
        "• Terrain 2004 / Terrain 2025 : la carte des tirs en carte de chaleur (mise en forme conditionnelle).",
        "",
        "Source : NBA.com, via github.com/DomSamangy/NBA_Shots_04_25 (4,4 millions de tirs, 2003-04 à 2024-25).",
    ])

    # --- Parts
    rows = [[s] + [R["part_par_zone"][s][z] for z in ZONES] for s in S]
    ecrire_csv(CSV, "parts_par_zone.csv", ["saison"] + ZONES, rows)
    ws = wb.create_sheet("Parts")
    titre(ws, "Part des tirs par zone, saison par saison", "Source : NBA.com. Lancers francs exclus.",
          "À faire : colonnes G, H, I (étape 1.1), puis le graphique en courbes (étape 1.2)." if exercice else None)
    entetes(ws, 4, ["Saison"] + ZONES + ["Près du panier", "3 points", "Mi-distance"])
    fin = 4 + len(S)
    for i, row in enumerate(rows, 5):
        ws.cell(row=i, column=1, value=row[0])
        for j, v in enumerate(row[1:], 2):
            ws.cell(row=i, column=j, value=v).number_format = "0.0%"
        for col in "GHI":
            ws[f"{col}{i}"].number_format = "0.0%"
        if not exercice:
            ws[f"G{i}"], ws[f"H{i}"], ws[f"I{i}"] = f"=B{i}+C{i}", f"=E{i}+F{i}", f"=D{i}"
    if exercice:
        a_faire(ws, f"G5:I{fin}")
    else:
        lc = LineChart()
        for col in (7, 8, 9):
            lc.add_data(Reference(ws, min_col=col, min_row=4, max_row=fin), titles_from_data=True)
        lc.set_categories(Reference(ws, min_col=1, min_row=5, max_row=fin))
        for s, coul, w, dash in zip(lc.series, (GRIS, BLEU, ORANGE), (22225, 34925, 34925), ("dash", None, None)):
            s.graphicalProperties.line.solidFill, s.graphicalProperties.line.width = coul, w
            if dash:
                s.graphicalProperties.line.dashStyle = dash
            s.smooth = False
        lc.x_axis.tickLblSkip = 3
        lc.y_axis.scaling.min, lc.y_axis.scaling.max = 0, .55
        onglet_graphique(wb, "G1 Parts", styler(lc, "Part des tirs NBA : le mi-distance s'efface", "Saison", "Part des tirs", num="0%"))

    # --- Rendement
    rows = [[s] + [R["rendement_par_zone"][s][z] for z in ZONES] for s in S]
    ecrire_csv(CSV, "rendement_par_zone.csv", ["saison"] + ZONES, rows)
    ws = wb.create_sheet("Rendement")
    titre(ws, "Points rapportés par tir, par zone et par saison", "Source : NBA.com. Rendement = points marqués / tirs tentés.",
          "À faire : le petit tableau H4:J9 puis le graphique en barres (étape 2)." if exercice else None)
    entetes(ws, 4, ["Saison"] + ZONES)
    for i, row in enumerate(rows, 5):
        ws.cell(row=i, column=1, value=row[0])
        for j, v in enumerate(row[1:], 2):
            ws.cell(row=i, column=j, value=v).number_format = "0.00"
    fin = 4 + len(S)
    for c, v in (("H4", "Zone"), ("I4", S[0]), ("J4", S[-1])):
        ws[c], ws[c].font, ws[c].fill = v, F(bold=True, color="FFFFFF"), ENTETE
    for k, z in enumerate(ZONES):
        col = get_column_letter(2 + k)
        ws[f"H{5 + k}"] = z
        if not exercice:
            ws[f"I{5 + k}"], ws[f"J{5 + k}"] = f"={col}5", f"={col}{fin}"
        ws[f"I{5 + k}"].number_format = ws[f"J{5 + k}"].number_format = "0.00"
    ws.column_dimensions["H"].width = 20
    if exercice:
        a_faire(ws, "I5:J9")
    else:
        ch = BarChart(); ch.type, ch.gapWidth = "bar", 50
        ch.add_data(Reference(ws, min_col=9, max_col=10, min_row=4, max_row=9), titles_from_data=True)
        ch.set_categories(Reference(ws, min_col=8, min_row=5, max_row=9))
        remplir(ch.series[0], GRIS); remplir(ch.series[1], ORANGE)
        etiquettes(ch.series[1], "0.00")
        ch.x_axis.scaling.orientation = "maxMin"
        onglet_graphique(wb, "G2 Rendement", styler(ch, "Points rapportés par tir, selon la zone", None, "Points par tir", num="0.0"))

    # --- Décomposition
    ws = wb.create_sheet("Decomposition")
    titre(ws, "Mieux tirer, ou tirer au bon endroit ? (décomposition mix / adresse)",
          "Tout se calcule à partir des onglets Parts et Rendement (première et dernière saison).",
          "À faire : colonnes B à E, puis les cellules B12 à B19 (étape 3, formule SOMMEPROD)." if exercice else None)
    entetes(ws, 4, ["Zone", f"Part {S[0]}", f"Part {S[-1]}", f"Rendement {S[0]}", f"Rendement {S[-1]}"], {1: 62, 2: 16, 3: 16, 4: 18, 5: 18})
    for k, z in enumerate(ZONES):
        i, col = 5 + k, get_column_letter(2 + k)
        ws[f"A{i}"] = z
        if not exercice:
            ws[f"B{i}"], ws[f"C{i}"] = f"=Parts!{col}5", f"=Parts!{col}{fin}"
            ws[f"D{i}"], ws[f"E{i}"] = f"=Rendement!{col}5", f"=Rendement!{col}{fin}"
        for c2, f2 in (("B", "0.0%"), ("C", "0.0%"), ("D", "0.000"), ("E", "0.000")):
            ws[f"{c2}{i}"].number_format = f2
    calc = [("Rendement global, première saison", "=SUMPRODUCT(B5:B9,D5:D9)"),
            ("Rendement global, dernière saison", "=SUMPRODUCT(C5:C9,E5:E9)"),
            ("Hausse totale (point par tir)", "=B13-B12"),
            ("Effet mix : on tire au bon endroit", "=SUMPRODUCT(C5:C9-B5:B9,D5:D9)"),
            ("Effet adresse : on tire mieux", "=SUMPRODUCT(B5:B9,E5:E9-D5:D9)"),
            ("Interaction", "=SUMPRODUCT(C5:C9-B5:B9,E5:E9-D5:D9)"),
            ("Part du gain due au mix", "=B15/B14"),
            ("Contrôle : mix + adresse + interaction − hausse (doit faire 0)", "=ROUND(B15+B16+B17-B14,10)")]
    for k, (lab, f) in enumerate(calc):
        i = 12 + k
        ws[f"A{i}"], ws[f"A{i}"].font = lab, F(bold=k in (2, 3, 6))
        if not exercice:
            ws[f"B{i}"] = f
        ws[f"B{i}"].number_format = "0.0%" if k == 6 else "0.000"
    if exercice:
        a_faire(ws, "B5:E9"); a_faire(ws, "B12:B19")

    # --- Corrélation
    rows = [[s, R["correlation_mi_distance_rendement"][s], R["equipe_avec_le_moins_de_mi_distance"][s]] for s in S]
    ecrire_csv(CSV, "correlation_equipes.csv", ["saison", "correlation", "equipe_moins_de_mi_distance"], rows)
    ws = wb.create_sheet("Correlation")
    titre(ws, "Corrélation entre part de mi-distance et rendement des équipes", "30 équipes par saison. Sous zéro : moins de mi-distance = plus efficace.",
          "À faire : le graphique (étape 4), barres négatives en bleu et positives en orange." if exercice else None)
    entetes(ws, 4, ["Saison", "Corrélation", "Équipe avec le moins de mi-distance"], {3: 36})
    for i, row in enumerate(rows, 5):
        ws.cell(row=i, column=1, value=row[0]); ws.cell(row=i, column=2, value=row[1]).number_format = "0.00"; ws.cell(row=i, column=3, value=row[2])
    if not exercice:
        ch = BarChart(); ch.gapWidth = 40
        ch.add_data(Reference(ws, min_col=2, min_row=4, max_row=fin), titles_from_data=True)
        ch.set_categories(Reference(ws, min_col=1, min_row=5, max_row=fin))
        s = ch.series[0]; remplir(s, BLEU); s.invertIfNegative = False
        s.dPt += [point(k, ORANGE) for k, row in enumerate(rows) if row[1] > 0]
        ch.x_axis.tickLblPos = "low"
        ch.x_axis.tickLblSkip = 3
        onglet_graphique(wb, "G3 Correlation", styler(ch, "Moins de mi-distance = plus efficace ? Plus vraiment.", "Saison", "Corrélation", legende=False, num="0.0"))

    # --- Terrain
    rows = []
    for s_, cells in T["saisons"].items():
        for cy, cx, part, pps in cells:
            rows.append([f"{int(s_) - 1}-{str(s_)[2:]}", cx * 2 - 25 + 1, cy * 2 + 1, round(part / 1000, 5), pps])
    ecrire_csv(CSV, "terrain.csv", ["saison", "x_pieds", "y_pieds", "part_des_tirs", "points_par_tir"], rows)
    for s_ in ("2004", "2025"):
        ws = wb.create_sheet(f"Terrain {s_}")
        titre(ws, f"Carte des tirs {int(s_) - 1}-{s_[2:]} : part des tirs (‰) par case de 2 × 2 pieds",
              "Ligne du haut = au niveau du panier. Plus c'est rouge, plus on tire de là. Même échelle de couleurs pour les deux saisons.",
              "À faire : la mise en forme conditionnelle (étape 5)." if exercice else None)
        grid = {(cy, cx): part for cy, cx, part, _ in T["saisons"][s_]}
        for cx in range(T["colonnes"]):
            ws.cell(row=4, column=2 + cx, value=cx * 2 - 24).font = F(bold=True, size=8)
            ws.column_dimensions[get_column_letter(2 + cx)].width = 5.5
        for cy in range(T["lignes"]):
            ws.cell(row=5 + cy, column=1, value=cy * 2 + 1).font = F(bold=True, size=8)
            for cx in range(T["colonnes"]):
                v = grid.get((cy, cx))
                c = ws.cell(row=5 + cy, column=2 + cx, value=round(v, 1) if v else None)
                c.font, c.number_format = F(size=8), "0.0"
        page_image(ws, f"A1:{get_column_letter(1 + T['colonnes'])}{4 + T['lignes']}")
        if not exercice:
            rng = f"B5:{get_column_letter(1 + T['colonnes'])}{4 + T['lignes']}"
            ws.conditional_formatting.add(rng, ColorScaleRule(start_type="num", start_value=0, start_color="FFFFFF",
                                                              mid_type="num", mid_value=10, mid_color="F4B183",
                                                              end_type="num", end_value=40, end_color="C0392B"))  # même échelle les deux années
    return wb


# ============================================================== Génération
RECALC = Path("/root/.claude/skills/synced/76f4f0b5-c16a-4277-a0bb-404ffdef9bac_5aa74d49-1dd6-4941-8f31-714f6152e5bc/xlsx/scripts/recalc.py")

if __name__ == "__main__":
    for nom, fab, graphes in (
        ("ufc-paris", paris, {"G1 Argent": "G1-argent.png", "G2 Evenements": "G2-evenements.png", "G3 Calibration": "G3-calibration.png",
                              "G4 Rendement": "G4-rendement.png", "G5 Simulateur": "G5-simulateur.png",
                              "Calculatrice": "calculatrice.png", "G6 Distribution": "G6-distribution.png"}),
    ):
        dossier = RACINE / "projets" / nom / "excel"
        dossier.mkdir(parents=True, exist_ok=True)
        for exo in (False, True):
            f = dossier / f"{nom}-{'exercice' if exo else 'corrige'}.xlsx"
            fab(exo).save(f)
            if RECALC.exists():  # calcule les formules pour que les valeurs s'affichent partout (aperçus, mobile...)
                print(f.name, subprocess.run(["python3", str(RECALC), str(f), "120"], capture_output=True, text=True).stdout.split('"status": ')[1][:16])
        exporter_graphiques(dossier / f"{nom}-corrige.xlsx", dossier / "graphiques", graphes)
        print(nom, "graphiques exportés")
