import telebot
from flask import Flask, request
import os
import hmac
import hashlib
import base64
from urllib.parse import urlencode
from config import BOT_TOKEN, COURSES, CHANNELS, MERCHANT_ACCOUNT, MERCHANT_SECRET_KEY
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)

# === Webhook endpoint ===
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok", 200
    else:
        return "Unsupported Media Type", 415

@app.route('/')
def index():
    return "🤖 Бот працює через Webhook!", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"

    # Установлюємо webhook
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)

    app.run(host="0.0.0.0", port=port)
