import os
from flask import Blueprint, render_template, request, jsonify
from models.db import mail
from flask_mail import Message
from anthropic import Anthropic

chatbot_blueprint = Blueprint('chatbot', __name__)

# Initialisation du client Anthropic
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Prompt système pour calibrer l'attitude de Claude
SYSTEM_PROMPT = """
Tu es l'assistant IA officiel du magasin "Occaz' Gaming". Ton rôle est d'aider les clients à concevoir le PC Gamer idéal sur-mesure.

Règles de recommandation :
1. Demande le budget global du client et ses besoins (jeux visés, résolution 1080p/14K, usage streaming/montage, etc.).
2. Pour les composants majeurs (Carte graphique, RAM, SSD), oriente la stratégie vers le marché de l'occasion reconditionné (LeBonCoin, Vinted, eBay) pour maximiser le rapport performance/prix.
3. Pour le reste (Alimentation, Boîtier, Ventirad/AIO), conseille du neuf pour garantir la fiabilité et la sécurité électrique.
4. Reste concis, accueillant, pro et dynamique (style gamer/expert).
"""

@chatbot_blueprint.route('/assistant', methods=['GET'])
def page_assistant():
    return render_template('assistant.html')

@chatbot_blueprint.route('/api/chatbot', methods=['POST'])
def chat_api():
    try:
        data = request.json
        user_messages = data.get('messages', []) # Historique des messages [{role: 'user', content: '...'}, ...]

        if not user_messages:
            return jsonify({"error": "Aucun message fourni"}), 400

        # Appel à l'API Claude (claude-3-haiku-20240229)
        response = client.messages.create(
            model="claude-sonnet-5",  # Modèle Claude
            max_tokens=800,
            thinking={"type": "disabled"},
            system=SYSTEM_PROMPT,
            messages=user_messages
        )

        bot_reply = response.content[0].text
        return jsonify({"reply": bot_reply})

    except Exception as e:
        print(f"❌ Erreur API Claude : {e}")
        return jsonify({"error": "Une erreur est survenue avec l'assistant."}), 500


@chatbot_blueprint.route('/api/envoyer-rapport-config', methods=['POST'])
def envoyer_rapport():
    try:
        data = request.json
        historique_chat = data.get('chat_summary', 'Pas de détail')
        client_email = data.get('client_email', 'Non précisé')

        contenu_html = f"""
        <div style="font-family: sans-serif; max-width: 600px; padding: 20px; background: #18181b; color: white; border-radius: 12px;">
            <h2 style="color: #3b82f6;">🎮 Nouvelle Config Sur-Mesure à Valider !</h2>
            <p><strong>Contact Client / Email :</strong> {client_email}</p>
            <hr style="border-color: #3f3f46;">
            <h3>Récapitulatif de la discussion avec l'IA :</h3>
            <div style="background: #09090b; padding: 15px; border-radius: 8px; font-size: 14px; white-space: pre-line;">
                {historique_chat}
            </div>
            <p style="font-size: 12px; color: #a1a1aa; margin-top: 15px;">
                💡 Action requise : Effectuer la recherche sur Leboncoin / Vinted pour GPU/RAM/SSD selon la demande ci-dessus.
            </p>
        </div>
        """

        msg = Message(
            subject="📥 Nouvelle demande de configuration PC - Occaz' Gaming",
            recipients=['occazware@gmail.com'],
            html=contenu_html
        )
        
        with mail.connect() as conn:
            conn.send(msg)

        return jsonify({"success": True, "message": "Le rapport a été envoyé avec succès à occazware@gmail.com !"})

    except Exception as e:
        print(f"❌ Erreur Envoi Mail : {e}")
        return jsonify({"success": False, "error": str(e)}), 500