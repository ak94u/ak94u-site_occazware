import os
from flask import Blueprint, flash, redirect, render_template, request, session, abort, url_for, current_app
from models import db
from models.db import db, Product, Order
from werkzeug.utils import secure_filename

page_admin = Blueprint('admin', __name__)

@page_admin.route('/admin/dashboard')
def dashboard():
    # 1. SÉCURITÉ : Vérifier si l'utilisateur est connecté ET s'il est admin
    if 'user_role' not in session or session['user_role'] != 'admin':
        # Si ce n'est pas un admin, on renvoie une erreur 403 (Accès interdit)
        # Comme ça, le client ne voit absolument rien du contenu.
        abort(403)

    # 2. LOGIQUE ADMIN : Si c'est bien l'admin, on charge les données secrètes
    # Exemple : Calcul du chiffre d'affaires total (Cahier des charges)
    all_orders = Order.query.order_by(Order.created_at.desc()).all()
    chiffre_affaire = sum(c.total_price for c in all_orders)
    total_produits = Product.query.count()
    tous_les_produits = Product.query.all()

    return render_template('admin.html', 
                           commandes=all_orders,
                           ca=chiffre_affaire, 
                           total_products=total_produits,
                           produits=tous_les_produits)

@page_admin.route('/admin/supprimer-produit/<int:product_id>', methods=['POST'])
def supprimer_produit(product_id):
    # 1. SÉCURITÉ : On vérifie toujours si c'est bien l'admin
    if 'user_role' not in session or session['user_role'] != 'admin':
        abort(403)

    # 2. On cherche le produit en base de données
    produit = Product.query.get_or_404(product_id)

    try:
        # 3. On le supprime
        db.session.delete(produit)
        db.session.commit()
        flash(f"Le produit '{produit.name}' a été supprimé du catalogue avec succès.", "success")
    except Exception as e:
        db.session.rollback()
        # Sécurité : Si le produit est lié à une commande passée (ON DELETE RESTRICT), MySQL va bloquer
        flash("Impossible de supprimer ce produit car il est lié à une commande dans l'historique.", "error")

    # 4. On recharge le tableau de bord
    return redirect(url_for('admin.dashboard'))

@page_admin.route('/admin/ajouter-produit', methods=['POST'])
def ajouter_produit():
    # 1. Sécurité Admin
    if 'user_role' not in session or session['user_role'] != 'admin':
        abort(403)

    # 2. Récupération des données du formulaire
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price', type=float)
    category = request.form.get('category')
    stock = request.form.get('stock', type=int)
    
    # 3. Gestion de l'image
    file = request.files.get('image')
    filename = 'default.png'  # Image par défaut si aucune n'est fournie

    if file and file.filename != '':
        # Sécurise le nom du fichier (évite les caractères bizarres)
        filename = secure_filename(file.filename)
        # Sauvegarde l'image dans static/img/
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

    # 4. Création et enregistrement du produit
    nouveau_produit = Product(
        name=name,
        description=description,
        price=price,
        category=category,
        stock=stock,
        image_url=filename
    )

    try:
        db.session.add(nouveau_produit)
        db.session.commit()
        flash(f"Le produit '{name}' a été ajouté au catalogue !", "success")
    except Exception as e:
        db.session.rollback()
        flash("Erreur lors de l'ajout du produit en base de données.", "error")

    return redirect(url_for('admin.dashboard'))