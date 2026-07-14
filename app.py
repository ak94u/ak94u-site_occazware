import os
from flask import Flask, request, g
from dotenv import load_dotenv
from models.db import db, mail

# Importer le blueprint depuis le dossier controllers
from controllers.accueil import page_accueil
from controllers.parametres import page_parametres
from controllers.a_propos import page_a_propos
from controllers.magasin import page_magasin
from controllers.admin import page_admin
from controllers.connexion import auth_blueprint
from controllers.panier import panier_blueprint
from controllers.auth_mot_de_passe import auth_mot_de_passe
from controllers.mention_legales import mention_legales
from controllers.cgv import cgv_blueprint
from controllers.pdc import pdc_blueprint
from controllers.cookies import cookies_blueprint
from controllers.gdc import gdc_blueprint


load_dotenv()

app = Flask(__name__)

#--- CONFIGURATION DU SERVEUR SMTP POUR L'ENVOI D'EMAILS ---
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']

app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
# L'expéditeur officiel DOIT impérativement être identique à ton MAIL_USERNAME (ton adresse gmail)
app.config['MAIL_DEFAULT_SENDER'] = ('Occaz Gaming 🎮', os.getenv('MAIL_USERNAME'))


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
mail.init_app(app)

# --- ENREGISTREMENT DES ROUTEURS (BLUEPRINTS) ---
# On dit à Flask d'activer les routes définies dans le controller
app.register_blueprint(page_accueil)
app.register_blueprint(page_parametres)
app.register_blueprint(page_a_propos)
app.register_blueprint(page_magasin)
app.register_blueprint(page_admin)
app.register_blueprint(auth_blueprint)
app.register_blueprint(panier_blueprint)
app.register_blueprint(auth_mot_de_passe)
app.register_blueprint(mention_legales)
app.register_blueprint(cgv_blueprint)
app.register_blueprint(pdc_blueprint)
app.register_blueprint(cookies_blueprint)
app.register_blueprint(gdc_blueprint)

@app.before_request
def check_consent():
    g.has_consent = request.cookies.get("consent") == "true"

if __name__ == '__main__':
    app.run(debug=True)