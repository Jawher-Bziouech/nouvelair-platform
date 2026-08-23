# Maquette UI — Nouvelair Knowledge Platform

Maquette **cliquable**, style proche du site [nouvelair.com](https://www.nouvelair.com/fr/suivre-nos-vols) : header blanc, logo, boutons rouges, listes simples.

Ouvrir **`maquette/index.html` dans Chrome ou Edge** (double-clic). Pas l’aperçu Cursor.

## Ouvrir

Double-cliquez sur :

`maquette/index.html`

ou ouvrez le fichier dans **Chrome ou Edge** (double-clic). N’utilisez pas l’aperçu Cursor : les clics y sont souvent bloqués.

> Pas besoin de serveur ni d’API — c’est une maquette purement visuelle.

## Contenu

### Authentification
- Connexion collaborateurs (email / mot de passe)

### Front-office
- **Accueil** — liste, filtres, cartes ressources
- **Publier** — formulaire d’ajout (Manager / Admin)
- **Détail** — métadonnées, aperçu PDF, édition
- **Assistant** — chat RAG + sources / citations

### Back-office (Administrateur)
- **Tableau de bord** — stats + actions rapides
- **Utilisateurs** — CRUD
- **Rôles** — CRUD
- **Catégories** — CRUD

## Simulation des rôles

En haut de la page, basculez entre :
- **Employé** — consultation + assistant
- **Manager** — + Publier / modifier / supprimer
- **Administrateur** — + Back-office complet

## Pour l’encadrant

Cette maquette présente la structure navigationnelle et les écrans avant / pendant le développement.
Les écrans correspondent aux routes Angular :
`/auth/login`, `/home`, `/home/upload`, `/home/:id`, `/home/assistant`,
`/admin/dashboard`, `/admin/users`, `/admin/roles`, `/admin/categories`.
