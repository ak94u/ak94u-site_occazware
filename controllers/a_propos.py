from flask import Blueprint, render_template

# On crée le Blueprint pour regrouper nos routes principales
page_a_propos = Blueprint('a_propos', __name__)

# Ta page À propos
@page_a_propos.route('/a_propos')
def index():
    return render_template('a_propos.html')
