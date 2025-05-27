from flask import Flask
from config import config
from app.models import db
import os

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialisation de la base de données
    db.init_app(app)
    
    # Création des tables si elles n'existent pas
    with app.app_context():
        # Vérifier si la base de données existe
        db_exists = os.path.exists(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
        
        # Créer les tables
        db.create_all()
        
        # Si la base de données existait déjà, vérifier si la colonne is_custom existe
        if db_exists:
            try:
                # Tenter d'accéder à la colonne is_custom
                db.session.execute('SELECT is_custom FROM words LIMIT 1')
            except Exception:
                # Si la colonne n'existe pas, l'ajouter
                db.session.execute('ALTER TABLE words ADD COLUMN is_custom BOOLEAN DEFAULT FALSE')
                db.session.commit()

    # Enregistrement des blueprints
    from app.routes import main
    app.register_blueprint(main.bp)

    return app 