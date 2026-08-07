# Occaz' Gaming — Plateforme E-Commerce

Occaz' Gaming est une application web e-commerce développée en Python avec le framework Flask. La plateforme est spécialisée dans l'achat et la revente de matériel informatique et d'équipements gaming d'occasion. Elle intègre un système complet de gestion de catalogue, une interface d'administration avec suivi financier, un tunnel de commande sécurisé et un hébergement de médias basé sur le cloud.

---

## Stack Technique

* **Backend :** Python 3, Flask (Architecture MVC / Blueprints)
* **Base de données :** MySQL (Hébergée sur Alwaysdata) / Flask-SQLAlchemy
* **Frontend :** Jinja2, Tailwind CSS, Alpine.js, JavaScript (ES6)
* **Gestion des Médias :** Cloudinary SDK (Stockage cloud des visuels et vidéos produits)
* **Déploiement & Serveur Web :** Render (Web Service) & Gunicorn
* **Versionning :** Git / GitHub

---

## Fonctionnalités Principales

* **Interface Utilisateur & Responsive Design :**
  * Design fluide adapté aux écrans Desktop, Tablettes et Mobiles.
  * Barre de navigation basse (Bottom Navigation Bar) dédiée aux smartphones.
  * Prise en charge du thème clair et du thème sombre.
  * Gestion complète des cookies techniques et bannière de consentement.

* **Catalogue & Expérience Client :**
  * Exploration filtrable du matériel gaming (PC Fixes, Portables, Composants).
  * Barre de recherche, fiches produits détaillées et panier dynamique.
  * Assistant virtuel (Chatbot) pour guider et conseiller les utilisateurs.

* **Espace Administrateur :**
  * Tableau de bord financier (Suivi du chiffre d'affaires et historique des transactions).
  * Gestion CRUD du catalogue (Ajout, modification, masquage et suppression).
  * Envoi dynamique des visuels produits vers Cloudinary.

* **Sécurité & Authentification :**
  * Inscription, connexion, réinitialisation de mot de passe et gestion des sessions.
  * Contrôle d'accès basé sur les rôles (`user`, `admin`).
  * Conformité RGPD : Pages légales (CGV, Mentions légales, PDC, GDC).

---

## Architecture du Projet

```text
ak94u-site_occazware/
├── __pycache__/          # Fichiers de cache Python
├── controllers/          # Logique des routes (Blueprints)
│   ├── __pycache__/
│   ├── a_propos.py
│   ├── accueil.py
│   ├── admin.py          # Tableau de bord et gestion du catalogue
│   ├── auth_mot_de_passe.py
│   ├── cgv.py
│   ├── chatbot.py        # Assistant virtuel
│   ├── connexion.py      # Authentification et gestion de session
│   ├── cookies.py
│   ├── gdc.py
│   ├── magasin.py        # Catalogue et recherche
│   ├── mention_legales.py
│   ├── panier.py         # Tunnel de commande
│   └── pdc.py
├── models/               # Modèles de données SQLAlchemy
│   ├── __pycache__/
│   └── db.py             # Définition des entités et relations BDD
├── static/               # Assets statiques frontend
│   ├── img/              # Images, logos et assets de la charte
│   │   └── favicons/     # Packages d'icônes multi-résolutions (.ico, .png)
│   ├── js/               # Scripts client (script.js)
│   └── video/            # Vidéo d'ambiance d'accueil
├── templates/            # Vues Jinja2 (HTML)
│   ├── doc/
│   ├── a_propos.html
│   ├── accueil.html
│   ├── admin.html
│   ├── apercu_mail.html
│   ├── assistant.html
│   ├── auth_mot_de_passe.html
│   ├── base.html         # Template racine responsive (Header, Nav Mobile, Footer)
│   ├── cgv.html
│   ├── connexion.html
│   ├── gdc.html
│   ├── magasin.html
│   ├── mention_legales.html
│   ├── nouveau_mdp.html
│   ├── paiement.html
│   ├── panier.html
│   ├── parametres.html
│   ├── pdc.html
│   └── succes.html
├── .env                  # Variables d'environnement (non versionné)
├── .gitignore            # Règles d'exclusion Git
├── app.py                # Point d'entrée principal de l'application Flask
├── LICENSE               # Licence du projet
├── Procfile              # Instruction de démarrage pour le serveur Gunicorn
├── README.md             # Documentation du projet
└── requirements.txt      # Dépendances Python

```
## Installation & Configuration Locale

### 1. Cloner le dépôt
```bash
git clone https://github.com/votre-user/ak94u-site_occazware.git
cd ak94u-site_occazware
```

## Configurer l'environnement virtuel et installer les dépendances

python -m venv venv

# Activation sur Windows :
venv\Scripts\activate

# Activation sur Linux/macOS :
source venv/bin/activate

# Installation des paquets
pip install -r requirements.txt

## Extrait de code .env

FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=votre_cle_secrete_flask

# Base de données MySQL (Alwaysdata)
DATABASE_URL=mysql+pymysql://utilisateur:motdepasse@serveur.alwaysdata.net/nom_bdd

# Cloudinary (Gestion des médias)
CLOUDINARY_CLOUD_NAME=votre_cloud_name
CLOUDINARY_API_KEY=votre_api_key
CLOUDINARY_API_SECRET=votre_api_secret

## Lancer l'application en locale 

flask run

L'application sera accessible sur l'adresse suivante : http://127.0.0.1:5000

## Visite du site sur internet

lien du site : https://occazware.onrender.com

## Auteur

BEN ABDALLAH AKRAM

