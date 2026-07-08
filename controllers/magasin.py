from flask import Blueprint, render_template

# On crée le Blueprint pour regrouper nos routes principales
page_magasin = Blueprint('magasin', __name__)

# Ta page de magasin
@page_magasin.route('/magasin')
def index():
    return render_template('magasin.html')
