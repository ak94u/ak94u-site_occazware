from flask import Blueprint, render_template

cgv_blueprint = Blueprint('cgv', __name__)

@cgv_blueprint.route('/cgv')
def cgv():
    return render_template('cgv.html')