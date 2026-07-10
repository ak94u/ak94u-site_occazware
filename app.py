import os
from flask import Flask
from dotenv import load_dotenv
from models.db import db

# Importer le blueprint depuis le dossier controllers
from controllers.accueil import page_accueil
from controllers.parametres import page_parametres
from controllers.a_propos import page_a_propos
from controllers.magasin import page_magasin
from controllers.admin import page_admin
from controllers.connexion import auth_blueprint
from controllers.panier import panier_blueprint

load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION (Inchangée) ---
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# Configuration du dossier où seront sauvegardées les images des produits
UPLOAD_FOLDER = os.path.join('static', 'img')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Créer le dossier s'il n'existe pas encore
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db.init_app(app)

# --- ENREGISTREMENT DES ROUTEURS (BLUEPRINTS) ---
# On dit à Flask d'activer les routes définies dans le controller
app.register_blueprint(page_accueil)
app.register_blueprint(page_parametres)
app.register_blueprint(page_a_propos)
app.register_blueprint(page_magasin)
app.register_blueprint(page_admin)
app.register_blueprint(auth_blueprint)
app.register_blueprint(panier_blueprint)

if __name__ == '__main__':
    app.run(debug=True)