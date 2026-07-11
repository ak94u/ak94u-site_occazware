from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

db = SQLAlchemy()
mail = Mail()

# =========================================================
# 1. DÉFINITION DU MODÈLE (Fidèle à PHPMyAdmin)
# =========================================================
class Product(db.Model):
    # Indique explicitement à SQLAlchemy le nom de la table sur PHPMyAdmin
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    
    # On utilise Numeric plutôt que Float pour éviter les bugs de centimes avec les prix
    price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Gestion du stock demandée dans ton cahier des charges
    stock = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.String(50))
    image_url = db.Column(db.String(255))

    def __repr__(self):
        return f"<Product {self.name}>"
    
    # =========================================================
# 2. MODÈLE UTILISATEUR (Table 'users')
# =========================================================
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='client')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f"<User {self.username}>"


# =========================================================
# 3. MODÈLE PANIER (Table 'cart_items')
# =========================================================
class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # Relations optionnelles pour charger facilement les objets liés en Python
    user = db.relationship('User', backref=db.backref('cart_items', lazy=True))
    product = db.relationship('Product')


# =========================================================
# 4. MODÈLE COMMANDE & LOGS (Tables 'orders' et 'order_items')
# =========================================================
class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default='Payé')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('orders', lazy=True))


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='RESTRICT'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Numeric(10, 2), nullable=False)

    order = db.relationship('Order', backref=db.backref('items', lazy=True))
    product = db.relationship('Product')