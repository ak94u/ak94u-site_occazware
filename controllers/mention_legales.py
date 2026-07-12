from flask import Blueprint, render_template

mention_legales = Blueprint('mention_legales', __name__)

@mention_legales.route('/mention_legales')
def page_mention_legales():
    return render_template('mention_legales.html')