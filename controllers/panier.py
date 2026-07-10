from flask import Blueprint, session, redirect, url_for, flash, abort, render_template, request
from models.db import db, Product, CartItem  # Assure-toi que ton modèle s'appelle bien CartItem

panier_blueprint = Blueprint('panier', __name__)

@panier_blueprint.route('/ajouter-au-panier/<int:product_id>', methods=['POST'])
def ajouter_au_panier(product_id):
    # 1. SÉCURITÉ : L'utilisateur doit être connecté pour avoir un panier
    if 'user_id' not in session:
        flash("Vous devez être connecté pour ajouter un article au panier.", "error")
        return redirect(url_for('auth.connexion'))

    user_id = session['user_id']

    # 2. Vérifier si le produit existe et s'il reste du stock
    produit = Product.query.get_or_404(product_id)
    if produit.stock <= 0:
        flash("Désolé, ce produit est épuisé !", "error")
        return redirect(url_for('magasin.index'))

    # 3. Vérifier si le produit est DÉJÀ dans le panier de cet utilisateur
    item_panier = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()

    if item_panier:
        # Si le produit y est déjà, on regarde si on ne dépasse pas le stock total
        if item_panier.quantity < produit.stock:
            item_panier.quantity += 1
            db.session.commit()
            flash(f"Quantité augmentée pour {produit.name}.", "success")
        else:
            flash(f"Impossible d'ajouter plus d'exemplaires (limite du stock atteinte).", "error")
    else:
        # Si c'est la première fois qu'il l'ajoute, on crée une nouvelle ligne dans la table
        nouvel_item = CartItem(
            user_id=user_id,
            product_id=product_id,
            quantity=1
        )
        db.session.add(nouvel_item)
        db.session.commit()
        flash(f"'{produit.name}' a été ajouté à votre panier !", "success")

    # 4. On redirige l'utilisateur sur le magasin pour qu'il puisse continuer ses achats
    return redirect(url_for('magasin.index'))

@panier_blueprint.route('/panier')
def voir_panier():
    # 1. Sécurité : L'utilisateur doit être connecté
    if 'user_id' not in session:
        flash("Veuillez vous connecter pour accéder à votre panier.", "error")
        return redirect(url_for('auth.connexion'))

    user_id = session['user_id']

    # 2. Récupérer les articles du panier de cet utilisateur
    items = CartItem.query.filter_by(user_id=user_id).all()

    # 3. Calculer le prix total global du panier
    total_global = 0
    for item in items:
        # On calcule dynamiquement le prix total pour chaque ligne (quantité x prix unitaire)
        item.total_ligne = item.quantity * item.product.price
        total_global += item.total_ligne

    return render_template('panier.html', items=items, total_global=total_global)


@panier_blueprint.route('/panier/modifier/<int:item_id>', methods=['POST'])
def modifier_quantite(item_id):
    if 'user_id' not in session:
        abort(403)
        
    action = request.form.get('action') # 'augmenter' ou 'diminuer' ou 'supprimer'
    item = CartItem.query.get_or_404(item_id)
    
    # Sécurité pour être sûr que l'item appartient bien à l'utilisateur connecté
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

    db.session.commit()
    return redirect(url_for('panier.voir_panier'))