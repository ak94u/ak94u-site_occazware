from flask import Blueprint, jsonify, request, make_response, render_template

cookies_blueprint = Blueprint('cookies', __name__)

# --- Créer un cookie ---
@cookies_blueprint.route('/set-cookie')
def set_cookie():
    response = make_response("Cookie 'theme' créé !")
    response.set_cookie("theme", "dark", max_age=60*60*24*30)  # 30 jours
    return response

# --- Lire un cookie ---
@cookies_blueprint.route('/get-cookie')
def get_cookie():
    theme = request.cookies.get("theme", "non défini")
    return f"Thème actuel : {theme}"

# --- Supprimer un cookie ---
@cookies_blueprint.route('/delete-cookie')
def delete_cookie():
    response = make_response("Cookie supprimé")
    response.delete_cookie("theme")
    return response

# --- Bannière de consentement optimisée pour Fetch ---
@cookies_blueprint.route('/consent')
def consent():
    # On renvoie une réponse JSON (plus propre pour du JavaScript)
    response = make_response(jsonify({"status": "success", "message": "Consentement enregistré"}))
    
    # Sécurisation du cookie : httponly=False pour que le JS puisse le lire au chargement,
    # samesite='Lax' pour la sécurité.
    response.set_cookie(
        "consent", 
        "true", 
        max_age=60*60*24*365,  # 1 an
        samesite='Lax'
    )
    return response
