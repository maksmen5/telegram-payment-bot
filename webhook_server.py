import telebot
from flask import Flask, request
import hmac
import hashlib
import base64
from urllib.parse import urlencode
from config import BOT_TOKEN, COURSES, CHANNELS, MERCHANT_ACCOUNT, MERCHANT_SECRET_KEY
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)  # Переніс сюди

bot = telebot.TeleBot(BOT_TOKEN)

# === ВАЖЛИВО: webhook endpoint ===
@app.route('/webhook', methods=['POST'])
def webhook():
    logging.info(f"Webhook received: {request.data}")
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "ok", 200
    else:
        return "unsupported Media Type", 415


@app.route('/')
def index():
    return "🤖 Бот працює через Webhook!", 200


# ======= Ваші хендлери =========
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('📚 Курси', 'ℹ️ Інформація')
    bot.send_message(message.chat.id, "👋 Привіт! Обери опцію нижче:", reply_markup=markup)

# інші ваші хендлери...


if __name__ == '__main__':
    # Установіть webhook
    webhook_url = "https://ВАШ_ДОМЕН/webhook"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)

    # Запуск Flask сервера
    app.run(host="0.0.0.0", port=5000, debug=False)
