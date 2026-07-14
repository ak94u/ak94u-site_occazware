from flask import Blueprint, render_template

gdc_blueprint = Blueprint('gdc', __name__)

@gdc_blueprint.route('/gdc')
def gdc():
    return render_template('gdc.html')