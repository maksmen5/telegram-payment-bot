import telebot
from flask import Flask, request
import hmac
import hashlib
import base64
from urllib.parse import urlencode

from config import BOT_TOKEN, COURSES, CHANNELS, MERCHANT_ACCOUNT, MERCHANT_SECRET_KEY

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

# Стартове меню
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('📚 Курси', 'ℹ️ Інформація')
    bot.send_message(message.chat.id, "👋 Привіт! Обери опцію нижче:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == '📚 Курси')
def show_courses(message):
    markup = telebot.types.InlineKeyboardMarkup()
    for cid, course in COURSES.items():
        markup.add(telebot.types.InlineKeyboardButton(course['name'], callback_data=f"select_{cid}"))
    bot.send_message(message.chat.id, "📘 Доступні курси:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("select_"))
def course_menu(call):
    cid = call.data.split("_")[1]
    course = COURSES[cid]
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("ℹ️ Інфо", callback_data=f"info_{cid}"),
        telebot.types.InlineKeyboardButton("💳 Купити", callback_data=f"buy_{cid}"),
        telebot.types.InlineKeyboardButton("🔙 Назад", callback_data="back")
    )
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=f"📘 {course['name']}",
                          reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("info_"))
def course_info(call):
    cid = call.data.split("_")[1]
    course = COURSES[cid]
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id,
                     f"*{course['name']}*\n\n{course['description']}",
                     parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "back")
def back_to_courses(call):
    show_courses(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def course_buy(call):
    cid = call.data.split("_")[1]
    course = COURSES[cid]

    if course['price'] == 0:
        handle_successful_payment(call.message.chat.id, cid)
        return

    order_ref = f"order_{call.message.chat.id}_{cid}"
    data = {
        "merchantAccount": MERCHANT_ACCOUNT,
        "merchantDomainName": "test.com",
        "orderReference": order_ref,
        "orderDate": 1699999999,
        "amount": course['price'],
        "currency": "UAH",
        "productName": [course['name']],
        "productCount": [1],
        "productPrice": [course['price']],
        "clientAccountId": str(call.message.chat.id),
        "returnUrl": "https://t.me/your_bot"
    }

    keys = [
        MERCHANT_ACCOUNT, "test.com", order_ref, "1699999999",
        str(course['price']), "UAH", course['name'], "1", str(course['price'])
    ]
    sign_str = ";".join(keys)
    sign = base64.b64encode(hmac.new(MERCHANT_SECRET_KEY.encode(), sign_str.encode(), hashlib.md5).digest()).decode()
    data['merchantSignature'] = sign

    pay_link = "https://secure.wayforpay.com/pay?" + urlencode(data, doseq=True)

    bot.send_message(call.message.chat.id,
                     f"💳 Щоб купити {course['name']}, сплати {course['price']} грн:\n{pay_link}\n\nПісля оплати бот видасть доступ.")

def handle_successful_payment(user_id, course_id):
    try:
        chat_id = CHANNELS.get(course_id)
        if not chat_id:
            bot.send_message(user_id, "❌ Канал не знайдено для цього курсу.")
            return
        invite = bot.create_chat_invite_link(
            chat_id=chat_id,
            member_limit=1,
            creates_join_request=False
        )
        bot.send_message(user_id, f"✅ Оплату підтверджено!\n🔗 Ось твоє посилання:\n{invite.invite_link}")
    except Exception as e:
        bot.send_message(user_id, f"❌ Помилка видачі доступу:\n{e}")

# === ВАЖЛИВО: webhook endpoint ===
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
        bot.process_new_updates([update])
        return "ok", 200

# Стартова перевірка (не обов’язково)
@app.route('/')
def index():
    return "🤖 Бот працює через Webhook!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
