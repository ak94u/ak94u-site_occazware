from flask import Blueprint, render_template

# On crée le Blueprint pour regrouper nos routes principales
page_parametres = Blueprint('parametres', __name__)

# Ta page de paramètres
@page_parametres.route('/parametres')
def index():
    return render_template('parametres.html')
