from flask import Blueprint, render_template

# On crée le Blueprint pour regrouper nos routes principales
page_accueil = Blueprint('accueil', __name__)

# Ta page d'accueil
@page_accueil.route('/')
def index():
    return render_template('accueil.html')
