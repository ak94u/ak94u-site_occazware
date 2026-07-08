from flask import Blueprint, render_template, request
# 1. On importe le 'db' et le modèle 'Product' depuis ton fichier models
from models.db import Product 

# On crée le Blueprint pour regrouper nos routes principales
page_magasin = Blueprint('magasin', __name__)

# Ta page de magasin
@page_magasin.route('/magasin')
def index():
    # 1. On récupère les filtres envoyés par le formulaire HTML
    recherche = request.args.get('q', '')
    categories = request.args.getlist('categorie') # ex: ['PC Fixe', 'Composant']
    prix_max = request.args.get('prix_max', 2500, type=int)

    # 2. On prépare la requête de base vers ta table Product (PHPMyAdmin)
    # Note : on utilise Product.query directement, pas db.Product
    query = Product.query.filter(Product.price <= prix_max)

    # 3. On applique les filtres s'ils sont remplis
    if recherche:
        query = query.filter(Product.name.ilike(f"%{recherche}%"))
    
    if categories:
        query = query.filter(Product.category.in_(categories))

    # 4. On récupère les résultats filtrés et on les envoie au HTML
    liste_produits = query.all()
    
    return render_template('magasin.html', produits=liste_produits)