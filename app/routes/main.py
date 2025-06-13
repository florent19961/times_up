from flask import render_template, request, session, redirect, url_for, flash, jsonify
from app.routes import bp
from werkzeug.exceptions import BadRequest
from app.models import db, Word, Player
import random
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import json
import os

INITIAL_WORDS = [
    # Habitat et Maison
    {"word": "maison", "difficulty": 1, "category": "habitat"},
    {"word": "appartement", "difficulty": 1, "category": "habitat"},
    {"word": "immeuble", "difficulty": 1, "category": "habitat"},
    {"word": "château", "difficulty": 2, "category": "habitat"},
    {"word": "cabane", "difficulty": 1, "category": "habitat"},
    {"word": "tente", "difficulty": 1, "category": "habitat"},
    {"word": "igloo", "difficulty": 2, "category": "habitat"},
    {"word": "gratte-ciel", "difficulty": 2, "category": "habitat"},
    {"word": "fenêtre", "difficulty": 1, "category": "habitat"},
    {"word": "porte", "difficulty": 1, "category": "habitat"},
    {"word": "toit", "difficulty": 1, "category": "habitat"},
    {"word": "mur", "difficulty": 1, "category": "habitat"},
    {"word": "plafond", "difficulty": 1, "category": "habitat"},
    {"word": "sol", "difficulty": 1, "category": "habitat"},
    {"word": "escalier", "difficulty": 1, "category": "habitat"},
    {"word": "ascenseur", "difficulty": 1, "category": "habitat"},
    {"word": "balcon", "difficulty": 1, "category": "habitat"},
    {"word": "terrasse", "difficulty": 1, "category": "habitat"},
    {"word": "jardin", "difficulty": 1, "category": "habitat"},
    {"word": "garage", "difficulty": 1, "category": "habitat"},

    # Mobilier
    {"word": "table", "difficulty": 1, "category": "mobilier"},
    {"word": "chaise", "difficulty": 1, "category": "mobilier"},
    {"word": "canapé", "difficulty": 1, "category": "mobilier"},
    {"word": "lit", "difficulty": 1, "category": "mobilier"},
    {"word": "armoire", "difficulty": 1, "category": "mobilier"},
    {"word": "commode", "difficulty": 1, "category": "mobilier"},
    {"word": "bureau", "difficulty": 1, "category": "mobilier"},
    {"word": "étagère", "difficulty": 1, "category": "mobilier"},
    {"word": "fauteuil", "difficulty": 1, "category": "mobilier"},
    {"word": "tabouret", "difficulty": 1, "category": "mobilier"},
    {"word": "buffet", "difficulty": 1, "category": "mobilier"},
    {"word": "bibliothèque", "difficulty": 2, "category": "mobilier"},
    {"word": "coiffeuse", "difficulty": 2, "category": "mobilier"},
    {"word": "meuble", "difficulty": 1, "category": "mobilier"},
    {"word": "lampe", "difficulty": 1, "category": "mobilier"},
    {"word": "miroir", "difficulty": 1, "category": "mobilier"},
    {"word": "tapis", "difficulty": 1, "category": "mobilier"},
    {"word": "rideau", "difficulty": 1, "category": "mobilier"},
    {"word": "oreiller", "difficulty": 1, "category": "mobilier"},
    {"word": "couverture", "difficulty": 1, "category": "mobilier"},

    # Transport
    {"word": "voiture", "difficulty": 1, "category": "transport"},
    {"word": "bus", "difficulty": 1, "category": "transport"},
    {"word": "train", "difficulty": 1, "category": "transport"},
    {"word": "avion", "difficulty": 1, "category": "transport"},
    {"word": "vélo", "difficulty": 1, "category": "transport"},
    {"word": "moto", "difficulty": 1, "category": "transport"},
    {"word": "camion", "difficulty": 1, "category": "transport"},
    {"word": "taxi", "difficulty": 1, "category": "transport"},
    {"word": "métro", "difficulty": 1, "category": "transport"},
    {"word": "tramway", "difficulty": 1, "category": "transport"},
    {"word": "bateau", "difficulty": 1, "category": "transport"},
    {"word": "hélicoptère", "difficulty": 2, "category": "transport"},
    {"word": "fusée", "difficulty": 2, "category": "transport"},
    {"word": "sous-marin", "difficulty": 2, "category": "transport"},
    {"word": "montgolfière", "difficulty": 2, "category": "transport"},
    {"word": "téléphérique", "difficulty": 2, "category": "transport"},
    {"word": "trampoline", "difficulty": 2, "category": "transport"},
    {"word": "trottinette", "difficulty": 2, "category": "transport"},
    {"word": "roller", "difficulty": 1, "category": "transport"},
    {"word": "skateboard", "difficulty": 2, "category": "transport"},

    # Technologie
    {"word": "ordinateur", "difficulty": 1, "category": "technologie"},
    {"word": "téléphone", "difficulty": 1, "category": "technologie"},
    {"word": "tablette", "difficulty": 1, "category": "technologie"},
    {"word": "écran", "difficulty": 1, "category": "technologie"},
    {"word": "clavier", "difficulty": 1, "category": "technologie"},
    {"word": "souris", "difficulty": 1, "category": "technologie"},
    {"word": "imprimante", "difficulty": 1, "category": "technologie"},
    {"word": "scanner", "difficulty": 1, "category": "technologie"},
    {"word": "camera", "difficulty": 1, "category": "technologie"},
    {"word": "microphone", "difficulty": 2, "category": "technologie"},
    {"word": "enceinte", "difficulty": 1, "category": "technologie"},
    {"word": "casque", "difficulty": 1, "category": "technologie"},
    {"word": "console", "difficulty": 1, "category": "technologie"},
    {"word": "manette", "difficulty": 1, "category": "technologie"},
    {"word": "drone", "difficulty": 1, "category": "technologie"},
    {"word": "robot", "difficulty": 1, "category": "technologie"},
    {"word": "satellite", "difficulty": 2, "category": "technologie"},
    {"word": "télévision", "difficulty": 1, "category": "technologie"},
    {"word": "radio", "difficulty": 1, "category": "technologie"},
    {"word": "réfrigérateur", "difficulty": 2, "category": "technologie"},

    # Nature
    {"word": "arbre", "difficulty": 1, "category": "nature"},
    {"word": "fleur", "difficulty": 1, "category": "nature"},
    {"word": "herbe", "difficulty": 1, "category": "nature"},
    {"word": "buisson", "difficulty": 1, "category": "nature"},
    {"word": "feuille", "difficulty": 1, "category": "nature"},
    {"word": "branche", "difficulty": 1, "category": "nature"},
    {"word": "tronc", "difficulty": 1, "category": "nature"},
    {"word": "racine", "difficulty": 1, "category": "nature"},
    {"word": "graine", "difficulty": 1, "category": "nature"},
    {"word": "fruit", "difficulty": 1, "category": "nature"},
    {"word": "légume", "difficulty": 1, "category": "nature"},
    {"word": "champignon", "difficulty": 2, "category": "nature"},
    {"word": "mousse", "difficulty": 1, "category": "nature"},
    {"word": "algue", "difficulty": 1, "category": "nature"},
    {"word": "cactus", "difficulty": 1, "category": "nature"},
    {"word": "rose", "difficulty": 1, "category": "nature"},
    {"word": "tulipe", "difficulty": 1, "category": "nature"},
    {"word": "pissenlit", "difficulty": 2, "category": "nature"},
    {"word": "tournesol", "difficulty": 2, "category": "nature"},
    {"word": "coquelicot", "difficulty": 2, "category": "nature"},

    # Météo
    {"word": "soleil", "difficulty": 1, "category": "météo"},
    {"word": "lune", "difficulty": 1, "category": "météo"},
    {"word": "étoile", "difficulty": 1, "category": "météo"},
    {"word": "nuage", "difficulty": 1, "category": "météo"},
    {"word": "pluie", "difficulty": 1, "category": "météo"},
    {"word": "neige", "difficulty": 1, "category": "météo"},
    {"word": "vent", "difficulty": 1, "category": "météo"},
    {"word": "orage", "difficulty": 1, "category": "météo"},
    {"word": "tonnerre", "difficulty": 1, "category": "météo"},
    {"word": "éclair", "difficulty": 1, "category": "météo"},
    {"word": "arc-en-ciel", "difficulty": 2, "category": "météo"},
    {"word": "brouillard", "difficulty": 2, "category": "météo"},
    {"word": "grêle", "difficulty": 1, "category": "météo"},
    {"word": "tempête", "difficulty": 1, "category": "météo"},
    {"word": "ouragan", "difficulty": 2, "category": "météo"},
    {"word": "tornade", "difficulty": 2, "category": "météo"},
    {"word": "tsunami", "difficulty": 2, "category": "météo"},
    {"word": "avalanche", "difficulty": 2, "category": "météo"},
    {"word": "inondation", "difficulty": 2, "category": "météo"},
    {"word": "sécheresse", "difficulty": 2, "category": "météo"},

    # Animaux
    {"word": "chien", "difficulty": 1, "category": "animaux"},
    {"word": "chat", "difficulty": 1, "category": "animaux"},
    {"word": "oiseau", "difficulty": 1, "category": "animaux"},
    {"word": "poisson", "difficulty": 1, "category": "animaux"},
    {"word": "lapin", "difficulty": 1, "category": "animaux"},
    {"word": "hamster", "difficulty": 1, "category": "animaux"},
    {"word": "souris", "difficulty": 1, "category": "animaux"},
    {"word": "rat", "difficulty": 1, "category": "animaux"},
    {"word": "cochon", "difficulty": 1, "category": "animaux"},
    {"word": "vache", "difficulty": 1, "category": "animaux"},
    {"word": "mouton", "difficulty": 1, "category": "animaux"},
    {"word": "chèvre", "difficulty": 1, "category": "animaux"},
    {"word": "cheval", "difficulty": 1, "category": "animaux"},
    {"word": "âne", "difficulty": 1, "category": "animaux"},
    {"word": "poule", "difficulty": 1, "category": "animaux"},
    {"word": "coq", "difficulty": 1, "category": "animaux"},
    {"word": "canard", "difficulty": 1, "category": "animaux"},
    {"word": "oie", "difficulty": 1, "category": "animaux"},
    {"word": "dinde", "difficulty": 1, "category": "animaux"},
    {"word": "pigeon", "difficulty": 1, "category": "animaux"},

    # Nourriture
    {"word": "pain", "difficulty": 1, "category": "nourriture"},
    {"word": "fromage", "difficulty": 1, "category": "nourriture"},
    {"word": "jambon", "difficulty": 1, "category": "nourriture"},
    {"word": "saucisse", "difficulty": 1, "category": "nourriture"},
    {"word": "poulet", "difficulty": 1, "category": "nourriture"},
    {"word": "poisson", "difficulty": 1, "category": "nourriture"},
    {"word": "œuf", "difficulty": 1, "category": "nourriture"},
    {"word": "lait", "difficulty": 1, "category": "nourriture"},
    {"word": "beurre", "difficulty": 1, "category": "nourriture"},
    {"word": "yaourt", "difficulty": 1, "category": "nourriture"},
    {"word": "crème", "difficulty": 1, "category": "nourriture"},
    {"word": "sucre", "difficulty": 1, "category": "nourriture"},
    {"word": "sel", "difficulty": 1, "category": "nourriture"},
    {"word": "poivre", "difficulty": 1, "category": "nourriture"},
    {"word": "huile", "difficulty": 1, "category": "nourriture"},
    {"word": "vinaigre", "difficulty": 1, "category": "nourriture"},
    {"word": "moutarde", "difficulty": 1, "category": "nourriture"},
    {"word": "ketchup", "difficulty": 1, "category": "nourriture"},
    {"word": "mayonnaise", "difficulty": 2, "category": "nourriture"},
    {"word": "sauce", "difficulty": 1, "category": "nourriture"},

    # Boissons
    {"word": "eau", "difficulty": 1, "category": "boissons"},
    {"word": "café", "difficulty": 1, "category": "boissons"},
    {"word": "thé", "difficulty": 1, "category": "boissons"},
    {"word": "jus", "difficulty": 1, "category": "boissons"},
    {"word": "soda", "difficulty": 1, "category": "boissons"},
    {"word": "limonade", "difficulty": 1, "category": "boissons"},
    {"word": "bière", "difficulty": 1, "category": "boissons"},
    {"word": "vin", "difficulty": 1, "category": "boissons"},
    {"word": "champagne", "difficulty": 2, "category": "boissons"},
    {"word": "whisky", "difficulty": 1, "category": "boissons"},
    {"word": "vodka", "difficulty": 1, "category": "boissons"},
    {"word": "rhum", "difficulty": 1, "category": "boissons"},
    {"word": "cidre", "difficulty": 1, "category": "boissons"},
    {"word": "lait", "difficulty": 1, "category": "boissons"},
    {"word": "chocolat", "difficulty": 1, "category": "boissons"},
    {"word": "smoothie", "difficulty": 2, "category": "boissons"},
    {"word": "milkshake", "difficulty": 2, "category": "boissons"},
    {"word": "cocktail", "difficulty": 2, "category": "boissons"},
    {"word": "sirop", "difficulty": 1, "category": "boissons"},
    {"word": "infusion", "difficulty": 2, "category": "boissons"},

    # Sports
    {"word": "football", "difficulty": 1, "category": "sports"},
    {"word": "basketball", "difficulty": 1, "category": "sports"},
    {"word": "tennis", "difficulty": 1, "category": "sports"},
    {"word": "rugby", "difficulty": 1, "category": "sports"},
    {"word": "volley", "difficulty": 1, "category": "sports"},
    {"word": "handball", "difficulty": 1, "category": "sports"},
    {"word": "natation", "difficulty": 1, "category": "sports"},
    {"word": "course", "difficulty": 1, "category": "sports"},
    {"word": "saut", "difficulty": 1, "category": "sports"},
    {"word": "lancer", "difficulty": 1, "category": "sports"},
    {"word": "boxe", "difficulty": 1, "category": "sports"},
    {"word": "judo", "difficulty": 1, "category": "sports"},
    {"word": "karaté", "difficulty": 1, "category": "sports"},
    {"word": "escrime", "difficulty": 2, "category": "sports"},
    {"word": "golf", "difficulty": 1, "category": "sports"},
    {"word": "ski", "difficulty": 1, "category": "sports"},
    {"word": "patinage", "difficulty": 2, "category": "sports"},
    {"word": "cyclisme", "difficulty": 2, "category": "sports"},
    {"word": "marche", "difficulty": 1, "category": "sports"},
    {"word": "danse", "difficulty": 1, "category": "sports"},

    # Instruments de musique
    {"word": "piano", "difficulty": 1, "category": "musique"},
    {"word": "guitare", "difficulty": 1, "category": "musique"},
    {"word": "violon", "difficulty": 1, "category": "musique"},
    {"word": "flûte", "difficulty": 1, "category": "musique"},
    {"word": "trompette", "difficulty": 1, "category": "musique"},
    {"word": "saxophone", "difficulty": 2, "category": "musique"},
    {"word": "batterie", "difficulty": 1, "category": "musique"},
    {"word": "tambour", "difficulty": 1, "category": "musique"},
    {"word": "accordéon", "difficulty": 2, "category": "musique"},
    {"word": "harpe", "difficulty": 1, "category": "musique"},
    {"word": "clarinette", "difficulty": 2, "category": "musique"},
    {"word": "trombone", "difficulty": 2, "category": "musique"},
    {"word": "tuba", "difficulty": 1, "category": "musique"},
    {"word": "triangle", "difficulty": 1, "category": "musique"},
    {"word": "cymbale", "difficulty": 1, "category": "musique"},
    {"word": "maracas", "difficulty": 1, "category": "musique"},
    {"word": "castagnettes", "difficulty": 2, "category": "musique"},
    {"word": "tambourin", "difficulty": 2, "category": "musique"},
    {"word": "xylophone", "difficulty": 2, "category": "musique"},
    {"word": "harmonica", "difficulty": 2, "category": "musique"}
]

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


def init_db():
    """Initialise la base de données avec les mots par défaut."""
    # Vérifier si la base de données est vide
    if Word.query.count() == 0:
        # Charger les mots depuis le fichier JSON
        json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'words.json')
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                words_data = data['words']
                
                # Ajouter les mots à la base de données
                for word_data in words_data:
                    # Vérifier si le mot existe déjà
                    existing_word = Word.query.filter_by(word=word_data['word']).first()
                    if not existing_word:
                        word = Word(**word_data)
                        db.session.add(word)
                
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    # Si un mot existe déjà, on continue avec les autres
                    pass
        except FileNotFoundError:
            print(f"Erreur : Le fichier {json_path} n'a pas été trouvé.")
        except json.JSONDecodeError:
            print(f"Erreur : Le fichier {json_path} n'est pas un JSON valide.")
        except Exception as e:
            print(f"Erreur lors de l'initialisation de la base de données : {str(e)}")

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/configurer_partie', methods=['GET', 'POST'])
def configurer_partie():
    print("je viens ici")
    print(session)
    if request.method == 'POST':
        print("et la")
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
            
            #print(session, 'au revoir')# Si le nombre de mots total a changé, ajuster les mots des joueurs
            # if 'nb_mots_total' in session and session['nb_mots_total'] != nb_mots_total:
            #     print(session, 'QUOIII')
            #     game_session = session.get('game_session')
            #     if game_session:
            #         #< nb_mots_joueurs fait sauter la session
            #         # Calculer la nouvelle distribution des mots
            #         new_distribution = calculate_words_distribution(nb_joueurs, nb_mots_total)
                    
            #         # Récupérer tous les joueurs de la session
            #         players = Player.query.filter_by(game_session=game_session).all()
                    
            #         # Ajuster les mots pour chaque joueur
            #         for i, player in enumerate(players):

            #             if i < len(new_distribution):
            #                 current_words = player.words.all()
            #                 print(player.words.all())
            #                 if len(current_words) > new_distribution[i]:
            #                     # Garder seulement le nombre requis de mots
            #                     player.words = current_words[:new_distribution[i]]
            #                     db.session.commit()
                                
            #                     # Mettre à jour le compteur dans la session
            #                     if 'mots_joueurs' not in session:
            #                         session['mots_joueurs'] = [0] * nb_joueurs
            #                     session['mots_joueurs'][i] = new_distribution[i]
            #                     session.modified = True
            
            # Stocker en session
            session['nb_equipes'] = nb_equipes
            session['nb_joueurs'] = nb_joueurs
            session['choix_mots'] = choix_mots
            session['choix_equipe'] = choix_equipe
            session['nb_mots_total'] = nb_mots_total
            session['duree_manche'] = duree_manche
            session['mot_reserve'] = mot_reserve
            
            # Redirection vers la page de saisie des noms
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

    # Ajuster la taille de mots_joueurs en fonction du nombre de joueurs actuel
    current_nb_joueurs = session['nb_joueurs']
    if 'mots_joueurs' not in session:
        session['mots_joueurs'] = [0] * current_nb_joueurs
    elif len(session['mots_joueurs']) != current_nb_joueurs:
        # Si le nombre de joueurs a changé, ajuster la liste
        old_mots = session['mots_joueurs']
        session['mots_joueurs'] = [0] * current_nb_joueurs
        # Copier les anciennes valeurs si possible
        for i in range(min(len(old_mots), current_nb_joueurs)):
            session['mots_joueurs'][i] = old_mots[i]
    session.modified = True

    # Initialiser le stockage temporaire si besoin
    if 'pending_words' not in session:
        session['pending_words'] = {}
        session.modified = True

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
            if len(nom) > 20:
                flash('Les noms ne doivent pas dépasser 20 caractères', 'error')
                return render_template('choix_mots_aleatoire.html'), 400
            nom = nom.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            noms_joueurs.append(nom)
        # Vérifier les doublons
        if len(set(noms_joueurs)) != len(noms_joueurs):
            flash('Des joueurs ont le même nom. Veuillez modifier les pseudonymes identiques.', 'error')
            return render_template('choix_mots_aleatoire.html'), 400
        # Stocker les noms en session
        session['noms_joueurs'] = noms_joueurs
        session.modified = True

        # Transférer les mots temporaires si un nom réel est donné
        game_session = session.get('game_session')
        if not game_session:
            game_session = str(datetime.utcnow().timestamp())
            session['game_session'] = game_session
        nb_joueurs = session['nb_joueurs']
        nb_mots_total = session['nb_mots_total']
        mots_distribution = calculate_words_distribution(nb_joueurs, nb_mots_total)
        for i, nom in enumerate(noms_joueurs):
            nom_defaut = f"Joueur {i + 1}"
            if nom and nom != nom_defaut:
                pending = session['pending_words'].pop(str(i), None)
                if pending:
                    player = Player.query.filter_by(name=nom, game_session=game_session).first()
                    if not player:
                        player = Player(name=nom, game_session=game_session)
                        db.session.add(player)
                        db.session.commit()
                    mots_requis = mots_distribution[i]
                    new_mots = []
                    for mot in pending:
                        word = Word.query.filter_by(word=mot).first()
                        if not word:
                            word = Word(word=mot, is_custom=True)
                            db.session.add(word)
                            db.session.commit()
                        new_mots.append(word)
                    player.words = new_mots[:mots_requis]
                    db.session.commit()
                    if 'mots_joueurs' not in session:
                        session['mots_joueurs'] = [0] * nb_joueurs
                    session['mots_joueurs'][i] = len(new_mots[:mots_requis])
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

    # Si choix_mots est "aleatoire", pré-remplir les mots pour chaque joueur
    if session.get('choix_mots') == 'aleatoire':
        game_session = session.get('game_session')
        if not game_session:
            game_session = str(datetime.utcnow().timestamp())
            session['game_session'] = game_session
            session.modified = True

        # Récupérer tous les mots déjà utilisés
        used_words = set()
        players = Player.query.filter_by(game_session=game_session).all()
        for player in players:
            for word in player.words:
                used_words.add(word.word)

        # Pour chaque joueur, générer ses mots
        mots_distribution = calculate_words_distribution(session['nb_joueurs'], session['nb_mots_total'])
        for i in range(session['nb_joueurs']):
            mots_requis = mots_distribution[i]
            new_mots = []
            attempts = 0
            max_attempts = mots_requis * 2  # Limite de tentatives pour éviter une boucle infinie

            while len(new_mots) < mots_requis and attempts < max_attempts:
                word = Word.query.filter(
                    Word.is_custom == False,
                    ~Word.word.in_(used_words)
                ).order_by(db.func.random()).first()

                if word and word.word not in new_mots:
                    new_mots.append(word.word)
                    used_words.add(word.word)
                attempts += 1

            if new_mots:
                session['pending_words'][str(i)] = new_mots
                if 'mots_joueurs' not in session:
                    session['mots_joueurs'] = [0] * session['nb_joueurs']
                session['mots_joueurs'][i] = len(new_mots)
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
    nom_defaut = f"Joueur {player_index + 1}"
    
    # Calculer la répartition des mots
    nb_joueurs = session.get('nb_joueurs', 0)
    nb_mots_total = session.get('nb_mots_total', 50)
    mots_distribution = calculate_words_distribution(nb_joueurs, nb_mots_total)
    mots_requis = mots_distribution[player_index]

    # Initialiser le stockage temporaire si besoin
    if 'pending_words' not in session:
        session['pending_words'] = {}
        session.modified = True

    # Si le nom est vide ou par défaut, on ne crée pas de joueur en base
    if not player_name or player_name == nom_defaut:
        if request.method == 'POST':
            # Stocker les mots temporairement
            new_mots = []
            for i in range(mots_requis):
                mot = request.form.get(f'mot_{i}', '').strip()
                if mot:
                    if len(mot) > 50:
                        flash('Les mots ne doivent pas dépasser 50 caractères', 'error')
                        return render_template('mots_joueur.html', 
                                               player_index=player_index,
                                               player_name=player_name,
                                               mots=[{'word': m} for m in new_mots],
                                               nb_mots_total=mots_requis), 400
                    mot = mot.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    new_mots.append(mot)
            session['pending_words'][str(player_index)] = new_mots
            if 'mots_joueurs' not in session:
                session['mots_joueurs'] = [0] * session['nb_joueurs']
            print(session)
            print(player_index, len(new_mots), new_mots, str(player_index), session['mots_joueurs'])
            # 4 1 ["on"] 4 
            session['mots_joueurs'][player_index] = len(new_mots)
            session.modified = True
            flash(f"Les mots ont été enregistrés temporairement pour {nom_defaut}", 'success')
            return redirect(url_for('main.choix_mots_aleatoire'))
        # Affichage GET : pré-remplir avec les mots temporaires si présents
        mots = [{'word': m} for m in session['pending_words'].get(str(player_index), [])]
        return render_template('mots_joueur.html', 
                              player_index=player_index,
                              player_name=player_name,
                              mots=mots,
                              nb_mots_total=mots_requis)

    # Sinon, nom réel : on transfère les mots temporaires s'ils existent
    game_session = session.get('game_session')
    if not game_session:
        game_session = str(datetime.utcnow().timestamp())
        session['game_session'] = game_session
    player = Player.query.filter_by(name=player_name, game_session=game_session).first()
    if not player:
        player = Player(name=player_name, game_session=game_session)
        db.session.add(player)
        db.session.commit()
        # Transfert des mots temporaires si présents
        pending = session['pending_words'].pop(str(player_index), None)
        if pending:
            new_mots = []
            for mot in pending:
                word = Word.query.filter_by(word=mot).first()
                if not word:
                    word = Word(word=mot, is_custom=True)
                    db.session.add(word)
                    db.session.commit()
                new_mots.append(word)
            player.words = new_mots[:mots_requis]
            db.session.commit()
            if 'mots_joueurs' not in session:
                session['mots_joueurs'] = [0] * session['nb_joueurs']
            session['mots_joueurs'][player_index] = len(new_mots[:mots_requis])
            session.modified = True

    if request.method == 'POST':
        # Récupérer et nettoyer les mots
        new_mots = []
        for i in range(mots_requis):
            mot = request.form.get(f'mot_{i}', '').strip()
            if mot:
                if len(mot) > 50:
                    flash('Les mots ne doivent pas dépasser 50 caractères', 'error')
                    return render_template('mots_joueur.html', 
                                           player_index=player_index,
                                           player_name=player_name,
                                           mots=player.words.all(),
                                           nb_mots_total=mots_requis), 400
                mot = mot.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                word = Word.query.filter_by(word=mot).first()
                if not word:
                    word = Word(word=mot, is_custom=True)
                    db.session.add(word)
                    db.session.commit()
                new_mots.append(word)
        new_mots = new_mots[:mots_requis]
        player.words = new_mots
        db.session.commit()
        if 'mots_joueurs' not in session:
            session['mots_joueurs'] = [0] * session['nb_joueurs']
        session['mots_joueurs'][player_index] = len(new_mots)
        session.modified = True
        flash(f'Les mots de {player_name} ont été enregistrés avec succès', 'success')
        return redirect(url_for('main.choix_mots_aleatoire'))

    # Ajuster le nombre de mots stockés si nécessaire
    current_words = player.words.all()
    if len(current_words) > mots_requis:
        player.words = current_words[:mots_requis]
        db.session.commit()
        if 'mots_joueurs' not in session:
            session['mots_joueurs'] = [0] * session['nb_joueurs']
        session['mots_joueurs'][player_index] = mots_requis
        session.modified = True
    return render_template('mots_joueur.html', 
                         player_index=player_index,
                         player_name=player_name,
                         mots=player.words.all(),
                         nb_mots_total=mots_requis)

@bp.route('/generate_random_word', methods=['POST'])
def generate_random_word():
    """Génère un mot aléatoire depuis la base de données, en évitant les doublons."""
    # S'assurer que la base de données est initialisée
    init_db()
    
    # Récupérer la session de jeu
    game_session = session.get('game_session')
    if not game_session:
        # Initialiser la session de jeu si elle n'existe pas
        game_session = str(datetime.utcnow().timestamp())
        session['game_session'] = game_session
        session.modified = True
    
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
        # Si aucun mot n'est disponible, retourner une erreur
        return {'error': 'Aucun mot disponible'}, 404

@bp.route('/reset_game', methods=['POST'])
def reset_game():
    try:
        # Récupérer la session de jeu actuelle
        game_session = session.get('game_session')
        
        if game_session:
            # Supprimer tous les joueurs et leurs mots associés de la base de données
            players = Player.query.filter_by(game_session=game_session).all()
            for player in players:
                # Supprimer les mots personnalisés créés par ce joueur
                for word in player.words:
                    if word.is_custom:
                        db.session.delete(word)
                # Supprimer le joueur
                db.session.delete(player)
            
            # Commit les changements dans la base de données
            db.session.commit()
        
        # Nettoyer toutes les variables de session
        session.clear()
        
        # Réinitialiser les paramètres par défaut
        session['nb_equipes'] = 2
        session['nb_joueurs'] = 4
        session['choix_mots'] = 'aleatoire'
        session['choix_equipe'] = 'personnalise'
        session['nb_mots_total'] = 50
        session['duree_manche'] = 30
        session['mot_reserve'] = 'oui'
        
        return {'status': 'success'}, 200
        
    except Exception as e:
        db.session.rollback()
        return {'status': 'error', 'message': str(e)}, 500

@bp.route('/delete_player_words/<int:player_index>', methods=['POST'])
def delete_player_words(player_index):
    try:
        # Vérifier que l'index est valide
        if not isinstance(player_index, int) or player_index < 0 or player_index >= session.get('nb_joueurs', 0):
            return {'status': 'error', 'message': 'Index de joueur invalide'}, 400
        
        # Récupérer le nom du joueur
        player_name = session.get('noms_joueurs', [''] * session['nb_joueurs'])[player_index]
        
        # Récupérer le joueur dans la base de données
        game_session = session.get('game_session')
        if game_session:
            player = Player.query.filter_by(name=player_name, game_session=game_session).first()
            if player:
                # Supprimer les mots personnalisés créés par ce joueur
                for word in player.words:
                    if word.is_custom:
                        db.session.delete(word)
                # Vider la liste des mots du joueur
                player.words = []
                db.session.commit()
                
                # Mettre à jour le compteur dans la session
                if 'mots_joueurs' in session:
                    session['mots_joueurs'][player_index] = 0
                    session.modified = True
        
        return {'status': 'success'}, 200
        
    except Exception as e:
        db.session.rollback()
        return {'status': 'error', 'message': str(e)}, 500

@bp.route('/save_advanced_settings', methods=['POST'])
def save_advanced_settings():
    try:
        data = request.get_json()
        
        # Récupérer les paramètres
        choix_equipe = data.get('choix_equipe')
        nb_mots_total = int(data.get('nb_mots_total'))
        duree_manche = int(data.get('duree_manche'))
        mot_reserve = data.get('mot_reserve')
        
        # Validation des paramètres
        if choix_equipe not in ['aleatoire', 'personnalise']:
            raise BadRequest("Choix d'équipe invalide")
        if not (20 <= nb_mots_total <= 80):
            raise BadRequest("Le nombre de mots total doit être entre 20 et 80")
        if not (20 <= duree_manche <= 60):
            raise BadRequest("La durée de la manche doit être entre 20 et 60 secondes")
        if mot_reserve not in ['oui', 'non']:
            raise BadRequest("Choix de mot en réserve invalide")
        
        # Sauvegarder en session
        session['choix_equipe'] = choix_equipe
        session['nb_mots_total'] = nb_mots_total
        session['duree_manche'] = duree_manche
        session['mot_reserve'] = mot_reserve
        session.modified = True
        
        return {'status': 'success'}, 200
        
    except (ValueError, BadRequest) as e:
        return {'status': 'error', 'message': str(e)}, 400
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

@bp.route('/constituer_equipes', methods=['GET'])
def constituer_equipes():
    # Vérifier que les paramètres nécessaires sont en session
    if not all(key in session for key in ['nb_equipes', 'nb_joueurs', 'noms_joueurs']):
        flash('Veuillez d\'abord configurer la partie', 'error')
        return redirect(url_for('main.configurer_partie'))
    
    return render_template('constituer_equipes.html')

@bp.route('/start_game', methods=['POST'])
def start_game():
    try:
        data = request.get_json()
        teams = data.get('teams', {})
        
        # Vérifier que toutes les équipes ont le bon nombre de joueurs
        nb_equipes = session.get('nb_equipes', 2)
        nb_joueurs = session.get('nb_joueurs', 4)
        joueurs_par_equipe = nb_joueurs // nb_equipes
        
        if len(teams) != nb_equipes:
            return jsonify({'status': 'error', 'message': 'Nombre d\'équipes incorrect'})
        
        for equipe in teams.values():
            if len(equipe) != joueurs_par_equipe:
                return jsonify({'status': 'error', 'message': 'Nombre de joueurs incorrect dans une équipe'})
        
        # Sauvegarder les équipes en session
        session['equipes'] = teams
        
        # Rediriger vers la page de jeu
        return jsonify({
            'status': 'success',
            'redirect': url_for('main.jouer_partie')
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}) 