-- Demo data for Nouvelair Knowledge Platform (XAMPP / phpMyAdmin)
-- 1) Create DB if needed, select it, then import this file
-- 2) Or: start the backend once first (creates tables), then import
--
-- Login password for ALL demo users: Password123!

CREATE DATABASE IF NOT EXISTS nouvelair_kb
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE nouvelair_kb;

SET FOREIGN_KEY_CHECKS = 0;
DELETE FROM ressources_connaissance;
DELETE FROM utilisateurs;
DELETE FROM categories;
DELETE FROM roles;
SET FOREIGN_KEY_CHECKS = 1;

-- Ensure contenu column exists (safe if already added by the app)
SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = 'nouvelair_kb'
    AND TABLE_NAME = 'ressources_connaissance'
    AND COLUMN_NAME = 'contenu'
);
SET @sql := IF(
  @col_exists = 0,
  'ALTER TABLE ressources_connaissance ADD COLUMN contenu TEXT NULL AFTER type',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

INSERT INTO roles (id, nom) VALUES
  (1, 'Administrateur'),
  (2, 'Manager'),
  (3, 'Employé');

-- bcrypt hash for: Password123!
INSERT INTO utilisateurs (id, nom, prenom, email, mot_de_passe, role_id) VALUES
  (1, 'Bziouech', 'Jawher', 'admin@example.com',
   '$2b$12$Y0GuKiKoydIoReVZomJOqOpZM5OMDS3BjGn.2WoO1Lo6HXRadA2eu', 1),
  (2, 'Ben Ali', 'Sarra', 'manager@example.com',
   '$2b$12$Y0GuKiKoydIoReVZomJOqOpZM5OMDS3BjGn.2WoO1Lo6HXRadA2eu', 2),
  (3, 'Trabelsi', 'Omar', 'employe@example.com',
   '$2b$12$Y0GuKiKoydIoReVZomJOqOpZM5OMDS3BjGn.2WoO1Lo6HXRadA2eu', 3),
  (4, 'Gharbi', 'Amira', 'amira.gharbi@example.com',
   '$2b$12$Y0GuKiKoydIoReVZomJOqOpZM5OMDS3BjGn.2WoO1Lo6HXRadA2eu', 3),
  (5, 'Jebali', 'Karim', 'karim.jebali@example.com',
   '$2b$12$Y0GuKiKoydIoReVZomJOqOpZM5OMDS3BjGn.2WoO1Lo6HXRadA2eu', 2);

INSERT INTO categories (id, nom, description) VALUES
  (1, 'Procédures', 'Procédures opérationnelles internes Nouvelair'),
  (2, 'Sécurité', 'Règles et consignes de sûreté / sécurité'),
  (3, 'RH', 'Ressources humaines, onboarding et notes internes'),
  (4, 'Commercial', 'Offres, ventes et relation client'),
  (5, 'IT & Outils', 'Guides outils numériques et bonnes pratiques');

INSERT INTO ressources_connaissance
  (id, titre, type, contenu, type_fichier, chemin_fichier, est_indexe, categorie_id, auteur_id)
VALUES
  (1, 'Procédure embarquement passagers', 'procedure',
   'Objectif : standardiser l''embarquement.\n\n1. Vérifier les documents de voyage.\n2. Contrôler la carte d''embarquement.\n3. Orienter les passagers prioritaires.\n4. Clôturer le vol avec le rapport cabine.',
   NULL, NULL, 0, 1, 2),

  (2, 'Consignes sécurité piste', 'guide',
   'Rappel sécurité piste :\n- Port des EPI obligatoire\n- Respect des zones balisées\n- Signalement immédiat de tout incident\n- Coordination permanente avec le dispatch',
   NULL, NULL, 0, 2, 1),

  (3, 'Bienvenue nouveaux collaborateurs', 'blog',
   'Bienvenue dans la base de connaissances Nouvelair.\n\nCet espace centralise procédures, notes et publications internes.\nUtilisez la recherche et les catégories pour trouver rapidement l''information validée.\n\nBonne intégration !',
   NULL, NULL, 0, 3, 1),

  (4, 'Processus réclamation client', 'procedure',
   'En cas de réclamation client :\n1. Écouter et noter les faits\n2. Ouvrir un ticket dans l''outil support\n3. Escalader au Manager si délai > 24h\n4. Confirmer la résolution au client',
   NULL, NULL, 0, 4, 5),

  (5, 'Guide connexion VPN interne', 'guide',
   'Pour accéder aux ressources internes hors site :\n1. Installer le client VPN approuvé\n2. Se connecter avec les identifiants Nouvelair\n3. Vérifier l''accès à la plateforme KB\n4. Signaler tout problème à l''équipe IT',
   NULL, NULL, 0, 5, 2),

  (6, 'Note interne : briefing matinal', 'note',
   'Point matinal équipes sol :\n- Vérifier les vols du jour\n- Confirmer les effectifs\n- Remonter les alertes météo\n- Partager les infos passagers prioritaires',
   NULL, NULL, 0, 1, 3),

  (7, 'Publication : campagne été 2026', 'publication_interne',
   'La campagne commerciale été 2026 est lancée.\nFocus destinations : Monastir, Djerba, Enfidha.\nLes argumentaires ventes sont disponibles dans la catégorie Commercial.',
   NULL, NULL, 0, 4, 5),

  (8, 'Checklist départ vol', 'document',
   'Checklist départ :\n[ ] Briefing équipage\n[ ] Contrôle documents\n[ ] Confirmation charge utile\n[ ] Go / No-Go dispatch\n[ ] Clôture dossier vol',
   NULL, NULL, 0, 1, 2);
