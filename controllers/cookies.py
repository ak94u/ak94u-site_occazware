from flask import Blueprint, jsonify, make_response

cookies_blueprint = Blueprint('cookies', __name__)

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

@cookies_blueprint.route('/set-theme/<mode>', methods=['POST'])
def set_theme(mode):
    if mode not in ["light", "dark"]:
        return jsonify({"error": "Mode invalide"}), 400

    response = make_response(jsonify({"status": "ok"}))
    response.set_cookie(
        "theme",
        mode,
        max_age=60*60*24*365,  # 1 an
        samesite='Lax'
    )
    return response

