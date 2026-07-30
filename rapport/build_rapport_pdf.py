"""
Génère le rapport PDF complet (preview 6) avec figures professionnelles
et sections corrigées (métier + classes + diagrammes de séquence).
"""
from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    KeepTogether,
    ListFlowable,
    ListItem,
)

ROOT = Path(__file__).parent
DIAG = ROOT / "diagrammes"
OUT = ROOT.parent / "jawher_bziouech_rapport_preview_6.pdf"

pdfmetrics.registerFont(TTFont("Times", r"C:\Windows\Fonts\times.ttf"))
pdfmetrics.registerFont(TTFont("Times-Bold", r"C:\Windows\Fonts\timesbd.ttf"))
pdfmetrics.registerFont(TTFont("Times-Italic", r"C:\Windows\Fonts\timesi.ttf"))
pdfmetrics.registerFont(TTFont("Times-BoldItalic", r"C:\Windows\Fonts\timesbi.ttf"))

# Thème académique classique (rapport original : noir / blanc)
BLACK = colors.black
GRAY = colors.HexColor("#333333")
LIGHT = colors.HexColor("#F3F3F3")
LINE = colors.HexColor("#999999")


def styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle(
        name="CoverTitle", fontName="Times-Bold", fontSize=20, leading=26,
        alignment=TA_CENTER, textColor=BLACK, spaceAfter=14,
    ))
    s.add(ParagraphStyle(
        name="CoverSub", fontName="Times", fontSize=13, leading=17,
        alignment=TA_CENTER, textColor=BLACK, spaceAfter=8,
    ))
    s.add(ParagraphStyle(
        name="CoverMeta", fontName="Times", fontSize=12, leading=16,
        alignment=TA_CENTER, textColor=BLACK, spaceBefore=6,
    ))
    s.add(ParagraphStyle(
        name="HChapter", fontName="Times-Bold", fontSize=16, leading=20,
        textColor=BLACK, spaceBefore=6, spaceAfter=14,
    ))
    s.add(ParagraphStyle(
        name="HSection", fontName="Times-Bold", fontSize=12, leading=16,
        textColor=BLACK, spaceBefore=14, spaceAfter=8,
    ))
    s.add(ParagraphStyle(
        name="HSub", fontName="Times-Bold", fontSize=11, leading=14,
        textColor=BLACK, spaceBefore=10, spaceAfter=6,
    ))
    s.add(ParagraphStyle(
        name="Body", fontName="Times", fontSize=11, leading=15,
        alignment=TA_JUSTIFY, textColor=BLACK, spaceAfter=7,
    ))
    s.add(ParagraphStyle(
        name="BulletBody", fontName="Times", fontSize=11, leading=14,
        textColor=BLACK, leftIndent=14, spaceAfter=2,
    ))
    s.add(ParagraphStyle(
        name="Caption", fontName="Times-Italic", fontSize=10, leading=13,
        alignment=TA_CENTER, textColor=BLACK, spaceBefore=4, spaceAfter=12,
    ))
    s.add(ParagraphStyle(
        name="TOCEntry", fontName="Times", fontSize=11, leading=15,
        textColor=BLACK, spaceAfter=2,
    ))
    s.add(ParagraphStyle(
        name="Quote", fontName="Times-Italic", fontSize=11, leading=15,
        alignment=TA_CENTER, textColor=BLACK, spaceBefore=8, spaceAfter=8,
        leftIndent=20, rightIndent=20,
    ))
    s.add(ParagraphStyle(
        name="TableCell", fontName="Times", fontSize=9, leading=12,
        textColor=BLACK,
    ))
    s.add(ParagraphStyle(
        name="TableHead", fontName="Times-Bold", fontSize=9, leading=12,
        textColor=BLACK,
    ))
    s.add(ParagraphStyle(
        name="Footer", fontName="Times", fontSize=9, textColor=GRAY,
        alignment=TA_CENTER,
    ))
    return s


S = styles()


def P(text: str, style="Body"):
    return Paragraph(text.replace("\n", "<br/>"), S[style])


def bullets(items):
    flow = []
    for it in items:
        flow.append(Paragraph(f"• {it}", S["BulletBody"]))
    flow.append(Spacer(1, 4))
    return flow


def numbered(items):
    flow = []
    for i, it in enumerate(items, 1):
        flow.append(Paragraph(f"{i}. {it}", S["BulletBody"]))
    flow.append(Spacer(1, 4))
    return flow


def fig(path: Path, caption: str, width=16 * cm, max_h=12 * cm):
    if not path.exists():
        return [P(f"[Figure manquante : {path.name}]", "Caption")]
    # preserve aspect ratio; allow taller diagrams (e.g. class diagram)
    from PIL import Image as PILImage
    with PILImage.open(path) as im:
        w, h = im.size
    aspect = h / float(w)
    disp_w = width
    disp_h = disp_w * aspect
    if disp_h > max_h:
        disp_h = max_h
        disp_w = disp_h / aspect
    img = Image(str(path), width=disp_w, height=disp_h)
    return KeepTogether([Spacer(1, 8), img, P(caption, "Caption")])


def make_table(headers, rows, col_widths=None):
    head = [Paragraph(h, S["TableHead"]) for h in headers]
    data = [head]
    for row in rows:
        data.append([Paragraph(str(c), S["TableCell"]) for c in row])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
        ("TEXTCOLOR", (0, 0), (-1, 0), BLACK),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("BOX", (0, 0), (-1, -1), 0.8, BLACK),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, BLACK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


class Doc(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="normal")
        self.addPageTemplates([PageTemplate(id="main", frames=frame, onPage=self._footer)])

    def _footer(self, canvas, doc):
        canvas.saveState()
        page = canvas.getPageNumber()
        if page > 1:
            canvas.setStrokeColor(LINE)
            canvas.setLineWidth(0.5)
            y = 1.4 * cm
            canvas.line(2 * cm, y + 8, A4[0] - 2 * cm, y + 8)
            canvas.setFont("Times", 9)
            canvas.setFillColor(GRAY)
            canvas.drawCentredString(A4[0] / 2, y, f"{page}")
        canvas.restoreState()


def build():
    story = []

    # ── COVER ──
    story.append(Spacer(1, 4 * cm))
    story.append(P("Rapport d'analyse et de conception", "CoverTitle"))
    story.append(Spacer(1, 0.6 * cm))
    story.append(P(
        "Conception et développement d'une plateforme de gestion des "
        "connaissances assistée par intelligence artificielle",
        "CoverSub",
    ))
    story.append(Spacer(1, 2.5 * cm))
    story.append(P("<b>Jawher Bziouech</b>", "CoverMeta"))
    story.append(P("Stage — Nouvelair", "CoverMeta"))
    story.append(P("Juillet – Août 2026", "CoverMeta"))
    story.append(P("Version preview 6 — figures et modèle métier corrigés", "CoverMeta"))
    story.append(PageBreak())

    # ── TOC (simplified static) ──
    story.append(P("Table des matières", "HChapter"))
    toc = [
        "Introduction générale",
        "1. Étude préliminaire",
        "    1.1 – 1.15  Contexte, besoins, méthodologie, analyse métier, environnement",
        "2. Analyse et conception de la solution",
        "    2.1 Introduction",
        "    2.2 Vision du produit",
        "    2.3 User Stories",
        "    2.4 Product Backlog",
        "    2.5 Architecture générale de la solution",
        "    2.6 Architecture métier",
        "    2.7 Architecture du module d'intelligence artificielle",
        "    2.8 Indexation des ressources de connaissance",
        "    2.9 Diagramme de cas d'utilisation",
        "    2.10 Description textuelle des cas d'utilisation principaux",
        "    2.11 Diagramme de classes",
        "    2.12 Diagramme de séquence — Poser une question",
        "    2.13 Diagramme de séquence — Ajouter une ressource",
    ]
    for e in toc:
        story.append(P(e, "TOCEntry"))
    story.append(PageBreak())

    # ── INTRO ──
    story.append(P("Introduction générale", "HChapter"))
    story.append(P(
        "La transformation numérique joue aujourd'hui un rôle essentiel dans l'amélioration des "
        "processus et de la circulation de l'information au sein des entreprises."
    ))
    story.append(P(
        "Dans ce contexte, la gestion des connaissances constitue un enjeu majeur, notamment "
        "lorsque les documents, procédures et informations internes sont dispersés sur différents "
        "supports. Cette situation peut rendre l'accès à l'information plus difficile et ralentir les "
        "activités des collaborateurs."
    ))
    story.append(P(
        "C'est dans cette optique que s'inscrit ce projet de stage réalisé au sein de Nouvelair. "
        "Il a pour objectif de concevoir et développer une plateforme web intelligente permettant "
        "de centraliser les ressources de connaissance de l'entreprise et de faciliter leur exploitation "
        "grâce à un assistant conversationnel basé sur l'intelligence artificielle."
    ))
    story.append(P(
        "Ce rapport présente les différentes étapes du projet, depuis l'étude des besoins jusqu'à "
        "la conception et la réalisation de la solution proposée."
    ))
    story.append(PageBreak())

    # ── CHAPTER 1 ──
    story.append(P("Chapitre 1 — Étude préliminaire", "HChapter"))

    story.append(P("1.1 Introduction", "HSection"))
    story.append(P(
        "Ce chapitre présente le cadre général du projet : l'entreprise d'accueil, la problématique, "
        "les objectifs, l'étude de l'existant, la solution proposée, les acteurs, les besoins ainsi que "
        "la méthodologie retenue."
    ))
    story.append(P(
        "L'objectif de cette première partie est de définir clairement le périmètre du projet "
        "avant de passer aux phases d'analyse, de conception et de développement."
    ))

    story.append(P("1.2 Présentation de l'entreprise", "HSection"))
    story.append(P(
        "Nouvelair est la première compagnie aérienne privée tunisienne. Fondée en 1989, elle "
        "appartient au groupe Tunisian Travel Service, également connu sous le nom de TTS. La "
        "compagnie a commencé son activité principalement dans le domaine des vols charters avant "
        "de développer progressivement des vols réguliers vers plusieurs destinations internationales."
    ))
    story.append(P(
        "Nouvelair assure aujourd'hui des liaisons aériennes entre la Tunisie et plusieurs pays, "
        "notamment en Europe, au Moyen-Orient et en Afrique du Nord. Elle opère à partir de "
        "plusieurs aéroports tunisiens, dont Monastir, Tunis-Carthage, Djerba-Zarzis et Enfidha-Hammamet."
    ))
    story.append(P(
        "Dans le cadre de sa modernisation, Nouvelair accorde une importance particulière à la "
        "digitalisation de ses processus internes. Cette orientation vise à améliorer la circulation "
        "de l'information, renforcer l'efficacité des collaborateurs et faciliter l'accès aux ressources "
        "nécessaires au bon déroulement des activités de l'entreprise."
    ))

    story.append(P("1.3 Contexte du projet", "HSection"))
    story.append(P(
        "Au sein d'une compagnie aérienne, les collaborateurs consultent régulièrement des procédures, "
        "documents administratifs, notes de service et autres ressources nécessaires à leurs activités. "
        "L'accès rapide à ces informations est essentiel pour l'efficacité des opérations et la "
        "coordination entre services."
    ))
    story.append(P(
        "Or, lorsque les ressources sont dispersées ou difficiles à retrouver, la recherche "
        "d'information devient plus longue et moins efficace. Nouvelair souhaite donc mettre en place "
        "une plateforme web de gestion des connaissances, détaillée à la section 1.9, permettant de "
        "centraliser ses ressources et d'en faciliter la consultation."
    ))

    story.append(P("1.4 Problématique", "HSection"))
    story.append(P(
        "La gestion des connaissances représente un enjeu important pour les entreprises disposant "
        "d'un volume conséquent de documents et d'informations internes. Bien que ces ressources "
        "soient disponibles, leur exploitation peut être limitée lorsqu'elles sont dispersées ou "
        "difficiles à retrouver."
    ))
    story.append(P(
        "Par ailleurs, les moteurs de recherche classiques reposent principalement sur des mots-clés "
        "et ne permettent pas toujours de répondre efficacement à des questions formulées en "
        "langage naturel."
    ))
    story.append(P("Cette situation peut entraîner plusieurs difficultés :"))
    story.extend(bullets([
        "perte de temps dans la recherche d'informations ;",
        "sollicitation fréquente des responsables ;",
        "sous-exploitation des ressources disponibles ;",
        "risque d'utilisation d'informations obsolètes ;",
        "difficulté à capitaliser les connaissances de l'entreprise.",
    ]))
    story.append(P("La problématique du projet peut ainsi être formulée comme suit :"))
    story.append(P(
        "« Comment concevoir une plateforme intelligente permettant de centraliser "
        "les ressources de connaissance de Nouvelair et d'en faciliter l'accès "
        "grâce à un assistant conversationnel capable de fournir des réponses "
        "fiables et fondées sur les contenus validés par l'entreprise ? »",
        "Quote",
    ))

    story.append(P("1.5 Objectifs du projet", "HSection"))
    story.append(P(
        "L'objectif principal de ce projet est de concevoir et développer une plateforme web "
        "intelligente de gestion des connaissances destinée aux collaborateurs de Nouvelair."
    ))
    story.append(P("Les objectifs spécifiques sont les suivants :"))
    story.extend(bullets([
        "centraliser les ressources de connaissance de l'entreprise au sein d'une plateforme unique ;",
        "permettre aux administrateurs et aux managers de publier, modifier et supprimer les ressources dont ils sont responsables ;",
        "offrir aux collaborateurs un accès simple et sécurisé aux ressources disponibles ;",
        "permettre la consultation et le téléchargement des documents autorisés ;",
        "intégrer un assistant conversationnel capable de répondre aux questions des utilisateurs ;",
        "garantir que les réponses de l'assistant soient fondées uniquement sur les ressources disponibles dans la plateforme ;",
        "afficher les sources utilisées par l'assistant afin d'assurer la traçabilité des réponses ;",
        "maintenir automatiquement la base de connaissances à jour lors de l'ajout, la modification ou la suppression d'une ressource ;",
        "assurer une gestion des accès basée sur les rôles ;",
        "concevoir une architecture évolutive permettant d'ajouter de nouvelles fonctionnalités à l'avenir.",
    ]))

    story.append(P("1.6 Étude de l'existant", "HSection"))
    story.append(P(
        "Actuellement, Nouvelair dispose de plusieurs ressources — documents internes, procédures, "
        "publications — permettant aux collaborateurs d'accéder aux informations nécessaires à "
        "leurs activités."
    ))
    story.append(P(
        "Ces ressources sont consultées manuellement selon les besoins de chaque service : la "
        "recherche d'une information spécifique nécessite souvent de parcourir plusieurs documents "
        "ou de solliciter un responsable. Aucun système intelligent n'est aujourd'hui disponible "
        "pour exploiter automatiquement ces connaissances."
    ))

    story.append(P("1.7 Critique de l'existant", "HSection"))
    story.append(P(
        "Cette étude met en évidence plusieurs limites. La navigation manuelle, peu adaptée à un "
        "volume important de ressources, allonge le temps nécessaire pour retrouver un document "
        "ou une procédure."
    ))
    story.append(P(
        "Les collaborateurs doivent aussi solliciter directement un responsable pour obtenir "
        "une réponse, ce qui ralentit l'accès à l'information et limite le partage des connaissances. "
        "Enfin, l'absence d'un assistant intelligent empêche de fournir des réponses rapides et "
        "contextualisées à partir des documents disponibles."
    ))

    story.append(P("1.8 Comparaison entre l'existant et la solution proposée", "HSection"))
    story.append(P(
        "Afin de mieux mettre en évidence les améliorations apportées par la solution développée, "
        "le tableau 1.1 présente une comparaison entre le fonctionnement actuel et le système proposé."
    ))
    story.append(Spacer(1, 6))
    story.append(make_table(
        ["Existant", "Solution proposée"],
        [
            ["Informations réparties sur plusieurs supports",
             "Plateforme centralisée de gestion des connaissances."],
            ["Recherche principalement basée sur des mots-clés",
             "Recherche intelligente assistée par intelligence artificielle."],
            ["Consultation manuelle des documents",
             "Réponses en langage naturel fournies par un assistant conversationnel."],
            ["Absence de centralisation des publications et documents",
             "Gestion unifiée des ressources de connaissance."],
            ["Recherche parfois longue et peu intuitive",
             "Accès rapide aux informations avec affichage des sources."],
        ],
        col_widths=[8 * cm, 8 * cm],
    ))
    story.append(P("Table 1.1 — Comparaison entre l'existant et la solution proposée", "Caption"))

    story.append(P("1.9 Solution proposée", "HSection"))
    story.append(P(
        "Afin de répondre aux limites identifiées, il est proposé de développer une plateforme web "
        "intelligente dédiée à la gestion et au partage des connaissances de Nouvelair."
    ))
    story.append(P(
        "La solution centralise les documents et publications internes au sein d'un espace "
        "unique, accessible selon les droits de chaque rôle : les managers et administrateurs publient "
        "et gèrent les ressources, les employés les consultent."
    ))
    story.append(P(
        "Un assistant conversationnel, détaillé à la section 2.7, complète la plateforme en "
        "répondant aux questions des utilisateurs à partir des contenus validés. Cette approche "
        "vise à améliorer l'accès à l'information et à réduire le temps consacré à la recherche "
        "documentaire."
    ))

    story.append(P("1.10 Identification des acteurs", "HSection"))
    story.append(P(
        "L'application est destinée à être utilisée par l'ensemble des collaborateurs de Nouvelair. "
        "Toutefois, les fonctionnalités accessibles varient selon le rôle attribué à chaque utilisateur. "
        "Trois catégories d'acteurs ont été identifiées."
    ))
    story.append(P("1.10.1 Administrateur", "HSub"))
    story.append(P(
        "L'administrateur est responsable de la gestion globale de la plateforme. Il dispose de "
        "l'ensemble des privilèges nécessaires pour administrer le système."
    ))
    story.append(P("Ses principales responsabilités sont les suivantes :"))
    story.extend(bullets([
        "gérer les utilisateurs ;",
        "gérer les rôles ;",
        "consulter l'ensemble des ressources de connaissance ;",
        "créer, modifier et supprimer les ressources ;",
        "administrer les publications ;",
        "superviser le fonctionnement général de la plateforme.",
    ]))
    story.append(P("1.10.2 Manager", "HSub"))
    story.append(P("Le manager est responsable des ressources de connaissance qu'il publie. Il peut :"))
    story.extend(bullets([
        "ajouter une nouvelle ressource ;",
        "modifier ses propres ressources ;",
        "supprimer ses propres ressources ;",
        "publier des annonces internes ;",
        "consulter les ressources disponibles.",
    ]))
    story.append(P("Le manager ne peut pas modifier les ressources publiées par un autre manager."))
    story.append(P("1.10.3 Employé", "HSub"))
    story.append(P("L'employé représente l'utilisateur principal de la plateforme. Il peut :"))
    story.extend(bullets([
        "consulter les ressources de connaissance ;",
        "télécharger les documents autorisés ;",
        "consulter les publications internes ;",
        "interagir avec l'assistant conversationnel ;",
        "effectuer des recherches dans la base de connaissances.",
    ]))

    story.append(P("1.11 Analyse des besoins", "HSection"))
    story.append(P(
        "L'analyse des besoins consiste à identifier l'ensemble des fonctionnalités attendues par les "
        "futurs utilisateurs de la plateforme ainsi que les contraintes auxquelles le système devra répondre."
    ))
    story.append(P("1.11.1 Besoins fonctionnels", "HSub"))
    story.extend(numbered([
        "Authentification des utilisateurs.",
        "Gestion des utilisateurs.",
        "Gestion des rôles.",
        "Gestion des ressources de connaissance.",
        "Consultation des ressources.",
        "Téléchargement des documents.",
        "Publication des annonces internes.",
        "Recherche des ressources.",
        "Assistant conversationnel basé sur l'intelligence artificielle.",
        "Consultation des sources utilisées par l'assistant.",
        "Mise à jour automatique de la base de connaissances après chaque ajout, modification ou suppression d'une ressource.",
    ]))
    story.append(P("1.11.2 Besoins non fonctionnels", "HSub"))
    story.extend(bullets([
        "La plateforme doit être disponible à tout moment pour les utilisateurs autorisés.",
        "L'authentification doit garantir un accès sécurisé aux ressources.",
        "Les performances doivent permettre d'obtenir des réponses rapides.",
        "L'interface utilisateur doit être intuitive.",
        "Les informations doivent rester confidentielles.",
        "Le système doit être facilement maintenable.",
        "L'architecture doit permettre l'ajout futur de nouvelles fonctionnalités.",
        "Les réponses de l'assistant doivent être traçables grâce à l'affichage des sources.",
    ]))
    story.append(P("1.11.3 Contraintes", "HSub"))
    story.extend(bullets([
        "durée du stage limitée à deux mois ;",
        "développement selon la méthodologie Agile Scrum ;",
        "accès sécurisé selon les rôles ;",
        "utilisation exclusive des ressources validées par l'entreprise pour alimenter l'assistant intelligent ;",
        "suppression automatique des ressources supprimées de la base de connaissances ;",
        "conservation de l'historique conversationnel durant les échanges avec l'assistant.",
    ]))

    story.append(P("1.12 Méthodologie de développement", "HSection"))
    story.append(P(
        "Afin d'assurer une organisation efficace du projet et de favoriser une évolution progressive "
        "de la solution, la méthodologie Agile Scrum a été retenue. Cette approche permet de développer "
        "l'application de manière incrémentale en découpant le projet en plusieurs sprints successifs."
    ))
    story.append(P(
        "À la fin de chaque sprint, une version fonctionnelle de l'application est produite, "
        "permettant de recueillir rapidement les retours de l'encadrant et d'intégrer les éventuelles "
        "améliorations avant le sprint suivant."
    ))
    story.append(P("1.12.1 Les rôles Scrum", "HSub"))
    story.append(make_table(
        ["Rôle", "Responsabilité"],
        [
            ["Product Owner", "Encadrant de stage représentant les besoins de Nouvelair."],
            ["Scrum Master", "Stagiaire chargé du respect de la méthodologie Scrum."],
            ["Équipe de développement", "Stagiaire responsable de la conception et du développement de la plateforme."],
        ],
        col_widths=[5 * cm, 11 * cm],
    ))
    story.append(P("Table 1.2 — Répartition des rôles Scrum", "Caption"))

    story.append(P("1.12.2 Planification des sprints", "HSub"))
    story.append(P(
        "Le projet est réparti sur une durée de deux mois. Le planning prévisionnel est composé "
        "de quatre sprints, chacun associé à un objectif précis, aux User Stories correspondantes "
        "(voir tableau 2.1) et à un livrable concret évalué en fin de sprint."
    ))
    story.append(make_table(
        ["Sprint", "Période", "Objectif", "User Stories", "Livrable"],
        [
            ["Sprint 1", "01/07 – 14/07", "Cadrer le projet et poser l'architecture", "—",
             "Spécifications, architecture et environnement de développement validés"],
            ["Sprint 2", "15/07 – 28/07", "Gérer les utilisateurs et les ressources",
             "US1, US2, US3, US4, US5, US8",
             "Authentification, gestion des rôles et CRUD des ressources/catégories"],
            ["Sprint 3", "29/07 – 11/08", "Intégrer l'assistant conversationnel", "US6, US7",
             "Assistant intelligent opérationnel (recherche vectorielle, réponses avec sources)"],
            ["Sprint 4", "12/08 – 31/08", "Finaliser et fiabiliser la plateforme", "US9",
             "Tableau de bord, tests, corrections et documentation finale"],
        ],
        col_widths=[2.2 * cm, 2.6 * cm, 3.4 * cm, 3.2 * cm, 4.6 * cm],
    ))
    story.append(P("Table 1.3 — Planification prévisionnelle des sprints", "Caption"))

    story.append(P("1.13 Conclusion", "HSection"))
    story.append(P(
        "Ce chapitre a présenté le contexte du projet et les besoins ayant conduit à la conception "
        "de la plateforme de gestion des connaissances de Nouvelair, ainsi que les limites de "
        "l'existant justifiant une solution centralisée intégrant un assistant intelligent. Les besoins "
        "fonctionnels et non fonctionnels ont ensuite été identifiés, avant de présenter la méthodologie "
        "Agile Scrum retenue pour conduire le développement du projet."
    ))
    story.append(P(
        "Le chapitre suivant est consacré à l'analyse et à la conception de la solution : diagrammes "
        "UML, architecture logicielle ainsi que conception de la base de données."
    ))

    story.append(P("1.14 Analyse métier", "HSection"))
    story.append(P(
        "Avant de procéder à la conception technique de la plateforme, il est nécessaire d'identifier "
        "les principaux concepts métier manipulés par le système. Cette étape permet de définir un "
        "vocabulaire commun qui servira de référence durant les phases de conception, de développement "
        "et de maintenance de l'application."
    ))
    story.append(P(
        "Contrairement à une plateforme documentaire classique, la solution proposée repose "
        "sur une approche orientée gestion des connaissances. Ainsi, l'ensemble des informations "
        "exploitées par la plateforme est représenté sous la forme de ressources de connaissance."
    ))
    story.append(P("1.14.1 Ressource de connaissance", "HSub"))
    story.append(P(
        "La ressource de connaissance constitue le concept central de la plateforme. Elle représente "
        "toute information officielle pouvant être consultée par les collaborateurs de Nouvelair."
    ))
    story.append(P("Une ressource de connaissance peut correspondre à :"))
    story.extend(bullets([
        "un document PDF ;",
        "un document Word ;",
        "une procédure interne ;",
        "une note de service ;",
        "une publication interne ;",
        "un guide technique ;",
        "toute autre information validée par l'entreprise.",
    ]))
    story.append(P("1.14.2 Utilisateur", "HSub"))
    story.append(P(
        "Un utilisateur représente une personne autorisée à accéder à la plateforme. Selon son rôle, "
        "il dispose de différents niveaux d'autorisation lui permettant de consulter, publier ou "
        "administrer les ressources de connaissance."
    ))
    story.append(P("1.14.3 Assistant intelligent", "HSub"))
    story.append(P(
        "L'assistant intelligent constitue le module chargé d'interpréter les questions formulées par "
        "les collaborateurs. Il exploite exclusivement les ressources de connaissance disponibles dans "
        "la plateforme afin de générer des réponses fiables et contextualisées. Chaque réponse est "
        "accompagnée des références des ressources utilisées afin d'assurer la traçabilité des "
        "informations fournies."
    ))
    story.append(P("1.14.4 Catégorie", "HSub"))
    story.append(P(
        "Les ressources de connaissance sont regroupées selon des catégories facilitant leur organisation "
        "et leur consultation. Cette classification permet également d'améliorer la recherche "
        "d'informations et l'administration de la plateforme."
    ))
    story.append(P("1.14.5 Session avec l'assistant", "HSub"))
    story.append(P(
        "Une session d'assistant représente l'ensemble des échanges entre un collaborateur et "
        "l'assistant intelligent (historique RAG). Chaque session est composée d'une succession de "
        "messages (questions utilisateur / réponses assistant). Il ne s'agit pas d'un forum : "
        "une publication interne est un type de ressource de connaissance, sans entités Post ou Commentaire."
    ))

    story.append(P("1.15 Environnement de travail", "HSection"))
    story.append(P(
        "La mise en place de l'environnement de développement constitue une étape du Sprint 1. "
        "Le tableau 1.4 présente les langages, frameworks et outils retenus pour la réalisation du projet."
    ))
    story.append(make_table(
        ["Catégorie", "Choix retenu"],
        [
            ["Langages", "Python (backend, IA), TypeScript (frontend)"],
            ["Frameworks", "Angular (interface web), FastAPI (API REST)"],
            ["Bases de données", "MySQL (données relationnelles), ChromaDB (base vectorielle)"],
            ["Bibliothèque IA", "LangChain (orchestration du pipeline RAG)"],
            ["Éditeur de code", "Visual Studio Code"],
            ["Gestion de versions", "Git / GitHub"],
            ["Test des API", "Postman"],
            ["Gestion de la base de données", "MySQL Workbench"],
        ],
        col_widths=[5 * cm, 11 * cm],
    ))
    story.append(P("Table 1.4 — Environnement de travail", "Caption"))
    story.append(PageBreak())

    # ── CHAPTER 2 ──
    story.append(P("Chapitre 2 — Analyse et conception de la solution", "HChapter"))

    story.append(P("2.1 Introduction", "HSection"))
    story.append(P(
        "Après avoir présenté le contexte du projet ainsi que les besoins exprimés par l'entreprise, "
        "ce chapitre est consacré à l'analyse fonctionnelle et à la conception de la solution proposée."
    ))
    story.append(P(
        "Dans un premier temps, les fonctionnalités du système sont identifiées sous forme de "
        "User Stories et organisées au sein d'un Product Backlog conformément à la méthodologie "
        "Agile Scrum. Par la suite, ces besoins sont traduits en modèles UML permettant de décrire "
        "la structure du système, les interactions entre les différents acteurs ainsi que son "
        "architecture logicielle."
    ))

    story.append(P("2.2 Vision du produit", "HSection"))
    story.append(P(
        "Au-delà de la gestion documentaire classique, la plateforme centralise les ressources de "
        "connaissance de Nouvelair et intègre un assistant conversationnel permettant de les exploiter "
        "de manière intuitive."
    ))
    story.append(P("Le système repose sur trois objectifs principaux :"))
    story.extend(bullets([
        "Centraliser les connaissances de l'entreprise.",
        "Faciliter la recherche d'informations.",
        "Améliorer le partage des connaissances grâce à l'intelligence artificielle.",
    ]))

    story.append(P("2.3 User Stories", "HSection"))
    story.append(P(
        "Les besoins fonctionnels précédemment identifiés sont exprimés sous forme de User Stories "
        "afin de faciliter leur planification dans les différents sprints."
    ))
    story.append(make_table(
        ["ID", "User Story"],
        [
            ["US1", "En tant qu'administrateur, je souhaite gérer les utilisateurs afin de contrôler l'accès à la plateforme."],
            ["US2", "En tant que manager, je souhaite publier une ressource de connaissance afin de partager une information avec les collaborateurs."],
            ["US3", "En tant que manager, je souhaite modifier uniquement mes propres ressources."],
            ["US4", "En tant qu'employé, je souhaite consulter les ressources de connaissance disponibles."],
            ["US5", "En tant qu'employé, je souhaite télécharger un document."],
            ["US6", "En tant qu'employé, je souhaite poser une question à l'assistant intelligent."],
            ["US7", "En tant qu'employé, je souhaite connaître les sources utilisées par l'assistant."],
            ["US8", "En tant qu'administrateur, je souhaite gérer les catégories."],
            ["US9", "En tant qu'administrateur, je souhaite consulter le tableau de bord."],
        ],
        col_widths=[1.8 * cm, 14.2 * cm],
    ))
    story.append(P("Table 2.1 — Principales User Stories", "Caption"))

    story.append(P("2.4 Product Backlog", "HSection"))
    story.append(P(
        "Le Product Backlog regroupe l'ensemble des fonctionnalités prévues pour la première "
        "version de la plateforme."
    ))
    story.append(make_table(
        ["Epic", "Fonctionnalités", "Priorité"],
        [
            ["Authentification", "Connexion, déconnexion, gestion des rôles.", "Haute"],
            ["Gestion des ressources", "Ajouter, modifier, supprimer et consulter les ressources de connaissance.", "Haute"],
            ["Gestion des catégories", "Organisation des ressources.", "Moyenne"],
            ["Assistant intelligent", "Question/Réponse, recherche intelligente, citations des sources.", "Très haute"],
            ["Administration", "Gestion des utilisateurs et tableau de bord.", "Haute"],
        ],
        col_widths=[4.2 * cm, 9 * cm, 2.8 * cm],
    ))
    story.append(P("Table 2.2 — Product Backlog", "Caption"))

    story.append(P("2.5 Architecture générale de la solution", "HSection"))
    story.append(P(
        "La solution proposée repose sur une architecture web modulaire composée d'une interface "
        "utilisateur, d'une API backend, d'une base de données relationnelle et d'un module "
        "d'intelligence artificielle."
    ))
    story.append(P(
        "L'objectif de cette architecture est de séparer clairement les responsabilités entre les "
        "différentes parties du système afin de faciliter la maintenance, l'évolution et les tests de "
        "l'application."
    ))
    story.append(fig(DIAG / "figure_2_1_architecture.png",
                     "Figure 2.1 — Architecture générale de la solution", width=15.5 * cm))
    story.append(P(
        "L'interface utilisateur sera développée avec Angular. Elle permettra aux utilisateurs "
        "d'accéder aux différentes fonctionnalités selon leur rôle : consultation des ressources, "
        "téléchargement des documents, gestion des ressources, administration et interaction avec "
        "l'assistant intelligent."
    ))
    story.append(P(
        "Le backend sera développé avec FastAPI. Il exposera les services REST nécessaires "
        "à la communication entre l'interface web, la base de données et le module d'intelligence artificielle."
    ))
    story.append(P(
        "La base de données MySQL assure la persistance des données métier telles que les "
        "utilisateurs, les rôles, les ressources de connaissance, les catégories, les sessions "
        "d'assistant, les messages et les citations."
    ))
    story.append(P(
        "Le module d'intelligence artificielle repose sur LangChain et ChromaDB. Il permet "
        "d'indexer les ressources disponibles, de rechercher les passages pertinents et de générer des "
        "réponses contextualisées à partir des ressources validées."
    ))

    story.append(P("2.6 Architecture métier", "HSection"))
    story.append(P(
        "La plateforme repose sur le concept central de <b>ressource de connaissance</b>. Une ressource "
        "représente toute information officielle pouvant être consultée par les collaborateurs et "
        "exploitée par l'assistant intelligent."
    ))
    story.append(P("Une ressource de connaissance peut correspondre à :"))
    story.extend(bullets([
        "un document ;",
        "une publication interne ;",
        "une procédure ;",
        "une note de service ;",
        "un guide ;",
        "toute autre information validée par l'entreprise.",
    ]))
    story.append(P(
        "Cette approche permet d'unifier la gestion des documents et des publications au sein "
        "d'un même modèle métier. Une publication interne n'est pas un forum : elle est un type "
        "de ressource, sans entités Post ou Commentaire."
    ))
    story.append(make_table(
        ["Concept métier", "Description"],
        [
            ["Utilisateur", "Personne authentifiée autorisée à accéder à la plateforme."],
            ["Rôle", "Niveau d'autorisation (Employé, Manager, Administrateur)."],
            ["RessourceDeConnaissance", "Entité centrale : document, procédure, note, guide, publication interne, etc."],
            ["Catégorie", "Permet d'organiser les ressources de connaissance."],
            ["SessionAssistant", "Session de dialogue entre un utilisateur et l'assistant intelligent (historique RAG)."],
            ["MessageAssistant", "Question de l'utilisateur ou réponse de l'assistant dans une session."],
            ["Citation", "Extrait d'une ressource utilisé pour justifier une réponse de l'assistant."],
        ],
        col_widths=[4.5 * cm, 11.5 * cm],
    ))
    story.append(P("Table 2.3 — Principaux concepts métier (vocabulaire corrigé)", "Caption"))

    story.append(P("2.7 Architecture du module d'intelligence artificielle", "HSection"))
    story.append(P(
        "Le module d'intelligence artificielle est basé sur une approche RAG (Retrieval Augmented "
        "Generation). Cette approche permet au modèle de langage de générer des réponses à partir "
        "de documents récupérés dans une base de connaissances."
    ))
    story.append(P("Le fonctionnement général du module est le suivant :"))
    story.extend(numbered([
        "L'utilisateur pose une question depuis l'interface web.",
        "La question est envoyée au backend FastAPI.",
        "Le système recherche les ressources les plus pertinentes dans ChromaDB.",
        "Les passages trouvés sont transmis au modèle de langage via LangChain.",
        "Le modèle génère une réponse basée sur les sources disponibles.",
        "La réponse et les sources sont renvoyées à l'utilisateur.",
    ]))
    story.append(fig(DIAG / "figure_2_2_pipeline_assistant.png",
                     "Figure 2.2 — Pipeline de l'assistant intelligent (RAG)", width=16 * cm))
    story.append(P(
        "Cette architecture permet d'éviter que l'assistant génère des réponses non fondées. "
        "Les réponses doivent être produites uniquement à partir des ressources disponibles dans la plateforme."
    ))

    story.append(P("2.8 Indexation des ressources de connaissance", "HSection"))
    story.append(P(
        "Lorsqu'un administrateur ou un manager ajoute une ressource, celle-ci est enregistrée dans "
        "la base de données relationnelle. Si la ressource est exploitable par l'assistant intelligent, "
        "une tâche d'indexation est lancée."
    ))
    story.append(P("Le processus d'indexation comprend les étapes suivantes :"))
    story.extend(numbered([
        "extraction du texte ;",
        "découpage du texte en fragments ;",
        "génération des embeddings ;",
        "stockage des vecteurs dans ChromaDB ;",
        "association entre les fragments indexés et la ressource originale.",
    ]))
    story.append(fig(DIAG / "figure_2_3_indexation.png",
                     "Figure 2.3 — Processus d'indexation des ressources de connaissance",
                     width=16 * cm))
    story.append(P(
        "Lorsqu'une ressource est supprimée, les fragments correspondants doivent également être "
        "supprimés de la base vectorielle afin d'empêcher l'assistant d'utiliser des informations obsolètes."
    ))

    story.append(P("2.9 Diagramme de cas d'utilisation", "HSection"))
    story.append(P(
        "Le diagramme de cas d'utilisation permet de représenter les principales interactions entre "
        "les acteurs du système et les fonctionnalités offertes par la plateforme."
    ))
    story.append(P(
        "Les trois acteurs identifiés (Administrateur, Manager, Employé) ne disposent pas de "
        "privilèges indépendants : chaque rôle englobe les droits du rôle précédent et y ajoute "
        "ses propres responsabilités. Le Manager hérite ainsi des cas d'utilisation de l'Employé, "
        "et l'Administrateur hérite de ceux du Manager."
    ))
    story.append(fig(DIAG / "figure_2_4_cas_utilisation.png",
                     "Figure 2.4 — Diagramme de cas d'utilisation (avec généralisation des acteurs)",
                     width=16 * cm))

    story.append(P("2.10 Description textuelle des cas d'utilisation principaux", "HSection"))
    story.append(P(
        "Afin de préciser le comportement attendu du système, les deux cas d'utilisation les plus "
        "significatifs sont détaillés ci-dessous sous forme de fiches descriptives."
    ))
    story.append(make_table(
        ["Élément", "Description"],
        [
            ["Cas", "Poser une question à l'assistant intelligent"],
            ["Acteur principal", "Employé (également accessible au Manager et à l'Administrateur)"],
            ["Pré-conditions", "L'utilisateur est authentifié"],
            ["Scénario nominal",
             "1. L'utilisateur saisit une question. 2. Recherche vectorielle dans ChromaDB. "
             "3. Passages transmis au LLM via LangChain. 4. Réponse + citations générées. "
             "5. Affichage à l'utilisateur."],
            ["Post-conditions",
             "La question et la réponse sont enregistrées dans la SessionAssistant."],
        ],
        col_widths=[3.5 * cm, 12.5 * cm],
    ))
    story.append(P("Table 2.4 — Fiche descriptive — Poser une question à l'assistant intelligent", "Caption"))

    story.append(make_table(
        ["Élément", "Description"],
        [
            ["Cas", "Ajouter une ressource de connaissance"],
            ["Acteur principal", "Manager (également accessible à l'Administrateur)"],
            ["Pré-conditions", "L'utilisateur est authentifié avec un rôle Manager ou Administrateur"],
            ["Scénario nominal",
             "1. Saisie des métadonnées et sélection d'une catégorie. 2. Enregistrement MySQL. "
             "3. Stockage du fichier et lancement de l'indexation. 4. Découpage, vectorisation, "
             "stockage ChromaDB. 5. Ressource consultable et exploitable par l'assistant."],
            ["Post-conditions", "La ressource est disponible et indexée (estIndexe = true)."],
            ["Scénario alternatif",
             "Si le fichier est invalide, le système affiche une erreur et annule l'enregistrement."],
        ],
        col_widths=[3.5 * cm, 12.5 * cm],
    ))
    story.append(P("Table 2.5 — Fiche descriptive — Ajouter une ressource de connaissance", "Caption"))

    story.append(P("2.11 Diagramme de classes", "HSection"))
    story.append(P(
        "Le diagramme de classes traduit les concepts métier en un modèle de données conceptuel. "
        "Il servira de base à la conception du schéma relationnel MySQL lors du développement."
    ))
    story.append(fig(DIAG / "figure_2_5_diagramme_classes.png",
                     "Figure 2.5 — Diagramme de classes (modèle métier corrigé)",
                     width=16 * cm, max_h=18 * cm))
    story.append(P(
        "Une ressource de connaissance appartient à une catégorie ; un utilisateur (manager ou "
        "administrateur) peut en publier plusieurs. L'historique du chat avec l'assistant est "
        "modélisé par <b>SessionAssistant</b> et <b>MessageAssistant</b> : il ne s'agit pas d'un forum "
        "(pas d'entités Post / Commentaire). Une publication interne est simplement une valeur de "
        "l'attribut <i>type</i> de RessourceDeConnaissance."
    ))
    story.append(P(
        "Chaque réponse de l'assistant peut s'appuyer sur une ou plusieurs <b>Citations</b> ; chaque "
        "citation référence la RessourceDeConnaissance d'origine via un extrait textuel. Ce concept "
        "remplace l'ancien libellé flou « Source IA »."
    ))

    story.append(P("2.12 Diagramme de séquence — Poser une question à l'assistant", "HSection"))
    story.append(P(
        "Le diagramme de séquence ci-dessous détaille les interactions entre les composants lors "
        "du cas d'utilisation « Poser une question à l'assistant intelligent »."
    ))
    story.append(fig(DIAG / "figure_2_6_sequence_question.png",
                     "Figure 2.6 — Diagramme de séquence — Poser une question à l'assistant intelligent",
                     width=16 * cm))

    story.append(P("2.13 Diagramme de séquence — Ajouter une ressource de connaissance", "HSection"))
    story.append(P(
        "Le second diagramme de séquence décrit le scénario d'ajout d'une ressource, incluant "
        "la persistance MySQL, le stockage du fichier et le pipeline d'indexation vers ChromaDB."
    ))
    story.append(fig(DIAG / "figure_2_7_sequence_ajout_ressource.png",
                     "Figure 2.7 — Diagramme de séquence — Ajouter une ressource de connaissance",
                     width=16 * cm))

    story.append(Spacer(1, 1.5 * cm))
    story.append(P(
        "— Fin du rapport d'analyse et de conception (preview 6) —",
        "Caption",
    ))

    doc = Doc(str(OUT))
    doc.build(story)
    print(f"PDF généré : {OUT}")
    return OUT


if __name__ == "__main__":
    build()
