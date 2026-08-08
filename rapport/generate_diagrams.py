"""
Génère les figures professionnelles pour le rapport de stage Nouvelair.
Sorties PNG dans rapport/diagrammes/
"""
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D

OUT = Path(__file__).parent / "diagrammes"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.family"] = "serif"
plt.rcParams["axes.unicode_minus"] = False

# Palette couleur Nouvelair (figures)
NAVY = "#0B5CAD"
TEAL = "#0E8A7D"
SLATE = "#243447"
LIGHT = "#EEF5FB"
BORDER = "#7A93A8"
ACCENT = "#E07A2F"
PURPLE = "#6B5B95"
GREEN = "#2E7D4F"
WHITE = "#FFFFFF"
SOFT = "#F7FAFD"
LAYER_A = "#E3F0FB"   # présentation (bleu clair)
LAYER_B = "#E5F6F3"   # application (teal clair)
LAYER_C = "#FFF0E4"   # données (orange clair)
LAYER_D = "#F0EAF8"   # IA (violet clair)
BOX_A = "#D6E9F8"
BOX_B = "#CDEEE9"
BOX_C = "#FFE2C8"
BOX_D = "#E4D9F5"


def save(fig, name: str):
    path = OUT / name
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor=WHITE, edgecolor="none")
    plt.close(fig)
    print(f"OK  {path}")


def rounded_box(ax, xy, w, h, text, *, fc=LIGHT, ec=NAVY, fontsize=9, bold=False, sub=None):
    x, y = xy
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="square,pad=0.01",
        linewidth=1.2, facecolor=fc, edgecolor=ec, zorder=2,
    )
    ax.add_patch(box)
    weight = "bold" if bold else "normal"
    if sub:
        ax.text(x + w / 2, y + h * 0.62, text, ha="center", va="center",
                fontsize=fontsize, fontweight=weight, color=SLATE, zorder=3,
                fontfamily="serif")
        ax.text(x + w / 2, y + h * 0.28, sub, ha="center", va="center",
                fontsize=fontsize - 1.5, color="#444444", zorder=3, style="italic",
                fontfamily="serif")
    else:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fontsize, fontweight=weight, color=SLATE, zorder=3,
                wrap=True, fontfamily="serif")
    return box


def arrow(ax, start, end, *, color=NAVY, style="-|>", rad=0):
    ax.annotate(
        "", xy=end, xytext=start,
        arrowprops=dict(
            arrowstyle=style, color=color, lw=1.5,
            connectionstyle=f"arc3,rad={rad}",
        ),
        zorder=1,
    )


# ─────────────────────────────────────────────────────────────
# Figure 2.1 — Architecture générale
# ─────────────────────────────────────────────────────────────
def fig_architecture():
    fig, ax = plt.subplots(figsize=(10.5, 7.2))
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 7.2)
    ax.axis("off")
    ax.set_title(
        "Architecture générale de la solution",
        fontsize=13, fontweight="bold", color=NAVY, pad=12,
    )

    # Couche présentation
    ax.add_patch(FancyBboxPatch((0.4, 5.7), 9.7, 1.2,
                                boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc=LAYER_A, ec=NAVY, lw=1.4, ls="--", zorder=0))
    ax.text(0.55, 6.7, "Couche présentation", fontsize=8, color=NAVY, fontweight="bold")
    rounded_box(ax, (3.2, 5.9), 4.1, 0.75, "Angular — Interface Web",
                fc=BOX_A, ec=NAVY, fontsize=10, bold=True,
                sub="Employé · Manager · Administrateur")

    # Flèche REST
    arrow(ax, (5.25, 5.9), (5.25, 5.15), color=TEAL)
    ax.text(5.55, 5.45, "REST / HTTPS", fontsize=8, color=TEAL, fontweight="bold")

    # Couche application
    ax.add_patch(FancyBboxPatch((0.4, 3.55), 9.7, 1.55,
                                boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc=LAYER_B, ec=TEAL, lw=1.4, ls="--", zorder=0))
    ax.text(0.55, 4.9, "Couche application", fontsize=8, color=TEAL, fontweight="bold")
    rounded_box(ax, (2.6, 3.8), 5.3, 0.95, "FastAPI — Backend Python",
                fc=BOX_B, ec=TEAL, fontsize=10, bold=True,
                sub="API REST · Auth · Services métier · Orchestration IA")

    # Flèches vers persistance / IA
    arrow(ax, (3.5, 3.8), (2.2, 2.95), color=ACCENT)
    arrow(ax, (6.8, 3.8), (8.0, 2.95), color=PURPLE)

    # Couche données
    ax.add_patch(FancyBboxPatch((0.4, 0.35), 4.4, 2.45,
                                boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc=LAYER_C, ec=ACCENT, lw=1.4, ls="--", zorder=0))
    ax.text(0.55, 2.55, "Persistance métier", fontsize=8, color=ACCENT, fontweight="bold")
    rounded_box(ax, (0.85, 1.35), 3.5, 0.95, "MySQL",
                fc=BOX_C, ec=ACCENT, fontsize=10, bold=True,
                sub="Utilisateurs · Rôles · Ressources · Catégories")

    # Couche IA
    ax.add_patch(FancyBboxPatch((5.5, 0.35), 4.6, 2.45,
                                boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc=LAYER_D, ec=PURPLE, lw=1.4, ls="--", zorder=0))
    ax.text(5.65, 2.55, "Module intelligence artificielle", fontsize=8, color=PURPLE, fontweight="bold")
    rounded_box(ax, (5.9, 1.55), 3.8, 0.75, "LangChain — Pipeline RAG",
                fc=BOX_D, ec=PURPLE, fontsize=9, bold=True)
    rounded_box(ax, (5.9, 0.55), 1.7, 0.75, "ChromaDB",
                fc=WHITE, ec=PURPLE, fontsize=9, bold=True, sub="Vecteurs")
    rounded_box(ax, (7.85, 0.55), 1.85, 0.75, "LLM",
                fc=WHITE, ec=PURPLE, fontsize=9, bold=True, sub="Génération")
    arrow(ax, (7.0, 1.55), (6.75, 1.3), color=PURPLE)
    arrow(ax, (8.5, 1.55), (8.7, 1.3), color=PURPLE)

    save(fig, "figure_2_1_architecture.png")


def fig_connecteurs():
    fig, ax = plt.subplots(figsize=(11.2, 5.2))
    ax.set_xlim(0, 11.2)
    ax.set_ylim(0, 5.2)
    ax.axis("off")
    ax.set_title(
        "Interconnexion de la plateforme Nouvelair",
        fontsize=13, fontweight="bold", color=NAVY, pad=8,
    )
    ax.text(
        5.6, 4.75,
        "Consolidation de LATA Aviation eLearning, Ideagen Luminate et AirbusWorld",
        ha="center", fontsize=9, color=BORDER, style="italic",
    )

    sources = [
        (0.4, 3.35, "LATA Aviation eLearning", LAYER_A, NAVY, "API LATA"),
        (0.4, 2.05, "Ideagen Luminate", LAYER_B, TEAL, "API Ideagen"),
        (0.4, 0.75, "AirbusWorld", LAYER_C, ACCENT, "API Airbus"),
    ]
    for x, y, label, fc, ec, api in sources:
        rounded_box(ax, (x, y), 3.4, 0.85, label, fc=fc, ec=ec, fontsize=9.5, bold=True)
        mid_y = y + 0.42
        ax.annotate(
            "", xy=(6.0, 2.55), xytext=(x + 3.45, mid_y),
            arrowprops=dict(arrowstyle="-|>", color=ec, lw=1.4),
        )
        ax.text(
            (x + 3.45 + 6.0) / 2, mid_y + 0.18, api,
            ha="center", fontsize=7.5, color=ec, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.18", fc=WHITE, ec=ec, lw=1.0),
        )

    rounded_box(
        ax, (6.1, 1.55), 4.6, 2.0,
        "Plateforme Nouvelair KB",
        fc=BOX_A, ec=NAVY, fontsize=11, bold=True,
        sub="Front + Back Office + API\nPoint d'accès unifié",
    )
    ax.add_patch(FancyBboxPatch(
        (0.4, 0.12), 10.4, 0.42,
        boxstyle="round,pad=0.01,rounding_size=0.04",
        fc=SOFT, ec=BORDER, lw=0.9, zorder=2,
    ))
    ax.text(
        5.6, 0.33,
        "Intégration via API REST : synchronisation des métadonnées et références documentaires",
        ha="center", fontsize=8, color=SLATE, zorder=3,
    )
    save(fig, "figure_2_1b_connecteurs_nouvelair.png")

# ─────────────────────────────────────────────────────────────
# Figure 2.2 — Pipeline assistant
# ─────────────────────────────────────────────────────────────
def fig_pipeline():
    fig, ax = plt.subplots(figsize=(11.5, 3.8))
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 3.8)
    ax.axis("off")
    ax.set_title(
        "Pipeline de l'assistant intelligent (RAG)",
        fontsize=13, fontweight="bold", color=NAVY, pad=10,
    )

    steps = [
        ("1", "Question\nutilisateur", "Angular"),
        ("2", "Endpoint IA", "FastAPI"),
        ("3", "Recherche\nvectorielle", "similarité"),
        ("4", "Passages\npertinents", "ChromaDB"),
        ("5", "Contexte +\nprompt", "LangChain"),
        ("6", "Génération", "LLM"),
        ("7", "Réponse +\ncitations", "UI"),
    ]
    w, h = 1.25, 1.55
    y = 1.15
    gap = 0.28
    x0 = 0.35

    for i, (num, title, sub) in enumerate(steps):
        x = x0 + i * (w + gap)
        if i in (0, 6):
            fc, ec, badge = LAYER_A, NAVY, NAVY
        elif i in (1, 2, 4):
            fc, ec, badge = LAYER_B, TEAL, TEAL
        else:
            fc, ec, badge = LAYER_D, PURPLE, PURPLE
        rounded_box(ax, (x, y), w, h, title, fc=fc, ec=ec, fontsize=8.5, bold=True, sub=sub)
        circ = plt.Circle((x + 0.18, y + h - 0.18), 0.14, fc=badge, ec=badge, zorder=4)
        ax.add_patch(circ)
        ax.text(x + 0.18, y + h - 0.18, num, ha="center", va="center",
                color=WHITE, fontsize=7, fontweight="bold", zorder=5)
        if i < len(steps) - 1:
            arrow(ax, (x + w + 0.02, y + h / 2), (x + w + gap - 0.02, y + h / 2), color=TEAL)

    ax.text(
        5.75, 0.45,
        "Principe RAG : la réponse est générée uniquement à partir des ressources indexées de Nouvelair.",
        ha="center", fontsize=8.5, color="#555555", style="italic",
    )
    save(fig, "figure_2_2_pipeline_assistant.png")


# ─────────────────────────────────────────────────────────────
# Figure 2.3 — Indexation
# ─────────────────────────────────────────────────────────────
def fig_indexation():
    fig, ax = plt.subplots(figsize=(11.5, 3.8))
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 3.8)
    ax.axis("off")
    ax.set_title(
        "Processus d'indexation des ressources de connaissance",
        fontsize=13, fontweight="bold", color=NAVY, pad=10,
    )

    steps = [
        ("1", "Ajout d'une\nressource", "Manager / Admin"),
        ("2", "Enregistrement\nmétadonnées", "MySQL"),
        ("3", "Stockage\ndu fichier", "disque / storage"),
        ("4", "Extraction\ndu texte", "PDF, DOCX…"),
        ("5", "Découpage\nen fragments", "chunking"),
        ("6", "Embeddings", "vecteurs"),
        ("7", "Stockage\nvectoriel", "ChromaDB"),
    ]
    w, h = 1.25, 1.55
    y = 1.15
    gap = 0.28
    x0 = 0.35

    for i, (num, title, sub) in enumerate(steps):
        x = x0 + i * (w + gap)
        if i <= 2:
            fc, ec, badge = LAYER_C, ACCENT, ACCENT
        elif i >= 5:
            fc, ec, badge = LAYER_D, PURPLE, PURPLE
        else:
            fc, ec, badge = LAYER_B, TEAL, TEAL
        rounded_box(ax, (x, y), w, h, title, fc=fc, ec=ec, fontsize=8.5, bold=True, sub=sub)
        circ = plt.Circle((x + 0.18, y + h - 0.18), 0.14, fc=badge, ec="none", zorder=4)
        ax.add_patch(circ)
        ax.text(x + 0.18, y + h - 0.18, num, ha="center", va="center",
                color=WHITE, fontsize=7, fontweight="bold", zorder=5)
        if i < len(steps) - 1:
            arrow(ax, (x + w + 0.02, y + h / 2), (x + w + gap - 0.02, y + h / 2), color=BORDER)

    ax.text(
        5.75, 0.45,
        "À la suppression d'une ressource, les fragments associés sont retirés de ChromaDB.",
        ha="center", fontsize=8.5, color="#555555", style="italic",
    )
    save(fig, "figure_2_3_indexation.png")


# ─────────────────────────────────────────────────────────────
# Figure 2.5 — Diagramme de classes (corrigé)
# ─────────────────────────────────────────────────────────────
def class_box(ax, x, y, w, name, attrs, methods=None, header_fc=NAVY):
    """Draw a UML class box. (x, y) = bottom-left. Returns (x, y, w, h)."""
    methods = methods or []
    row_h = 0.26
    header_h = 0.36
    attr_h = max(len(attrs), 1) * row_h + 0.10
    meth_h = (len(methods) * row_h + 0.10) if methods else 0
    total_h = header_h + attr_h + meth_h

    # outer border
    ax.add_patch(Rectangle((x, y), w, total_h,
                            facecolor=WHITE, edgecolor=NAVY, lw=1.3, zorder=2))
    # header
    ax.add_patch(Rectangle((x, y + attr_h + meth_h), w, header_h,
                            facecolor=header_fc, edgecolor=NAVY, lw=1.3, zorder=3))
    ax.text(x + w / 2, y + attr_h + meth_h + header_h / 2, name,
            ha="center", va="center", color=WHITE, fontsize=8.5, fontweight="bold", zorder=4)

    # attributes compartment separator already via fill
    for i, a in enumerate(attrs):
        ax.text(x + 0.10, y + meth_h + attr_h - 0.10 - i * row_h, a,
                ha="left", va="top", fontsize=6.8, color=SLATE, family="monospace", zorder=4)

    if methods:
        # separator line between attrs and methods
        sep_y = y + meth_h
        ax.plot([x, x + w], [sep_y, sep_y], color=NAVY, lw=1.0, zorder=3)
        for i, m in enumerate(methods):
            ax.text(x + 0.10, y + meth_h - 0.10 - i * row_h, m,
                    ha="left", va="top", fontsize=6.8, color=TEAL, family="monospace", zorder=4)
        # separator between header and attrs
    ax.plot([x, x + w], [y + meth_h + attr_h, y + meth_h + attr_h],
            color=NAVY, lw=1.0, zorder=3)

    return (x, y, w, total_h)


def _mid(box, side):
    x, y, w, h = box
    if side == "top":
        return (x + w / 2, y + h)
    if side == "bottom":
        return (x + w / 2, y)
    if side == "left":
        return (x, y + h / 2)
    if side == "right":
        return (x + w, y + h / 2)
    if side == "bottom-left":
        return (x + w * 0.25, y)
    if side == "bottom-right":
        return (x + w * 0.75, y)
    if side == "top-left":
        return (x + w * 0.25, y + h)
    if side == "top-right":
        return (x + w * 0.75, y + h)
    return (x + w / 2, y + h / 2)


def assoc(ax, p1, p2, m1="", m2="", label="", label_offset=(0, 0.18),
          m1_off=(0, 0.14), m2_off=(0, 0.14), route=None):
    """Optional route='vh' (vertical then horizontal) or 'hv'."""
    if route == "vh":
        xs, ys = [p1[0], p1[0], p2[0]], [p1[1], p2[1], p2[1]]
    elif route == "hv":
        xs, ys = [p1[0], p2[0], p2[0]], [p1[1], p1[1], p2[1]]
    else:
        xs, ys = [p1[0], p2[0]], [p1[1], p2[1]]
    ax.plot(xs, ys, color=SLATE, lw=1.15, zorder=1)

    def _lbl(pt, text, off):
        ax.text(pt[0] + off[0], pt[1] + off[1], text,
                fontsize=6.5, color=SLATE, fontweight="bold", zorder=5, ha="center",
                bbox=dict(boxstyle="round,pad=0.12", fc=WHITE, ec="none", alpha=0.95))

    if m1:
        _lbl(p1, m1, m1_off)
    if m2:
        _lbl(p2, m2, m2_off)
    if label:
        if len(xs) == 2:
            mx = (xs[0] + xs[1]) / 2 + label_offset[0]
            my = (ys[0] + ys[1]) / 2 + label_offset[1]
        else:
            mx = (xs[0] + xs[1]) / 2 + label_offset[0]
            my = (ys[0] + ys[1]) / 2 + label_offset[1]
        ax.text(mx, my, label, fontsize=6.5, color=TEAL, style="italic", ha="center",
                zorder=5, bbox=dict(boxstyle="round,pad=0.12", fc=WHITE, ec="none", alpha=0.95))


def fig_classes():
    fig, ax = plt.subplots(figsize=(14.0, 11.5))
    ax.set_xlim(0, 14.0)
    ax.set_ylim(0, 11.5)
    ax.axis("off")
    ax.set_title(
        "Diagramme de classes — modèle métier de la plateforme",
        fontsize=13, fontweight="bold", color=NAVY, pad=10,
    )

    role = class_box(ax, 0.5, 8.55, 2.7, "Rôle",
                     ["- id : int", "- nom : string"],
                     header_fc=NAVY)
    user = class_box(ax, 5.2, 7.9, 3.5, "Utilisateur",
                     ["- id : int", "- nom : string", "- prenom : string",
                      "- email : string", "- motDePasse : string",
                      "- dateCreation : datetime"],
                     ["+ sAuthentifier()"],
                     header_fc=NAVY)
    cat = class_box(ax, 10.6, 8.4, 2.9, "Catégorie",
                    ["- id : int", "- nom : string", "- description : string"],
                    header_fc=TEAL)

    res = class_box(ax, 4.8, 3.85, 4.3, "RessourceDeConnaissance",
                    ["- id : int", "- titre : string", "- type : enum",
                     "- typeFichier : string", "- cheminFichier : string",
                     "- dateAjout : datetime", "- estIndexe : boolean"],
                    ["+ ajouter()", "+ modifier()",
                     "+ supprimer()", "+ telecharger()"],
                    header_fc=ACCENT)

    sess = class_box(ax, 0.4, 1.2, 3.3, "SessionAssistant",
                     ["- id : int", "- dateDebut : datetime",
                      "- dateDerniereActivite : datetime"],
                     header_fc=PURPLE)
    msg = class_box(ax, 5.15, 1.05, 3.5, "MessageAssistant",
                    ["- id : int", "- texte : text",
                     "- role : enum {user, assistant}",
                     "- dateEnvoi : datetime"],
                    header_fc=PURPLE)
    cit = class_box(ax, 10.1, 1.2, 3.3, "Citation",
                    ["- id : int", "- extrait : text",
                     "- scorePertinence : float"],
                    header_fc=PURPLE)

    assoc(ax, _mid(role, "right"), _mid(user, "left"),
          "1", "0..*", "attribue",
          m1_off=(0.18, 0.16), m2_off=(-0.22, 0.16), label_offset=(0, 0.28))
    assoc(ax, _mid(user, "bottom"), _mid(res, "top"),
          "1", "0..*", "publie",
          m1_off=(0.30, -0.18), m2_off=(0.30, 0.18), label_offset=(0.55, 0))
    assoc(ax, _mid(cat, "bottom"), _mid(res, "right"),
          "1", "0..*", "classe",
          m1_off=(0.25, -0.18), m2_off=(0.30, 0.12),
          label_offset=(0.40, 0.35), route="vh")
    assoc(ax, _mid(user, "left"), _mid(sess, "top"),
          "1", "0..*", "ouvre",
          m1_off=(-0.28, 0.14), m2_off=(0.25, 0.18),
          label_offset=(-0.55, 0.20), route="hv")
    assoc(ax, _mid(sess, "right"), _mid(msg, "left"),
          "1", "1..*",
          m1_off=(0.20, 0.16), m2_off=(-0.25, 0.16), label_offset=(0, 0.28))
    assoc(ax, _mid(msg, "right"), _mid(cit, "left"),
          "0..*", "0..*",
          m1_off=(0.25, 0.16), m2_off=(-0.28, 0.16), label_offset=(0, 0.28))
    assoc(ax, _mid(cit, "top"), _mid(res, "bottom-right"),
          "0..*", "1", "provient de",
          m1_off=(0.30, 0.18), m2_off=(0.35, -0.18), label_offset=(0.55, 0))

    ax.add_patch(FancyBboxPatch(
        (0.35, 0.12), 13.3, 0.72,
        boxstyle="round,pad=0.02,rounding_size=0.05",
        fc=LAYER_A, ec=BORDER, lw=1, zorder=0,
    ))
    ax.text(
        0.55, 0.60,
        "SessionAssistant / MessageAssistant = historique du chat IA (RAG), pas un forum. "
        "Une publication interne = type de RessourceDeConnaissance (pas Post / Commentaire).",
        fontsize=7.2, color=SLATE, va="center",
    )
    ax.text(
        0.55, 0.30,
        "Citation remplace « Source IA » : extrait d'une ressource justifiant une réponse de l'assistant.",
        fontsize=7.2, color=SLATE, va="center",
    )

    save(fig, "figure_2_5_diagramme_classes.png")


# ─────────────────────────────────────────────────────────────
# Diagrammes de séquence
# ─────────────────────────────────────────────────────────────
def sequence_diagram(title, actors, messages, filename, lifeline_notes=None):
    """
    actors: list of names
    messages: list of (from_idx, to_idx, text, kind)
      kind: 'call' | 'return' | 'self' | 'note'
    """
    n = len(actors)
    fig_w = max(11, 1.8 * n + 2)
    # estimate height from messages
    fig_h = 1.6 + 0.42 * len(messages) + 0.8
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold", color=NAVY, pad=8)

    xs = [1.2 + i * ((fig_w - 1.5) / max(n - 1, 1)) for i in range(n)]
    header_y = fig_h - 0.7
    bottom_y = 0.45

    # headers + lifelines
    actor_colors = [LAYER_A, LAYER_B, LAYER_B, LAYER_D, LAYER_D, LAYER_C, LAYER_C]
    actor_edges = [NAVY, TEAL, TEAL, PURPLE, PURPLE, ACCENT, ACCENT]
    for i, name in enumerate(actors):
        w = 1.55
        fc = actor_colors[i % len(actor_colors)]
        ec = actor_edges[i % len(actor_edges)]
        rounded_box(ax, (xs[i] - w / 2, header_y - 0.15), w, 0.55,
                    name, fc=fc, ec=ec, fontsize=7.5, bold=True)
        ax.plot([xs[i], xs[i]], [header_y - 0.15, bottom_y],
                color=BORDER, lw=1, ls="--", zorder=0)

    y = header_y - 0.55
    for item in messages:
        kind = item[3] if len(item) > 3 else "call"
        if kind == "note":
            ax.add_patch(FancyBboxPatch(
                (0.4, y - 0.28), fig_w - 0.8, 0.35,
                boxstyle="round,pad=0.01,rounding_size=0.04",
                fc=LAYER_C, ec=ACCENT, lw=0.9, zorder=2))
            ax.text(fig_w / 2, y - 0.1, item[2], ha="center", va="center",
                    fontsize=7, color=SLATE, zorder=3)
            y -= 0.48
            continue

        a, b, text = item[0], item[1], item[2]
        y -= 0.12
        x1, x2 = xs[a], xs[b]
        if kind == "return":
            ax.annotate("", xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="-|>", color=BORDER,
                                        lw=1.1, linestyle="--"))
            ax.text((x1 + x2) / 2, y + 0.06, text, ha="center", fontsize=7,
                    color=BORDER, style="italic")
        elif kind == "self":
            ax.annotate("", xy=(x1 + 0.55, y - 0.18), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="-|>", color=PURPLE, lw=1.2,
                                        connectionstyle="arc3,rad=-0.4"))
            ax.text(x1 + 0.65, y - 0.05, text, ha="left", fontsize=7, color=SLATE)
            y -= 0.15
        else:
            ax.annotate("", xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.3))
            ax.text((x1 + x2) / 2, y + 0.06, text, ha="center", fontsize=7.2,
                    color=SLATE, fontweight="medium")
        y -= 0.38

    save(fig, filename)


def fig_seq_question():
    actors = ["Employé", "Angular", "FastAPI", "ChromaDB", "LangChain/LLM", "MySQL"]
    messages = [
        (0, 1, "1. Saisir une question", "call"),
        (1, 2, "2. POST /api/assistant/question", "call"),
        (2, 5, "3. Charger / créer SessionAssistant", "call"),
        (5, 2, "sessionId", "return"),
        (2, 3, "4. Recherche vectorielle (embedding question)", "call"),
        (3, 2, "fragments + métadonnées ressources", "return"),
        (2, 4, "5. Construire prompt + contexte (RAG)", "call"),
        (4, 2, "réponse générée", "return"),
        (2, 5, "6. Persister MessageAssistant + Citations", "call"),
        (5, 2, "OK", "return"),
        (2, 1, "7. Réponse + citations (titre, extrait)", "return"),
        (1, 0, "8. Afficher réponse et sources", "return"),
        (None, None, "Post-condition : l'échange est disponible dans l'historique de session.", "note"),
    ]
    sequence_diagram(
        "Diagramme de séquence — Poser une question à l'assistant intelligent",
        actors, messages, "figure_2_6_sequence_question.png",
    )


def fig_seq_ajout():
    actors = ["Manager", "Angular", "FastAPI", "MySQL", "Stockage", "Indexeur", "ChromaDB"]
    messages = [
        (0, 1, "1. Formulaire : titre, catégorie, fichier", "call"),
        (1, 2, "2. POST /api/ressources", "call"),
        (2, 3, "3. INSERT RessourceDeConnaissance", "call"),
        (3, 2, "ressourceId", "return"),
        (2, 4, "4. Stocker le fichier", "call"),
        (4, 2, "cheminFichier", "return"),
        (2, 5, "5. Déclencher tâche d'indexation", "call"),
        (5, 5, "6. Extraire texte → chunks → embeddings", "self"),
        (5, 6, "7. Upsert vecteurs + lien ressourceId", "call"),
        (6, 5, "OK", "return"),
        (5, 3, "8. UPDATE estIndexe = true", "call"),
        (5, 2, "indexation terminée", "return"),
        (2, 1, "9. Ressource créée et indexée", "return"),
        (1, 0, "10. Confirmation", "return"),
        (None, None, "Scénario alternatif : fichier invalide → erreur, aucune persistance ni indexation.", "note"),
    ]
    sequence_diagram(
        "Diagramme de séquence — Ajouter une ressource de connaissance",
        actors, messages, "figure_2_7_sequence_ajout_ressource.png",
    )


if __name__ == "__main__":
    fig_architecture()
    fig_connecteurs()
    fig_pipeline()
    fig_indexation()
    fig_classes()
    fig_seq_question()
    fig_seq_ajout()
    print("\nToutes les figures ont été générées.")
