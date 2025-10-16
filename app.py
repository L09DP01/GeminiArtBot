import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
OPENROUTER_API_KEY = os.getenv('API_KEY_REF')

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
SUPABASE_API_URL = f"{SUPABASE_URL}/rest/v1"


def send_telegram_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)


def send_telegram_photo(chat_id, photo_url, caption=""):
    url = f"{TELEGRAM_API_URL}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption
    }
    requests.post(url, json=payload)


def send_menu(chat_id):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "👋 Bienvenue sur GeminiArtBot ! Que veux-tu faire ?",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "✍️ Prompt texte", "callback_data": "prompt_text"},
                    {"text": "📸 Photo", "callback_data": "prompt_photo"}
                ],
                [
                    {"text": "🎁 Crédits", "callback_data": "check_credits"},
                    {"text": "💳 Acheter", "callback_data": "buy_credits"}
                ],
                [
                    {"text": "ℹ️ À propos", "callback_data": "about_bot"}
                ]
            ]
        }
    }
    requests.post(url, json=payload)


def answer_callback(callback_query_id):
    url = f"{TELEGRAM_API_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id}
    requests.post(url, json=payload)


def get_user(user_id):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    response = requests.get(
        f"{SUPABASE_API_URL}/users?id=eq.{user_id}",
        headers=headers
    )
    users = response.json()
    return users[0] if users else None


def create_user(user_id):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    payload = {
        "id": user_id,
        "credits": 3,
        "language": "en"
    }
    response = requests.post(
        f"{SUPABASE_API_URL}/users",
        headers=headers,
        json=payload
    )
    if response.status_code == 201:
        # Some setups may return 201 with an empty body. Fallback to fetching the user.
        try:
            data = response.json()
            if isinstance(data, list) and data:
                return data[0]
        except Exception:
            pass
        # Fallback: fetch created user
        fetched = get_user(user_id)
        if fetched:
            return fetched
    # User already exists
    if response.status_code == 409:
        return get_user(user_id)
    # Log error to server console for debugging
    try:
        print(f"create_user error: status={response.status_code}, body={response.text}")
    except Exception:
        pass
    return None


def update_user_credits(user_id, new_credits):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"credits": new_credits}
    requests.patch(
        f"{SUPABASE_API_URL}/users?id=eq.{user_id}",
        headers=headers,
        json=payload
    )


def save_prompt(user_id, prompt_text, image_url):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "user_id": user_id,
        "prompt_text": prompt_text,
        "image_url": image_url
    }
    requests.post(
        f"{SUPABASE_API_URL}/prompts",
        headers=headers,
        json=payload
    )


def generate_image(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "google/gemini-2.5-flash-image-preview",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            if "http" in content:
                lines = content.split("\n")
                for line in lines:
                    if "http" in line:
                        url_start = line.find("http")
                        url_end = line.find(")", url_start)
                        if url_end == -1:
                            url_end = line.find(" ", url_start)
                        if url_end == -1:
                            url_end = len(line)
                        return line[url_start:url_end].strip()

            return None
        else:
            return None
    except Exception as e:
        print(f"Error generating image: {e}")
        return None


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    callback = data.get('callback_query')
    if callback:
        chat_id = callback['message']['chat']['id']
        user_id = callback['from']['id']
        callback_data = callback['data']

        if callback_data == 'prompt_text':
            send_telegram_message(chat_id, "✍️ Envoie-moi ton prompt texte !")
        elif callback_data == 'prompt_photo':
            send_telegram_message(chat_id, "📸 Envoie-moi une photo maintenant.")
        elif callback_data == 'check_credits':
            user = get_user(user_id)
            if not user:
                user = create_user(user_id)
            if user:
                send_telegram_message(chat_id, f"🎁 Tu as *{user['credits']} crédit(s)* disponibles.")
            else:
                send_telegram_message(chat_id, "❌ Erreur de création du compte. Réessaie plus tard.")
        elif callback_data == 'buy_credits':
            send_telegram_message(chat_id, "💳 Paiement bientôt disponible via Stripe/Telegram.")
        elif callback_data == 'about_bot':
            send_telegram_message(
                chat_id,
                "🤖 *GeminiArtBot* est un générateur d'images IA propulsé par Gemini 2.5 Flash et OpenRouter.\n\n"
                "✨ Envoie un prompt texte pour générer une image !\n\n"
                "💡 Chaque génération coûte 1 crédit."
            )

        answer_callback(callback['id'])
        return 'OK', 200

    if 'message' not in data:
        return 'OK', 200

    message = data['message']
    chat_id = message['chat']['id']
    user_id = message['from']['id']

    if 'text' not in message:
        return 'OK', 200

    text = message['text']

    if text.startswith('/start'):
        user = get_user(user_id)

        if not user:
            user = create_user(user_id)
            send_telegram_message(
                chat_id,
                "✨ *Compte créé !*\n\nTu as reçu *3 crédits gratuits* pour générer des images IA."
            )

        send_menu(chat_id)

    elif text.startswith('/credits'):
        user = get_user(user_id)
        if not user:
            user = create_user(user_id)
        if user:
            send_telegram_message(
                chat_id,
                f"💳 Tu as *{user['credits']} crédits* disponibles."
            )
        else:
            send_telegram_message(
                chat_id,
                "❌ Erreur de création du compte. Réessaie plus tard."
            )

    else:
        user = get_user(user_id)

        if not user:
            send_telegram_message(
                chat_id,
                "❌ Utilise /start pour t'inscrire d'abord."
            )
            return 'OK', 200

        if user['credits'] <= 0:
            send_telegram_message(
                chat_id,
                "⚠️ Tu n'as plus de crédits!"
            )
            return 'OK', 200

        send_telegram_message(chat_id, "🎨 Génération en cours...")

        image_url = generate_image(text)

        if image_url:
            new_credits = user['credits'] - 1
            update_user_credits(user_id, new_credits)
            save_prompt(user_id, text, image_url)

            send_telegram_photo(
                chat_id,
                image_url,
                f"✅ Image générée!\n\n💳 Crédits restants: *{new_credits}*"
            )
        else:
            send_telegram_message(
                chat_id,
                "❌ Erreur lors de la génération. Réessaie avec un prompt différent."
            )

    return 'OK', 200


@app.route('/')
def index():
    return 'GeminiArtBot is running!', 200


@app.route('/debug')
def debug():
    """Debug endpoint to test Supabase connection"""
    try:
        # Test basic connection
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        
        response = requests.get(f"{SUPABASE_API_URL}/users?limit=1", headers=headers)
        
        # Test user creation
        test_user_id = 999999999
        payload = {
            "id": test_user_id,
            "credits": 3,
            "language": "fr"
        }
        
        create_response = requests.post(
            f"{SUPABASE_API_URL}/users",
            headers={**headers, "Content-Type": "application/json"},
            json=payload
        )
        
        # Test user retrieval
        get_response = requests.get(
            f"{SUPABASE_API_URL}/users?id=eq.{test_user_id}",
            headers=headers
        )
        
        return {
            "status": "debug_info",
            "supabase_url": SUPABASE_URL,
            "supabase_key_set": bool(SUPABASE_KEY),
            "telegram_token_set": bool(TELEGRAM_TOKEN),
            "openrouter_key_set": bool(OPENROUTER_API_KEY),
            "connection_test": {
                "status_code": response.status_code,
                "response": response.text[:200] if response.text else "No response"
            },
            "create_test": {
                "status_code": create_response.status_code,
                "response": create_response.text[:200] if create_response.text else "No response"
            },
            "get_test": {
                "status_code": get_response.status_code,
                "response": get_response.text[:200] if get_response.text else "No response"
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "supabase_url": SUPABASE_URL,
            "supabase_key_set": bool(SUPABASE_KEY)
        }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
