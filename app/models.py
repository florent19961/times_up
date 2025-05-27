from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Table d'association entre les joueurs et leurs mots
player_words = db.Table('player_words',
    db.Column('player_id', db.Integer, db.ForeignKey('players.id'), primary_key=True),
    db.Column('word_id', db.Integer, db.ForeignKey('words.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.now)
)

class Player(db.Model):
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    game_session = db.Column(db.String(50), nullable=False)  # Pour identifier la session de jeu
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relation avec les mots
    words = db.relationship('Word', secondary=player_words, lazy='dynamic',
                          backref=db.backref('players', lazy=True))

    def __repr__(self):
        return f'<Player {self.name}>'

class Word(db.Model):
    __tablename__ = 'words'
    
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50), nullable=False, unique=True)
    difficulty = db.Column(db.Integer, default=1)  # 1-5 pour la difficulté du mot
    category = db.Column(db.String(50), nullable=True)  # Catégorie du mot (ex: animaux, nourriture, etc.)
    is_custom = db.Column(db.Boolean, default=False)  # Indique si c'est un mot personnalisé
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Word {self.word}>' 