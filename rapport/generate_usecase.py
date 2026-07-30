"""Génère le diagramme de cas d'utilisation professionnel."""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse

OUT = Path(__file__).parent / "diagrammes" / "figure_2_4_cas_utilisation.png"
NAVY, TEAL, SLATE, WHITE, BORDER, ACCENT = (
    "#000000", "#222222", "#111111", "#FFFFFF", "#666666", "#000000",
)

fig, ax = plt.subplots(figsize=(12.5, 8.5))
ax.set_xlim(0, 12.5)
ax.set_ylim(0, 8.5)
ax.axis("off")
ax.set_title(
    "Diagramme de cas d'utilisation (généralisation des acteurs)",
    fontsize=13, fontweight="bold", color=NAVY, pad=8,
)

ax.add_patch(FancyBboxPatch(
    (2.2, 0.4), 8.2, 7.5,
    boxstyle="square,pad=0.01",
    fc="#F5F5F5", ec=NAVY, lw=1.4, ls="--",
))
ax.text(6.3, 7.7, "Plateforme de gestion des connaissances",
        ha="center", fontsize=9, color=NAVY, fontweight="bold")


def actor(x, y, label):
    ax.add_patch(plt.Circle((x, y + 0.55), 0.12, fc=WHITE, ec=NAVY, lw=1.2))
    ax.plot([x, x], [y + 0.43, y + 0.15], color=NAVY, lw=1.2)
    ax.plot([x - 0.18, x + 0.18], [y + 0.35, y + 0.35], color=NAVY, lw=1.2)
    ax.plot([x, x - 0.15], [y + 0.15, y], color=NAVY, lw=1.2)
    ax.plot([x, x + 0.15], [y + 0.15, y], color=NAVY, lw=1.2)
    ax.text(x, y - 0.25, label, ha="center", fontsize=8, fontweight="bold", color=SLATE)


def uc(x, y, w, h, text):
    ax.add_patch(Ellipse((x, y), w, h, fc=WHITE, ec=TEAL, lw=1.2, zorder=2))
    ax.text(x, y, text, ha="center", va="center", fontsize=6.8, color=SLATE, zorder=3)


def include(a, b):
    ax.annotate(
        "", xy=b, xytext=a,
        arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=1, ls="--"),
    )
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    ax.text(mx + 0.15, my, "«include»", fontsize=5.5, color=ACCENT, style="italic")


actor(0.9, 4.2, "Employé")
actor(0.9, 6.3, "Manager")
actor(0.9, 7.5, "Administrateur")

ax.annotate("", xy=(0.9, 6.95), xytext=(0.9, 7.35),
            arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.2, mutation_scale=14))
ax.annotate("", xy=(0.9, 5.0), xytext=(0.9, 6.05),
            arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.2, mutation_scale=14))
ax.text(1.15, 5.5, "généralisation", fontsize=6, color="#555555", rotation=90, va="center")

ucs_emp = [
    (4.0, 7.1, 2.4, 0.55, "S'authentifier"),
    (4.0, 6.35, 2.4, 0.55, "Consulter les ressources"),
    (4.0, 5.6, 2.4, 0.55, "Télécharger un document"),
    (4.0, 4.85, 2.4, 0.55, "Poser une question\nà l'assistant"),
    (4.0, 4.05, 2.4, 0.55, "Consulter les sources\nde la réponse"),
    (4.0, 3.25, 2.4, 0.55, "Consulter l'historique\ndes sessions"),
]
ucs_mgr = [
    (7.0, 6.5, 2.5, 0.55, "Ajouter une ressource"),
    (7.0, 5.7, 2.5, 0.55, "Indexer la ressource"),
    (7.0, 4.9, 2.5, 0.55, "Modifier sa ressource"),
    (7.0, 4.1, 2.5, 0.55, "Supprimer sa ressource"),
    (7.0, 3.3, 2.5, 0.55, "Publier une annonce\ninterne"),
    (7.0, 2.5, 2.5, 0.55, "Supprimer de la\nbase vectorielle"),
]
ucs_adm = [
    (9.8, 6.3, 2.3, 0.55, "Gérer les utilisateurs"),
    (9.8, 5.5, 2.3, 0.55, "Gérer les rôles"),
    (9.8, 4.7, 2.3, 0.55, "Gérer les catégories"),
    (9.8, 3.9, 2.3, 0.55, "Consulter le\ntableau de bord"),
]

for x, y, w, h, t in ucs_emp + ucs_mgr + ucs_adm:
    uc(x, y, w, h, t)

for _, y, *_ in ucs_emp:
    ax.plot([1.2, 2.8], [4.6, y], color=BORDER, lw=0.8, zorder=1)
for _, y, *_ in ucs_mgr:
    ax.plot([1.2, 5.75], [6.7, y], color=BORDER, lw=0.7, zorder=1)
for _, y, *_ in ucs_adm:
    ax.plot([1.2, 8.65], [7.85, y], color=BORDER, lw=0.7, zorder=1)

include((7.0, 6.22), (7.0, 5.98))
include((7.0, 4.38), (7.0, 2.78))
include((4.0, 4.58), (4.0, 4.32))

ax.text(
    6.3, 0.7,
    "Note : l'Administrateur hérite du Manager, qui hérite de l'Employé.",
    ha="center", fontsize=7.5, color="#555555", style="italic",
)

fig.savefig(OUT, dpi=200, bbox_inches="tight", facecolor=WHITE)
plt.close(fig)
print(f"OK  {OUT}")
