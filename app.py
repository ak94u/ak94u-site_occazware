import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Charger les variables du fichier .env
load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION SÉCURISÉE DE LA BD ---
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Récupération de la clé secrète
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)