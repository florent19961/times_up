from flask import render_template, request, session, redirect, url_for
from app.routes import bp

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/configurer_partie', methods=['GET', 'POST'])
def configurer_partie():
    if request.method == 'POST':
        nb_equipes = int(request.form.get('nb-equipes'))
        nb_mots = int(request.form.get('nb-mots'))
        choix_mots = request.form.get('choix-mots')
        
        # Ici vous pouvez utiliser ces valeurs pour configurer la partie
        # Par exemple, les stocker en session :
        session['nb_equipes'] = nb_equipes
        session['nb_mots'] = nb_mots
        session['choix_mots'] = choix_mots
        
        # Rediriger vers la page de jeu
        return redirect(url_for('play'))
    
    return render_template('configurer_partie.html')

@bp.route('/rules')
def rules():
    return render_template('rules.html') 