from flask import render_template, request, session, redirect, url_for, flash
from app.routes import bp
from werkzeug.exceptions import BadRequest
from app.models import db, Word, Player
import random
from datetime import datetime

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

# Liste initiale de mots pour peupler la base de données
INITIAL_WORDS = [
    {"word": "maison", "difficulty": 1, "category": "habitat"},
    {"word": "voiture", "difficulty": 1, "category": "transport"},
    {"word": "ordinateur", "difficulty": 2, "category": "technologie"},
    {"word": "téléphone", "difficulty": 1, "category": "technologie"},
    {"word": "livre", "difficulty": 1, "category": "culture"},
    {"word": "table", "difficulty": 1, "category": "mobilier"},
    {"word": "chaise", "difficulty": 1, "category": "mobilier"},
    {"word": "fenêtre", "difficulty": 1, "category": "habitat"},
    {"word": "porte", "difficulty": 1, "category": "habitat"},
    {"word": "arbre", "difficulty": 1, "category": "nature"},
    {"word": "fleur", "difficulty": 1, "category": "nature"},
    {"word": "soleil", "difficulty": 1, "category": "nature"},
    {"word": "lune", "difficulty": 1, "category": "nature"},
    {"word": "étoile", "difficulty": 1, "category": "nature"},
    {"word": "nuage", "difficulty": 1, "category": "nature"},
    {"word": "pluie", "difficulty": 1, "category": "nature"},
    {"word": "neige", "difficulty": 1, "category": "nature"},
    {"word": "vent", "difficulty": 1, "category": "nature"},
    {"word": "montagne", "difficulty": 2, "category": "nature"},
    {"word": "rivière", "difficulty": 2, "category": "nature"},
    {"word": "océan", "difficulty": 2, "category": "nature"},
    {"word": "plage", "difficulty": 2, "category": "nature"},
    {"word": "forêt", "difficulty": 2, "category": "nature"},
    {"word": "jardin", "difficulty": 2, "category": "nature"},
    {"word": "animal", "difficulty": 1, "category": "faune"},
    {"word": "chien", "difficulty": 1, "category": "faune"},
    {"word": "chat", "difficulty": 1, "category": "faune"},
    {"word": "oiseau", "difficulty": 2, "category": "faune"},
    {"word": "poisson", "difficulty": 2, "category": "faune"},
    {"word": "fruit", "difficulty": 1, "category": "nourriture"},
    {"word": "légume", "difficulty": 2, "category": "nourriture"},
    {"word": "pain", "difficulty": 1, "category": "nourriture"},
    {"word": "eau", "difficulty": 1, "category": "nourriture"},
    {"word": "café", "difficulty": 1, "category": "nourriture"},
    {"word": "thé", "difficulty": 1, "category": "nourriture"},
    {"word": "vin", "difficulty": 1, "category": "nourriture"},
    {"word": "bière", "difficulty": 1, "category": "nourriture"},
    {"word": "sucre", "difficulty": 1, "category": "nourriture"},
    {"word": "sel", "difficulty": 1, "category": "nourriture"},
    {"word": "poivre", "difficulty": 2, "category": "nourriture"}
]

def init_db():
    """Initialise la base de données avec les mots par défaut."""
    # Vérifier si la base de données est vide
    if Word.query.count() == 0:
        # Ajouter les mots initiaux
        for word_data in INITIAL_WORDS:
            word = Word(**word_data)
            db.session.add(word)
        db.session.commit()

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
    required_params = ['nb_joueurs', 'choix_mots', 'nb_mots_total']
    if not all(param in session for param in required_params):
        flash('Configuration de partie invalide. Veuillez recommencer.', 'error')
        return redirect(url_for('main.configurer_partie'))

    # Vérifier que les valeurs sont valides
    try:
        nb_mots_total = int(session['nb_mots_total'])
        if not (20 <= nb_mots_total <= 80):
            raise ValueError("Nombre de mots total invalide")
    except (ValueError, TypeError):
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

def calculate_words_distribution(nb_joueurs, nb_mots_total):
    """Calcule la répartition équitable des mots entre les joueurs."""
    base_words = nb_mots_total // nb_joueurs
    extra_words = nb_mots_total % nb_joueurs
    
    # Créer une liste avec la distribution de base
    distribution = [base_words] * nb_joueurs
    
    # Ajouter les mots restants un par un aux premiers joueurs
    for i in range(extra_words):
        distribution[i] += 1
        
    return distribution

@bp.route('/mots_joueur/<int:player_index>', methods=['GET', 'POST'])
def mots_joueur(player_index):
    # Vérifier que l'index est valide
    if not isinstance(player_index, int) or player_index < 0 or player_index >= session.get('nb_joueurs', 0):
        flash('Index de joueur invalide', 'error')
        return redirect(url_for('main.choix_mots_aleatoire'))
    
    # Récupérer le nom du joueur
    player_name = session.get('noms_joueurs', [''] * session['nb_joueurs'])[player_index]
    
    # Calculer la répartition des mots
    nb_joueurs = session.get('nb_joueurs', 0)
    nb_mots_total = session.get('nb_mots_total', 50)
    mots_distribution = calculate_words_distribution(nb_joueurs, nb_mots_total)
    
    # Créer ou récupérer le joueur dans la base de données
    game_session = session.get('game_session')
    if not game_session:
        game_session = str(datetime.utcnow().timestamp())
        session['game_session'] = game_session
    
    player = Player.query.filter_by(name=player_name, game_session=game_session).first()
    if not player:
        player = Player(name=player_name, game_session=game_session)
        db.session.add(player)
        db.session.commit()

    if request.method == 'POST':
        # Récupérer et nettoyer les mots
        new_mots = []
        for i in range(mots_distribution[player_index]):
            mot = request.form.get(f'mot_{i}', '').strip()
            
            # Validation du mot
            if mot:
                # Limiter la longueur du mot
                if len(mot) > 50:
                    flash('Les mots ne doivent pas dépasser 50 caractères', 'error')
                    return render_template('mots_joueur.html', 
                                        player_index=player_index,
                                        player_name=player_name,
                                        mots=player.words.all(),
                                        nb_mots_total=mots_distribution[player_index]), 400
                
                # Nettoyer le mot (échapper les caractères HTML)
                mot = mot.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                
                # Créer ou récupérer le mot dans la base de données
                word = Word.query.filter_by(word=mot).first()
                if not word:
                    word = Word(word=mot, is_custom=True)
                    db.session.add(word)
                    db.session.commit()
                
                new_mots.append(word)
        
        # Mettre à jour les mots du joueur
        player.words = new_mots
        db.session.commit()
        
        flash('Les mots ont été enregistrés avec succès', 'success')
        return redirect(url_for('main.choix_mots_aleatoire'))
    
    return render_template('mots_joueur.html', 
                         player_index=player_index,
                         player_name=player_name,
                         mots=player.words.all(),
                         nb_mots_total=mots_distribution[player_index])

@bp.route('/generate_random_word', methods=['POST'])
def generate_random_word():
    """Génère un mot aléatoire depuis la base de données, en évitant les doublons."""
    # S'assurer que la base de données est initialisée
    init_db()
    
    # Récupérer la session de jeu
    game_session = session.get('game_session')
    if not game_session:
        return {'error': 'Session de jeu invalide'}, 400
    
    # Récupérer tous les joueurs de la session
    players = Player.query.filter_by(game_session=game_session).all()
    
    # Récupérer tous les mots déjà utilisés dans cette session
    used_words = set()
    for player in players:
        for word in player.words:
            used_words.add(word.word)
    
    # Récupérer un mot aléatoire qui n'est pas personnalisé et qui n'a pas déjà été utilisé
    word = Word.query.filter(
        Word.is_custom == False,
        ~Word.word.in_(used_words)
    ).order_by(db.func.random()).first()
    
    if word:
        return {'word': word.word}, 200
    else:
        return {'error': 'Aucun mot disponible'}, 404 