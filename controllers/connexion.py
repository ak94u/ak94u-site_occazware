from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from models.db import User, db
from email_validator import validate_email, EmailNotValidError

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/connexion', methods=['GET', 'POST'])
def connexion():
    if request.method == 'POST':
        email_saisi = request.form.get('email')
        password_saisi = request.form.get('password')

        # 1. Chercher l'utilisateur dans la base de données via son email
        user = User.query.filter_by(email=email_saisi).first()

        # 2. Vérifier si l'utilisateur existe et si le mot de passe correspond au hash robuste (Cahier des charges)
        if user and check_password_hash(user.password_hash, password_saisi):
            # On stocke les informations importantes dans la session Flask
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_role'] = user.role

            flash('Connexion réussie !', 'success')
            
            # Redirection selon le rôle
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('magasin.index'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')

    return render_template('connexion.html')

@auth_blueprint.route('/deconnexion')
def deconnexion():
    # On vide la session pour déconnecter l'utilisateur
    session.clear()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('magasin.index'))

@auth_blueprint.route('/inscription', methods=['POST'])
def inscription():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    # 🟢 VERIFICATION SANS ENVOI : L'adresse email est-elle réelle ?
    try:
        # check_deliverability=True va interroger les serveurs (DNS/SMTP) pour vérifier l'existence réelle
        email_valide = validate_email(email, check_deliverability=True)
        
        # On récupère l'email normalisé (ex: convertit les majuscules oubliées en minuscules)
        email = email_valide.normalized
        
    except EmailNotValidError as e:
        # Si le serveur n'existe pas ou si l'adresse n'est pas réelle, on lève une erreur
        flash(f"L'adresse email est invalide ou inexistante.", "error")
        return redirect(url_for('auth.connexion', mode='inscription'))

    # 1. Vérifier si l'adresse email existe déjà en Base de Données
    user_existe = User.query.filter_by(email=email).first()
    if user_existe:
        flash("Cette adresse email est déjà utilisée.", "error")
        return redirect(url_for('auth.connexion', mode='inscription'))

    # 2. Hacher le mot de passe de manière fiable
    password_safe = generate_password_hash(password)

    # 3. Créer le nouvel utilisateur
    nouvel_utilisateur = User(
        username=username,
        email=email,
        password_hash=password_safe,
        role='client'
    )

    try:
        db.session.add(nouvel_utilisateur)
        db.session.commit()
        flash("Compte créé avec succès ! Vous pouvez maintenant vous connecter.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Une erreur est survenue lors de l'inscription.", "error")

    return redirect(url_for('auth.connexion'))