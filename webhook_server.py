from flask import Flask, request
import telebot
from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
