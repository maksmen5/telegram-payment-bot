from flask import Flask, request, jsonify
import hmac
import base64
import telebot
import threading

from config import BOT_TOKEN, MERCHANT_SECRET_KEY, CHANNELS

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Webhook WayForPay
def validate_signature(data, signature):
    keys = [
        "merchantAccount", "orderReference", "amount", "currency",
        "authCode", "cardPan", "transactionStatus", "reasonCode"
    ]
    sign_str = ";".join(str(data.get(k, "")) for k in keys)
    calculated = base64.b64encode(hmac.new(
        MERCHANT_SECRET_KEY.encode(), sign_str.encode(), digestmod="md5"
    ).digest()).decode()
    return calculated == signature

@app.route("/wayforpay_callback", methods=["POST"])
def callback():
    data = request.json
    signature = data.get("signature", "")
    if data.get("transactionStatus") == "Approved" and validate_signature(data, signature):
        user_id = int(data.get("clientAccountId"))
        course_id = data.get("orderReference").split("_")[-1]
        try:
            chat_id = CHANNELS.get(course_id)
            invite = bot.create_chat_invite_link(
                chat_id=chat_id,
                member_limit=1,
                creates_join_request=False
            )
            bot.send_message(user_id, f"✅ Оплата пройдена!\nОсь твоє посилання: {invite.invite_link}")
        except Exception as e:
            bot.send_message(user_id, f"❌ Помилка доступу: {e}")
        return jsonify({"code": "accept"})
    return jsonify({"code": "reject"})

@app.route("/")
def home():
    return "🚀 Webhook працює!"

# 👇 Телеграм БОТ
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привіт! Я працюю!")

# 🔁 Функція запуску бота у фоні
def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    # Запускаємо бота у фоні
    threading.Thread(target=run_bot).start()
    # Запускаємо Flask сервер
    app.run(host="0.0.0.0", port=5000)
