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
    # Vérifier que les paramètres nécessaires sont en session
    required_params = ['nb_joueurs', 'choix_mots']
    if not all(param in session for param in required_params):
        flash('Configuration de partie invalide. Veuillez recommencer.', 'error')
        return redirect(url_for('main.configurer_partie'))

    if request.method == 'POST':
        # Récupérer et nettoyer les noms des joueurs
        noms_joueurs = []
        for i in range(session['nb_joueurs']):
            nom = request.form.get(f'joueur_{i}', '').strip()
            
            # Validation du nom
            if not nom:
                flash('Tous les joueurs doivent avoir un nom', 'error')
                return render_template('choix_mots_aleatoire.html'), 400
            
            # Limiter la longueur du nom
            if len(nom) > 20:
                flash('Les noms ne doivent pas dépasser 20 caractères', 'error')
                return render_template('choix_mots_aleatoire.html'), 400
            
            # Nettoyer le nom (échapper les caractères HTML)
            nom = nom.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            noms_joueurs.append(nom)
        
        # Vérifier les doublons
        if len(set(noms_joueurs)) != len(noms_joueurs):
            flash('Des joueurs ont le même nom. Veuillez modifier les pseudonymes identiques.', 'error')
            return render_template('choix_mots_aleatoire.html'), 400
        
        # Stocker les noms en session
        session['noms_joueurs'] = noms_joueurs
        session.modified = True
        
        # Rediriger vers la page de jeu
        return redirect(url_for('main.play'))
    
    # Initialiser ou mettre à jour la liste des noms
    if 'noms_joueurs' not in session:
        session['noms_joueurs'] = [''] * session['nb_joueurs']
        session.modified = True
    else:
        # Si le nombre de joueurs a changé, ajuster la liste des noms
        current_noms = session['noms_joueurs']
        new_noms = [''] * session['nb_joueurs']
        # Copier les noms existants jusqu'à la nouvelle taille
        for i in range(min(len(current_noms), session['nb_joueurs'])):
            new_noms[i] = current_noms[i]
        session['noms_joueurs'] = new_noms
        session.modified = True
    
    return render_template('choix_mots_aleatoire.html')

@bp.route('/rules')
def rules():
    return render_template('rules.html')

@bp.route('/save_choice', methods=['POST'])
def save_choice():
    data = request.get_json()
    choice = data.get('choice')
    if choice in ['aleatoire', 'personnalise']:
        session['choix_mots'] = choice
        return {'status': 'success'}, 200
    return {'status': 'error', 'message': 'Choix invalide'}, 400

@bp.route('/save_player_name', methods=['POST'])
def save_player_name():
    data = request.get_json()
    player_index = data.get('index')
    player_name = data.get('name', '').strip()
    
    # Vérifier que l'index est valide
    if not isinstance(player_index, int) or player_index < 0 or player_index >= session.get('nb_joueurs', 0):
        return {'status': 'error', 'message': 'Index de joueur invalide'}, 400
    
    # Initialiser la liste si elle n'existe pas
    if 'noms_joueurs' not in session:
        session['noms_joueurs'] = [''] * session['nb_joueurs']
    
    # Sauvegarder le nom
    session['noms_joueurs'][player_index] = player_name
    
    # Marquer la session comme modifiée
    session.modified = True
    
    return {'status': 'success', 'saved_name': player_name}, 200 