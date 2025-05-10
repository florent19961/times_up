from flask import render_template
from app.routes import bp

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/configurer_partie')
def configurer_partie():
    return render_template('configurer_partie.html')

@bp.route('/rules')
def rules():
    return render_template('rules.html') 