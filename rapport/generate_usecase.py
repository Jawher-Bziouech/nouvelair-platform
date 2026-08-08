"""Genere 2 diagrammes de cas d'utilisation plus lisibles.

- Figure 2.4a : vue generale (acteurs -> macro-fonctions)
- Figure 2.4b : vue detaillee (cas principaux et relations include)
"""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse

DIAG = Path(__file__).parent / "diagrammes"
OUT_A = DIAG / "figure_2_4a_cas_utilisation_general.png"
OUT_B = DIAG / "figure_2_4b_cas_utilisation_detail.png"

NAVY, TEAL, SLATE, WHITE, BORDER, ACCENT, PURPLE = (
    "#0B5CAD", "#0E8A7D", "#243447", "#FFFFFF", "#7A93A8", "#E07A2F", "#6B5B95",
)
LAYER = "#EAF3FB"
UC_EMP = "#E3F0FB"
UC_MGR = "#E5F6F3"
UC_ADM = "#F0EAF8"
UC_EDGE_EMP = "#0B5CAD"
UC_EDGE_MGR = "#0E8A7D"
UC_EDGE_ADM = "#6B5B95"


def actor(ax, x, y, label):
    ax.add_patch(plt.Circle((x, y + 0.55), 0.12, fc=WHITE, ec=NAVY, lw=1.4))
    ax.plot([x, x], [y + 0.43, y + 0.15], color=NAVY, lw=1.4)
    ax.plot([x - 0.18, x + 0.18], [y + 0.35, y + 0.35], color=NAVY, lw=1.4)
    ax.plot([x, x - 0.15], [y + 0.15, y], color=NAVY, lw=1.4)
    ax.plot([x, x + 0.15], [y + 0.15, y], color=NAVY, lw=1.4)
    ax.text(x, y - 0.25, label, ha="center", fontsize=9, fontweight="bold", color=SLATE)


def uc(ax, x, y, w, h, text, fs=8.0, fc=WHITE, ec=TEAL):
    ax.add_patch(Ellipse((x, y), w, h, fc=fc, ec=ec, lw=1.5, zorder=2))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=SLATE, zorder=3)


def include(ax, a, b, dx=0.25):
    ax.annotate(
        "", xy=b, xytext=a,
        arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=1.2, ls="--"),
    )
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    ax.text(mx + dx, my, "«include»", fontsize=6.5, color=ACCENT, style="italic")


def generate_general():
    # Compact canvas: box tightly wraps the 4 use cases (no empty bottom)
    fig, ax = plt.subplots(figsize=(12.5, 6.2))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 6.2)
    ax.axis("off")
    ax.set_title(
        "Diagramme de cas d'utilisation - Vue generale",
        fontsize=13, fontweight="bold", color=NAVY, pad=8,
    )

    # System boundary fitted to content
    ax.add_patch(FancyBboxPatch(
        (2.5, 1.15), 8.6, 4.35,
        boxstyle="square,pad=0.01",
        fc=LAYER, ec=NAVY, lw=1.4, ls="--",
    ))
    ax.text(
        6.8, 5.25, "Plateforme de gestion des connaissances",
        ha="center", fontsize=10, color=NAVY, fontweight="bold",
    )

    # Actors: general on top, specialized below
    # Employe (base) -> Manager -> Administrateur
    actor(ax, 0.95, 4.55, "Employe")
    actor(ax, 0.95, 3.05, "Manager")
    actor(ax, 0.95, 1.55, "Administrateur")

    # UML generalisation: arrowhead points to the more general actor
    ax.annotate("", xy=(0.95, 4.20), xytext=(0.95, 3.70),
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.2, mutation_scale=14))
    ax.annotate("", xy=(0.95, 2.70), xytext=(0.95, 2.20),
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.2, mutation_scale=14))
    ax.text(1.25, 3.95, "herite", fontsize=7, color=BORDER, style="italic")
    ax.text(1.25, 2.45, "herite", fontsize=7, color=BORDER, style="italic")

    usecases = [
        (5.2, 4.55, 3.2, 0.9, "Consulter les ressources", UC_EMP, UC_EDGE_EMP),
        (9.0, 4.55, 3.2, 0.9, "Interroger l'assistant", UC_EMP, UC_EDGE_EMP),
        (7.1, 3.40, 3.4, 0.95, "Gerer les ressources", UC_MGR, UC_EDGE_MGR),
        (7.1, 1.90, 3.4, 0.95, "Administrer la plateforme", UC_ADM, UC_EDGE_ADM),
    ]
    for x, y, w, h, t, fc, ec in usecases:
        uc(ax, x, y, w, h, t, fs=9.0, fc=fc, ec=ec)

    # Associations
    ax.plot([1.25, 3.6], [4.95, 4.55], color=BORDER, lw=1.05)  # Employe -> Consulter
    ax.plot([1.25, 7.4], [4.95, 4.55], color=BORDER, lw=1.05)  # Employe -> Interroger
    ax.plot([1.25, 5.4], [3.40, 3.40], color=BORDER, lw=1.15)  # Manager -> Gerer
    ax.plot([1.25, 5.4], [1.95, 1.90], color=BORDER, lw=1.15)  # Admin -> Administrer

    ax.text(
        6.8, 0.45,
        "Generalisation : Manager = Employe + droits supplementaires ; "
        "Administrateur = Manager + droits d'administration.",
        ha="center", fontsize=7.5, color="#555555", style="italic",
    )

    fig.savefig(OUT_A, dpi=220, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)


def generate_detail():
    fig, ax = plt.subplots(figsize=(13, 8.0))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8.0)
    ax.axis("off")
    ax.set_title(
        "Diagramme de cas d'utilisation - Vue detaillee",
        fontsize=13, fontweight="bold", color=NAVY, pad=8,
    )

    # Boundary tightly fitted to content
    ax.add_patch(FancyBboxPatch(
        (2.3, 0.95), 9.5, 6.35,
        boxstyle="square,pad=0.01",
        fc=LAYER, ec=NAVY, lw=1.4, ls="--",
    ))
    ax.text(
        7.05, 7.05, "Plateforme de gestion des connaissances",
        ha="center", fontsize=10, color=NAVY, fontweight="bold",
    )

    actor(ax, 0.95, 6.0, "Employe")
    actor(ax, 0.95, 3.9, "Manager")
    actor(ax, 0.95, 1.8, "Administrateur")

    # Arrowhead points to more general actor (Employe <- Manager <- Admin)
    ax.annotate("", xy=(0.95, 5.65), xytext=(0.95, 4.55),
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.2, mutation_scale=14))
    ax.annotate("", xy=(0.95, 3.55), xytext=(0.95, 2.45),
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.2, mutation_scale=14))

    ucs_emp = [
        (4.55, 6.40, 2.7, 0.66, "S'authentifier"),
        (4.55, 5.35, 2.7, 0.66, "Consulter les ressources"),
        (4.55, 4.30, 2.7, 0.66, "Telecharger un document"),
        (4.55, 3.25, 2.7, 0.66, "Poser une question\na l'assistant"),
        (4.55, 2.05, 2.7, 0.66, "Consulter les sources"),
    ]
    ucs_mgr = [
        (7.55, 4.85, 2.8, 0.66, "Ajouter une ressource"),
        (7.55, 3.85, 2.8, 0.66, "Indexer la ressource"),
        (7.55, 2.85, 2.8, 0.66, "Modifier sa ressource"),
        (7.55, 1.85, 2.8, 0.66, "Supprimer sa ressource"),
    ]
    ucs_adm = [
        (10.55, 4.85, 2.6, 0.66, "Gerer les utilisateurs"),
        (10.55, 3.85, 2.6, 0.66, "Gerer les roles"),
        (10.55, 2.85, 2.6, 0.66, "Gerer les categories"),
        (10.55, 1.85, 2.6, 0.66, "Consulter le dashboard"),
    ]

    for x, y, w, h, t in ucs_emp:
        uc(ax, x, y, w, h, t, fs=7.8, fc=UC_EMP, ec=UC_EDGE_EMP)
    for x, y, w, h, t in ucs_mgr:
        uc(ax, x, y, w, h, t, fs=7.8, fc=UC_MGR, ec=UC_EDGE_MGR)
    for x, y, w, h, t in ucs_adm:
        uc(ax, x, y, w, h, t, fs=7.8, fc=UC_ADM, ec=UC_EDGE_ADM)

    for _, y, *_ in ucs_emp:
        ax.plot([1.25, 3.2], [6.4, y], color=BORDER, lw=0.9, zorder=1)
    for _, y, *_ in ucs_mgr:
        ax.plot([1.25, 6.15], [4.3, y], color=BORDER, lw=0.85, zorder=1)
    for _, y, *_ in ucs_adm:
        ax.plot([1.25, 9.25], [2.2, y], color=BORDER, lw=0.85, zorder=1)

    include(ax, (7.55, 4.52), (7.55, 4.18), dx=0.35)
    include(ax, (4.55, 2.92), (4.55, 2.38), dx=0.35)

    ax.text(
        7.05, 0.4,
        "Generalisation UML : Manager herite de l'Employe ; Administrateur herite du Manager.",
        ha="center", fontsize=8, color="#555555", style="italic",
    )

    fig.savefig(OUT_B, dpi=220, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)


if __name__ == "__main__":
    generate_general()
    generate_detail()
    print(f"OK  {OUT_A}")
    print(f"OK  {OUT_B}")
