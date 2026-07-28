from flask import Blueprint, session, redirect, url_for, flash, abort, render_template, request, send_from_directory
from models.db import db, Product, CartItem, Order, OrderItem, mail
from flask_mail import Message
import stripe
from dotenv import load_dotenv
import os
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

load_dotenv()

panier_blueprint = Blueprint('panier', __name__)

# Configuration Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


# =========================================================
# 1. GESTION DU PANIER
# =========================================================

@panier_blueprint.route('/ajouter-au-panier/<int:product_id>', methods=['POST'])
def ajouter_au_panier(product_id):
    if 'user_id' not in session:
        flash("Vous devez être connecté pour ajouter un article au panier.", "error")
        return redirect(url_for('auth.connexion'))

    user_id = session['user_id']
    produit = Product.query.get_or_404(product_id)
    
    if produit.stock <= 0:
        flash("Désolé, ce produit est épuisé !", "error")
        return redirect(url_for('magasin.index'))

    item_panier = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()

    if item_panier:
        if item_panier.quantity < produit.stock:
            item_panier.quantity += 1
            db.session.commit()
            flash(f"Quantité augmentée pour {produit.name}.", "success")
        else:
            flash("Impossible d'ajouter plus d'exemplaires (limite du stock atteinte).", "error")
    else:
        nouvel_item = CartItem(
            user_id=user_id,
            product_id=product_id,
            quantity=1
        )
        db.session.add(nouvel_item)
        db.session.commit()
        flash(f"'{produit.name}' a été ajouté à votre panier !", "success")

    return redirect(url_for('magasin.index'))


@panier_blueprint.route('/panier')
def voir_panier():
    if 'user_id' not in session:
        flash("Veuillez vous connecter pour accéder à votre panier.", "error")
        return redirect(url_for('auth.connexion'))

    user_id = session['user_id']
    items = CartItem.query.filter_by(user_id=user_id).all()

    total_global = 0
    for item in items:
        item.total_ligne = item.quantity * item.product.price
        total_global += item.total_ligne

    return render_template('panier.html', items=items, total_global=total_global)


@panier_blueprint.route('/panier/modifier/<int:item_id>', methods=['POST'])
def modifier_quantite(item_id):
    if 'user_id' not in session:
        abort(403)
        
    action = request.form.get('action')
    item = CartItem.query.get_or_404(item_id)
    
    if item.user_id != session['user_id']:
        abort(403)

    if action == 'augmenter':
        if item.quantity < item.product.stock:
            item.quantity += 1
        else:
            flash("Limite du stock atteinte pour cet article.", "error")
    elif action == 'diminuer':
        item.quantity -= 1
        if item.quantity <= 0:
            db.session.delete(item)
    elif action == 'supprimer':
        db.session.delete(item)
        flash(f"'{item.product.name}' a été retiré de votre panier avec succès.", "success")

    db.session.commit()
    return redirect(url_for('panier.voir_panier'))


# =========================================================
# 2. TUNNEL DE PAIEMENT STRIPE
# =========================================================

@panier_blueprint.route('/panier/checkout', methods=['GET', 'POST'])
def page_paiement():
    if 'user_id' not in session:
        flash("Veuillez vous connecter pour procéder au paiement.", "error")
        return redirect(url_for('auth.connexion'))
    
    user_id = session['user_id']
    items = CartItem.query.filter_by(user_id=user_id).all()
    
    articles_panier = []
    total = 0
    
    for item in items:
        if item.product:
            subtotal = item.product.price * item.quantity
            total += subtotal
            articles_panier.append({
                "nom": item.product.name,
                "quantite": item.quantity,
                "prix": float(item.product.price)
            })
            
    return render_template('paiement.html', articles=articles_panier, total_prix=round(total, 2))


# =========================================================
# CREATION DE SESSION DE PAIEMENT STRIPE
# =========================================================

@panier_blueprint.route('/panier/creer-session-paiement', methods=['POST'])
def creer_session_paiement():
    if 'user_id' not in session:
        abort(403)

    user_id = session['user_id']

    # Récupération des données du formulaire de facturation
    nom = request.form.get('nom', '')
    prenom = request.form.get('prenom', '')
    email = request.form.get('email', '')

    # Sauvegarde temporaire des infos client dans la session Flask
    session['billing_info'] = {
        'nom': nom,
        'prenom': prenom,
        'email': email
    }

    try:
        items = CartItem.query.filter_by(user_id=user_id).all()
        if not items:
            flash("Votre panier est vide.", "error")
            return redirect(url_for('panier.voir_panier'))

        line_items_stripe = []
        for item in items:
            if item.product:
                line_items_stripe.append({
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': item.product.name
                        },
                        'unit_amount': int(item.product.price * 100),
                    },
                    'quantity': item.quantity
                })

        session_stripe = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=email if email else None,
            line_items=line_items_stripe,
            mode='payment',
            success_url=url_for('panier.paiement_succes', _external=True),
            cancel_url=url_for('panier.page_paiement', _external=True),
        )

        return redirect(session_stripe.url, code=303)

    except Exception as e:
        print(f"Erreur Stripe : {e}")
        return "Une erreur est survenue lors de l'initialisation du paiement.", 500


# =========================================================
# CONFIRMATION DU PAIEMENT & ENVOI AUTOMATIQUE DU PDF
# =========================================================

@panier_blueprint.route('/panier/paiement-reussi')
def paiement_succes():
    if 'user_id' not in session:
        abort(403)

    user_id = session['user_id']
    items = CartItem.query.filter_by(user_id=user_id).all()
    
    if not items:
        return redirect(url_for('magasin.index'))

    try:
        # 1. Enregistrement de la commande en BDD
        total = sum(item.product.price * item.quantity for item in items if item.product)

        nouvelle_commande = Order(
            user_id=user_id,
            total_price=total,
            status='Payé'
        )
        db.session.add(nouvelle_commande)
        db.session.flush()

        articles_pour_facture = []
        for item in items:
            if item.product:
                details_article = OrderItem(
                    order_id=nouvelle_commande.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price_at_purchase=item.product.price
                )
                db.session.add(details_article)

                articles_pour_facture.append({
                    "nom": item.product.name,
                    "quantite": item.quantity,
                    "prix": float(item.product.price)
                })

                if item.product.stock >= item.quantity:
                    item.product.stock -= item.quantity
                else:
                    item.product.stock = 0

        # 2. Récupération des infos client enregistrées
        billing_info = session.get('billing_info', {})
        nom = billing_info.get('nom', 'Client')
        prenom = billing_info.get('prenom', '')
        client_email = billing_info.get('email', '')

        # 3. Génération du PDF
        path_dir = os.path.join("templates", "doc")
        if not os.path.exists(path_dir):
            os.makedirs(path_dir)

        nom_fichier = f"facture_occazgaming_cmd_{nouvelle_commande.id}.pdf"
        chemin_pdf = os.path.join(path_dir, nom_fichier)

        generer_facture_pdf(
            nom=nom,
            prenom=prenom,
            email=client_email,
            articles=articles_pour_facture,
            total=total,
            filename=chemin_pdf
        )

        # 4. Envoi du mail avec la facture en pièce jointe
        if client_email:
            msg = Message(
                subject=f"🎮 Merci pour votre achat ! Votre facture Occaz' Gaming (Commande #{nouvelle_commande.id})",
                recipients=[client_email],
                body=f"Bonjour {prenom} {nom},\n\nToute l'équipe d'Occaz' Gaming vous remercie pour votre commande !\n\nVous trouverez ci-joint votre facture officielle en format PDF.\n\nÀ très bientôt sur Occaz' Gaming !"
            )

            # Attachement du fichier PDF
            with open(chemin_pdf, 'rb') as fp:
                msg.attach(nom_fichier, 'application/pdf', fp.read())

            with mail.connect() as conn:
                conn.send(msg)

        # Nettoyage du panier
        CartItem.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
        flash("Merci pour votre achat ! Votre commande a été validée et votre facture vous a été envoyée par email.", "success")
        return render_template('succes.html', pdf_filename=nom_fichier)

    except Exception as e:
        db.session.rollback()
        print(f"Erreur validation commande : {e}")
        return "Le paiement est validé mais un problème est survenu lors du traitement de votre commande.", 500

# =========================================================
# GÉNÉRATEUR DE FACTURE PDF
# =========================================================
def generer_facture_pdf(nom, prenom, email, articles, total, filename="facture.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor("#2563eb"),
        spaceAfter=10
    )

    text_style = ParagraphStyle(
        'TextStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#18181b")
    )

    # 1. En-tête avec Logo en haut à gauche
    logo_path = os.path.join(os.getcwd(), 'static', 'img', 'logo.png')
    date_du_jour = datetime.now().strftime("%d/%m/%Y")

    if os.path.exists(logo_path):
        img = Image(logo_path, width=120, height=60)
        img.hAlign = 'LEFT'
        
        header_data = [
            [img, Paragraph("<b>FACTURE DE COMMANDE</b>", title_style)]
        ]
        header_table = Table(header_data, colWidths=[150, 350])
        header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        story.append(header_table)
    else:
        story.append(Paragraph("FACTURE DE COMMANDE", title_style))

    story.append(Spacer(1, 15))

    # 2. Informations Entreprise & Client
    info_data = [
        [
            Paragraph("<b>Vendeur :</b><br/>Occaz' Gaming<br/>PC d'occasion & Hautes Performances<br/>Contact: occazware@gmail.com", text_style),
            Paragraph(f"<b>Client :</b><br/>{prenom} {nom}<br/>Email: {email}<br/>Date: {date_du_jour}", text_style)
        ]
    ]
    info_table = Table(info_data, colWidths=[250, 250])
    story.append(info_table)
    story.append(Spacer(1, 20))

    # 3. Tableau des articles
    table_data = [["Article", "Quantité", "Prix Unitaire", "Total"]]
    for item in articles:
        table_data.append([
            item['nom'],
            str(item['quantite']),
            f"{item['prix']:.2f} €",
            f"{item['prix'] * item['quantite']:.2f} €"
        ])

    table = Table(table_data, colWidths=[240, 70, 90, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2563eb")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor("#f8f9fa")),
        ('GRID', (0, 0), (-1, -2), 1, colors.HexColor("#e0e0e0")),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))

    story.append(table)
    story.append(Spacer(1, 30))
    story.append(Paragraph("<i>Merci pour votre confiance en Occaz' Gaming ! Vos composants sont testés et garantis.</i>", text_style))

    doc.build(story)
