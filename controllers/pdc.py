from flask import Blueprint, render_template

pdc_blueprint = Blueprint('pdc', __name__)

@pdc_blueprint.route('/pdc')
def pdc():
    return render_template('pdc.html')