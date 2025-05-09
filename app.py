from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'votre_cle_secrete'  # Nécessaire pour les sessions
db = SQLAlchemy(app)

# Modèle de données
class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), nullable=False)
    mots = db.relationship('Mot', backref='utilisateur', lazy=True)

class Mot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenu = db.Column(db.String(100), nullable=False)
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), nullable=False)

@app.route("/")
def accueil():
    utilisateur_id = session.get('utilisateur_id')
    utilisateur = None
    if utilisateur_id:
        utilisateur = Utilisateur.query.get(utilisateur_id)
    return render_template("index.html", utilisateur=utilisateur)

# Route
@app.route("/pseudo", methods=["GET", "POST"])
def pseudo():
    if request.method == "POST":
        nom = request.form["nom"]
        # Vérifier si l'utilisateur existe déjà
        utilisateur_existant = Utilisateur.query.filter_by(nom=nom).first()
        
        if utilisateur_existant:
            # L'utilisateur existe déjà
            return render_template("pseudo.html", 
                                erreur="Ce nom d'utilisateur existe déjà",
                                utilisateur_existant=utilisateur_existant)
        else:
            # Créer un nouvel utilisateur
            nouvel_utilisateur = Utilisateur(nom=nom)
            db.session.add(nouvel_utilisateur)
            db.session.commit()
            session['utilisateur_id'] = nouvel_utilisateur.id
            return render_template("pseudo.html", nom=nom, utilisateur=nouvel_utilisateur)
    
    return render_template("pseudo.html")

@app.route("/connexion/<int:utilisateur_id>")
def connexion(utilisateur_id):
    session['utilisateur_id'] = utilisateur_id
    return redirect(url_for('accueil'))

@app.route("/liste")
def liste():
    utilisateurs = Utilisateur.query.all()  # Récupère tous les utilisateurs
    return render_template("liste.html", utilisateurs=utilisateurs)

@app.route("/ajout_mot", methods=["GET", "POST"])
def ajout_mot():
    utilisateur_id = session.get('utilisateur_id')  # Récupère l'ID depuis la session
    if not utilisateur_id:
        return redirect(url_for('pseudo'))
    
    utilisateur = Utilisateur.query.get(utilisateur_id)
    if not utilisateur:
        return redirect(url_for('pseudo'))

    if request.method == "POST":
        contenu = request.form["mot"]
        nouveau_mot = Mot(contenu=contenu, utilisateur_id=utilisateur_id)
        db.session.add(nouveau_mot)
        db.session.commit()
        return redirect(url_for('ajout_mot'))
    
    mots = Mot.query.filter_by(utilisateur_id=utilisateur_id).order_by(Mot.date_ajout.desc()).all()
    return render_template("ajout_mot.html", utilisateur=utilisateur, mots=mots)

@app.route("/deconnexion")
def deconnexion():
    session.pop('utilisateur_id', None)  # Supprime l'ID de l'utilisateur de la session
    return redirect(url_for('accueil'))

@app.route("/modifier_compte", methods=["GET", "POST"])
def modifier_compte():
    utilisateur_id = session.get('utilisateur_id')
    if not utilisateur_id:
        return redirect(url_for('pseudo'))
    
    utilisateur = Utilisateur.query.get(utilisateur_id)
    if not utilisateur:
        return redirect(url_for('pseudo'))

    if request.method == "POST":
        nouveau_nom = request.form["nom"]
        utilisateur.nom = nouveau_nom
        db.session.commit()
        return redirect(url_for('accueil'))
    
    return render_template("modifier_compte.html", utilisateur=utilisateur)

@app.route("/liste_utilisateurs")
def liste_utilisateurs():
    utilisateurs = Utilisateur.query.all()
    return render_template("liste_utilisateurs.html", utilisateurs=utilisateurs)

@app.route("/reinitialiser_db")
def reinitialiser_db():
    # Supprimer toutes les tables
    db.drop_all()
    # Recréer les tables
    db.create_all()
    # Vider la session
    session.clear()
    return redirect(url_for('accueil'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Crée la base si elle n'existe pas
    app.run(debug=True)