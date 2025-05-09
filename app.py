from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'votre_cle_secrete'  # Nécessaire pour les sessions
db = SQLAlchemy(app)

# Modèle de données
class Mot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenu = db.Column(db.String(100), nullable=False)
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)

@app.route("/")
def accueil():
    return render_template("index.html")

@app.route("/reinitialiser_db")
def reinitialiser_db():
    # Supprimer toutes les tables
    db.drop_all()
    # Recréer les tables
    db.create_all()
    # Vider la session
    session.clear()
    return redirect(url_for('accueil'))

@app.route("/regles")
def regles():
    return render_template("regles.html")

@app.route("/configurer_partie", methods=["GET", "POST"])
def configurer_partie():
    if request.method == "POST":
        try:
            nb_equipes = int(request.form.get("nb_equipes", 2))
            mots_par_joueur = int(request.form.get("mots_par_joueur", 5))
            
            # Validation des entrées
            if not (2 <= nb_equipes <= 4):
                flash("Le nombre d'équipes doit être entre 2 et 4", "error")
                return redirect(url_for('configurer_partie'))
            
            if not (3 <= mots_par_joueur <= 10):
                flash("Le nombre de mots par joueur doit être entre 3 et 10", "error")
                return redirect(url_for('configurer_partie'))
            
            # Stockage des paramètres en session
            session['config_partie'] = {
                'nb_equipes': nb_equipes,
                'mots_par_joueur': mots_par_joueur
            }
            
            # Pour le moment, on redirige vers l'accueil
            # TODO: Implémenter la logique de création d'équipes
            return redirect(url_for('accueil'))
            
        except ValueError:
            flash("Veuillez entrer des nombres valides", "error")
            return redirect(url_for('configurer_partie'))
    
    return render_template("configurer_partie.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Crée la base si elle n'existe pas
    app.run(debug=True)