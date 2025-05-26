from flask import render_template, request, session, redirect, url_for, flash
from app.routes import bp
from werkzeug.exceptions import BadRequest

def validate_game_settings(nb_equipes, nb_joueurs, choix_mots, choix_equipe, nb_mots_total, duree_manche, mot_reserve):
    """Valide les paramètres de la partie."""
    if not (2 <= nb_equipes <= 5):
        raise BadRequest("Le nombre d'équipes doit être entre 2 et 5")
    if not (nb_equipes * 2 <= nb_joueurs <= 20):
        raise BadRequest("Le nombre de joueurs doit être entre 2 fois le nombre d'équipes et 20")
    if choix_mots not in ['aleatoire', 'personnalise']:
        raise BadRequest("Choix de mots invalide")
    if choix_equipe not in ['aleatoire', 'personnalise']:
        raise BadRequest("Choix d'équipe invalide")
    if not (20 <= nb_mots_total <= 80):
        raise BadRequest("Le nombre de mots total doit être entre 20 et 80")
    if not (20 <= duree_manche <= 60):
        raise BadRequest("La durée de la manche doit être entre 20 et 60 secondes")
    if mot_reserve not in ['oui', 'non']:
        raise BadRequest("Choix de mot en réserve invalide")

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/configurer_partie', methods=['GET', 'POST'])
def configurer_partie():
    if request.method == 'POST':
        try:
            # Paramètres de base
            nb_equipes = int(request.form.get('nb-equipes', 2))
            nb_joueurs = int(request.form.get('nb-joueurs', 4))
            choix_mots = request.form.get('choix-mots', 'aleatoire')
            
            # Paramètres avancés
            choix_equipe = request.form.get('choix-equipe', 'personnalise')
            nb_mots_total = int(request.form.get('nb-mots-total', 50))
            duree_manche = int(request.form.get('duree-manche', 30))
            mot_reserve = request.form.get('choix-reserve', 'oui')
            
            # Validation des paramètres
            validate_game_settings(nb_equipes, nb_joueurs, choix_mots, choix_equipe, 
                                 nb_mots_total, duree_manche, mot_reserve)
            
            # Stocker en session
            session['nb_equipes'] = nb_equipes
            session['nb_joueurs'] = nb_joueurs
            session['choix_mots'] = choix_mots
            session['choix_equipe'] = choix_equipe
            session['nb_mots_total'] = nb_mots_total
            session['duree_manche'] = duree_manche
            session['mot_reserve'] = mot_reserve
            
            # Redirection selon le choix des mots
            if choix_mots == 'personnalise':
                return redirect(url_for('main.choix_mots_personnalise'))
            else:
                return redirect(url_for('main.choix_mots_aleatoire'))
            
        except (ValueError, BadRequest) as e:
            flash(str(e), 'error')
            return render_template('configurer_partie.html'), 400
    
    return render_template('configurer_partie.html')

@bp.route('/choix_mots_aleatoire', methods=['GET', 'POST'])
def choix_mots_aleatoire():
    if request.method == 'POST':
        # Récupérer les noms des joueurs
        noms_joueurs = []
        for i in range(session['nb_joueurs']):
            nom = request.form.get(f'joueur_{i}')
            if not nom or len(nom.strip()) == 0:
                flash('Tous les joueurs doivent avoir un nom', 'error')
                return render_template('choix_mots_aleatoire.html'), 400
            noms_joueurs.append(nom.strip())
        
        # Stocker les noms en session
        session['noms_joueurs'] = noms_joueurs
        
        # Rediriger vers la page de jeu
        return redirect(url_for('main.play'))
    
    return render_template('choix_mots_aleatoire.html')

@bp.route('/rules')
def rules():
    return render_template('rules.html') 