"""
Seed demo data for local XAMPP MySQL.
Run (with venv active, from backend/):

  python seed_demo.py

All users password: Password123!
"""

from app.core.security import hash_password
from app.database import SessionLocal, engine, Base
from app.models import assistant, categorie, ressource, role, user  # noqa: F401
from app.models.assistant import Citation, MessageAssistant, SessionAssistant
from app.models.categorie import Categorie
from app.models.ressource import RessourceDeConnaissance
from app.models.role import Role
from app.models.user import User
from app.services.indexer import clear_vector_store, index_ressource
from sqlalchemy import text

Base.metadata.create_all(bind=engine)

PASSWORD = "Password123!"


def ensure_contenu_column() -> None:
    with engine.begin() as conn:
        exists = conn.execute(
            text(
                """
                SELECT COUNT(*) FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'ressources_connaissance'
                  AND COLUMN_NAME = 'contenu'
                """
            )
        ).scalar()
        if not exists:
            conn.execute(
                text(
                    "ALTER TABLE ressources_connaissance "
                    "ADD COLUMN contenu TEXT NULL AFTER type"
                )
            )


def seed() -> None:
    ensure_contenu_column()
    db = SessionLocal()
    try:
        db.query(Citation).delete()
        db.query(MessageAssistant).delete()
        db.query(SessionAssistant).delete()
        db.query(RessourceDeConnaissance).delete()
        db.query(User).delete()
        db.query(Categorie).delete()
        db.query(Role).delete()
        db.commit()

        roles = [
            Role(id=1, nom="Administrateur"),
            Role(id=2, nom="Manager"),
            Role(id=3, nom="Employé"),
        ]
        db.add_all(roles)
        db.flush()

        hashed = hash_password(PASSWORD)
        users = [
            User(
                id=1,
                nom="Bziouech",
                prenom="Jawher",
                email="admin@example.com",
                mot_de_passe=hashed,
                role_id=1,
            ),
            User(
                id=2,
                nom="Ben Ali",
                prenom="Sarra",
                email="manager@example.com",
                mot_de_passe=hashed,
                role_id=2,
            ),
            User(
                id=3,
                nom="Trabelsi",
                prenom="Omar",
                email="employe@example.com",
                mot_de_passe=hashed,
                role_id=3,
            ),
            User(
                id=4,
                nom="Gharbi",
                prenom="Amira",
                email="amira.gharbi@example.com",
                mot_de_passe=hashed,
                role_id=3,
            ),
            User(
                id=5,
                nom="Jebali",
                prenom="Karim",
                email="karim.jebali@example.com",
                mot_de_passe=hashed,
                role_id=2,
            ),
        ]
        db.add_all(users)
        db.flush()

        categories = [
            Categorie(
                id=1,
                nom="Procédures",
                description="Procédures opérationnelles internes Nouvelair",
            ),
            Categorie(
                id=2,
                nom="Sécurité",
                description="Règles et consignes de sûreté / sécurité",
            ),
            Categorie(
                id=3,
                nom="RH",
                description="Ressources humaines, onboarding et notes internes",
            ),
            Categorie(
                id=4,
                nom="Commercial",
                description="Offres, ventes et relation client",
            ),
            Categorie(
                id=5,
                nom="IT & Outils",
                description="Guides outils numériques et bonnes pratiques",
            ),
        ]
        db.add_all(categories)
        db.flush()

        ressources = [
            RessourceDeConnaissance(
                titre="Procédure embarquement passagers",
                type="procedure",
                contenu=(
                    "Objectif : standardiser l'embarquement.\n\n"
                    "1. Vérifier les documents de voyage.\n"
                    "2. Contrôler la carte d'embarquement.\n"
                    "3. Orienter les passagers prioritaires.\n"
                    "4. Clôturer le vol avec le rapport cabine."
                ),
                categorie_id=1,
                auteur_id=2,
                est_indexe=False,
            ),
            RessourceDeConnaissance(
                titre="Consignes sécurité piste",
                type="guide",
                contenu=(
                    "Rappel sécurité piste :\n"
                    "- Port des EPI obligatoire\n"
                    "- Respect des zones balisées\n"
                    "- Signalement immédiat de tout incident\n"
                    "- Coordination permanente avec le dispatch"
                ),
                categorie_id=2,
                auteur_id=1,
                est_indexe=False,
            ),
            RessourceDeConnaissance(
                titre="Bienvenue nouveaux collaborateurs",
                type="blog",
                contenu=(
                    "Bienvenue dans la base de connaissances Nouvelair.\n\n"
                    "Cet espace centralise procédures, notes et publications internes.\n"
                    "Utilisez la recherche et les catégories pour trouver rapidement "
                    "l'information validée.\n\nBonne intégration !"
                ),
                categorie_id=3,
                auteur_id=1,
                est_indexe=False,
            ),
            RessourceDeConnaissance(
                titre="Processus réclamation client",
                type="procedure",
                contenu=(
                    "En cas de réclamation client :\n"
                    "1. Écouter et noter les faits\n"
                    "2. Ouvrir un ticket dans l'outil support\n"
                    "3. Escalader au Manager si délai > 24h\n"
                    "4. Confirmer la résolution au client"
                ),
                categorie_id=4,
                auteur_id=5,
                est_indexe=False,
            ),
            RessourceDeConnaissance(
                titre="Guide connexion VPN interne",
                type="guide",
                contenu=(
                    "Pour accéder aux ressources internes hors site :\n"
                    "1. Installer le client VPN approuvé\n"
                    "2. Se connecter avec les identifiants Nouvelair\n"
                    "3. Vérifier l'accès à la plateforme KB\n"
                    "4. Signaler tout problème à l'équipe IT"
                ),
                categorie_id=5,
                auteur_id=2,
                est_indexe=False,
            ),
            RessourceDeConnaissance(
                titre="Note interne : briefing matinal",
                type="note",
                contenu=(
                    "Point matinal équipes sol :\n"
                    "- Vérifier les vols du jour\n"
                    "- Confirmer les effectifs\n"
                    "- Remonter les alertes météo\n"
                    "- Partager les infos passagers prioritaires"
                ),
                categorie_id=1,
                auteur_id=3,
                est_indexe=False,
            ),
            RessourceDeConnaissance(
                titre="Publication : campagne été 2026",
                type="publication_interne",
                contenu=(
                    "La campagne commerciale été 2026 est lancée.\n"
                    "Focus destinations : Monastir, Djerba, Enfidha.\n"
                    "Les argumentaires ventes sont disponibles dans la catégorie Commercial."
                ),
                categorie_id=4,
                auteur_id=5,
                est_indexe=False,
            ),
            RessourceDeConnaissance(
                titre="Checklist départ vol",
                type="document",
                contenu=(
                    "Checklist départ :\n"
                    "[ ] Briefing équipage\n"
                    "[ ] Contrôle documents\n"
                    "[ ] Confirmation charge utile\n"
                    "[ ] Go / No-Go dispatch\n"
                    "[ ] Clôture dossier vol"
                ),
                categorie_id=1,
                auteur_id=2,
                est_indexe=False,
            ),
        ]
        db.add_all(ressources)
        db.commit()

        indexed = 0
        clear_vector_store()
        for r in db.query(RessourceDeConnaissance).all():
            if index_ressource(db, r):
                indexed += 1

        print("Demo data loaded.")
        print(f"Indexed resources for RAG: {indexed}")
        print("Password for all users:", PASSWORD)
        print("  admin@example.com     (Administrateur)")
        print("  manager@example.com   (Manager)")
        print("  employe@example.com   (Employé)")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
