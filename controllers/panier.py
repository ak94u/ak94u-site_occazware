from flask import Blueprint, session, redirect, url_for, flash, abort, render_template, request
from models.db import db, Product, CartItem, Order, OrderItem
import stripe
from dotenv import load_dotenv
import os

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


@panier_blueprint.route('/panier/creer-session-paiement', methods=['POST'])
def creer_session_paiement():
    if 'user_id' not in session:
        abort(403)

    user_id = session['user_id']

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
            line_items=line_items_stripe,
            mode='payment',
            success_url=url_for('panier.paiement_succes', _external=True),
            cancel_url=url_for('panier.page_paiement', _external=True),
        )

        return redirect(session_stripe.url, code=303)

    except Exception as e:
        print(f"Erreur Stripe : {e}")
        return "Une erreur est survenue lors de l'initialisation du paiement.", 500


@panier_blueprint.route('/panier/paiement-reussi')
def paiement_succes():
    if 'user_id' not in session:
        abort(403)

    user_id = session['user_id']
    items = CartItem.query.filter_by(user_id=user_id).all()
    
    if not items:
        return redirect(url_for('magasin.index'))

    try:
        total = sum(item.product.price * item.quantity for item in items if item.product)

        nouvelle_commande = Order(
            user_id=user_id,
            total_price=total,
            status='Payé'
        )
        db.session.add(nouvelle_commande)
        db.session.flush()

        for item in items:
            if item.product:
                details_article = OrderItem(
                    order_id=nouvelle_commande.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price_at_purchase=item.product.price
                )
                db.session.add(details_article)

                if item.product.stock >= item.quantity:
                    item.product.stock -= item.quantity
                else:
                    item.product.stock = 0

        CartItem.query.filter_by(user_id=user_id).delete()
        
        db.session.commit()
        flash("Merci pour votre achat ! Votre commande a été validée.", "success")
        return render_template('succes.html')

    except Exception as e:
        db.session.rollback()
        print(f"Erreur validation commande : {e}")
        return "Le paiement est validé mais un problème est survenu lors du traitement de votre commande.", 500
