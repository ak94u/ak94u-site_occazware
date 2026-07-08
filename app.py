import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Importer le blueprint depuis le dossier controllers
from controllers.accueil import page_accueil
from controllers.parametres import page_parametres
from controllers.a_propos import page_a_propos
from controllers.magasin import page_magasin

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

db = SQLAlchemy(app)

# --- ENREGISTREMENT DES ROUTEURS (BLUEPRINTS) ---
# On dit à Flask d'activer les routes définies dans le controller
app.register_blueprint(page_accueil)
app.register_blueprint(page_parametres)
app.register_blueprint(page_a_propos)
app.register_blueprint(page_magasin)

if __name__ == '__main__':
    app.run(debug=True)