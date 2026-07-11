from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.db import User, db, mail
from werkzeug.security import generate_password_hash
from flask_mail import Message
# On importe l'objet 'mail' depuis ton fichier app.py


auth_mot_de_passe = Blueprint('auth_mot_de_passe', __name__)

@auth_mot_de_passe.route('/mot_de_passe', methods=['GET', 'POST'])
def mot_de_passe():
    if request.method == 'POST':
        email_saisi = request.form.get('email')
        user = User.query.filter_by(email=email_saisi).first()

        if user:
            # 1. On génère le lien absolu qui sera envoyé dans le mail
            lien_reinitialisation = url_for(
                'auth_mot_de_passe.reinitialiser_page', 
                email_user=email_saisi, 
                _external=True  # _external=True force Flask à mettre http://127.0.0.1:5000 devant l'URL
            )

            # 2. On prépare le contenu HTML du mail avec le beau bouton bleu
            contenu_html = f"""
            <div style="font-family: sans-serif; max-width: 500px; margin: 0 auto; padding: 20px; background-color: #18181b; color: #ffffff; border-radius: 12px;">
                <h2 style="color: #3b82f6; text-align: center;">Occaz' Gaming 🎮</h2>
                <p>Bonjour,</p>
                <p>Nous avons reçu une demande de réinitialisation de mot de passe pour votre compte.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{lien_reinitialisation}" style="background-color: #2563eb; color: #ffffff; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 8px; display: inline-block;">
                        🔄 Réinitialiser mon mot de passe
                    </a>
                </div>
                <p style="font-size: 11px; color: #a1a1aa; text-align: center;">
                    Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer ce mail.
                </p>
            </div>
            """

            # 3. Envoi du vrai mail au client
            try:
                msg = Message(
                    subject="Réinitialisation de votre mot de passe - Occaz' Gaming",
                    recipients=[email_saisi],
                    html=contenu_html
                )
                
                with mail.connect() as conn:
                    conn.send(msg)

                # Une fois envoyé, on laisse le client sur la page avec un message de succès
                flash('Un lien de réinitialisation a été envoyé directement sur votre boîte mail !', 'success')
                return redirect(url_for('auth.connexion'))
                
            except Exception as e:
                flash("Erreur technique lors de l'envoi du mail.", "error")
                print(f"Erreur lors de l'envoi du mail : {e}")  # Pour le débogage côté serveur
        else:
            flash('Aucun utilisateur trouvé avec cette adresse email.', 'error')

    return render_template('auth_mot_de_passe.html')

# Cette route reste identique : c'est celle sur laquelle le client atterrit en cliquant dans son mail !
@auth_mot_de_passe.route('/reinitialiser/<string:email_user>', methods=['GET', 'POST'])
def reinitialiser_page(email_user):
    user = User.query.filter_by(email=email_user).first_or_404()

    if request.method == 'POST':
        nouveau_mdp = request.form.get('password')
        confirm_mdp = request.form.get('password_confirm')
        if nouveau_mdp and nouveau_mdp == confirm_mdp:
            user.password_hash = generate_password_hash(nouveau_mdp)
            db.session.commit()
            flash('Votre mot de passe a été modifié avec succès ! Connectez-vous.', 'success')
            return redirect(url_for('auth.connexion'))
        else: 
            flash('Les mots de passe ne correspondent pas.', 'error')
            return redirect(url_for('auth.connexion'))

    return render_template('nouveau_mdp.html', email=email_user)