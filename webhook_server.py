import telebot
from telebot import types
from flask import Flask, request
import hmac
import hashlib
import base64
from urllib.parse import urlencode
import threading

from config import BOT_TOKEN, MERCHANT_ACCOUNT, MERCHANT_SECRET_KEY, COURSES, CHANNELS

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# === START MENU ===
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📅 Обрати курс")
    bot.send_message(message.chat.id, "👋 Привіт! Натисни кнопку нижче, щоб переглянути доступні курси.", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "📅 Обрати курс")
def show_courses(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for cid, course in COURSES.items():
        markup.add(types.InlineKeyboardButton(course['name'], callback_data=f"select_{cid}"))
    bot.send_message(message.chat.id, "📃 Обери курс:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("select_"))
def course_menu(call):
    cid = call.data.split("_")[1]
    course = COURSES[cid]
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("ℹ️ Інфо", callback_data=f"info_{cid}"),
        types.InlineKeyboardButton("💳 Купити", callback_data=f"buy_{cid}")
    )
    markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="go_back"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f"📘 {course['name']}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "go_back")
def back_to_courses(call):
    show_courses(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("info_"))
def course_info(call):
    cid = call.data.split("_")[1]
    course = COURSES[cid]
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id,
                     f"*{course['name']}*\n\n{course['description']}",
                     parse_mode="Markdown")

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
                     f"💳 Щоб купити *{course['name']}*, сплати {course['price']} грн:\n{pay_link}\n\nПісля оплати бот видасть доступ.",
                     parse_mode="Markdown")

# === PAYMENT CALLBACK ===
@app.route('/', methods=['POST'])
def wfp_callback():
    data = request.json
    if not data:
        return 'No JSON', 400

    order_ref = data.get('orderReference')
    status = data.get('transactionStatus')

    if status == 'Approved':
        chat_id = int(data.get('clientAccountId'))
        course_id = order_ref.split('_')[-1]
        handle_successful_payment(chat_id, course_id)
    return 'OK'

# === ACCESS DELIVERY ===
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

# === RUN BOT IN THREAD ===
thr = threading.Thread(target=lambda: bot.infinity_polling(timeout=10, long_polling_timeout=5))
thr.start()

# === PING ENDPOINT ===
@app.route('/', methods=['GET'])
def index():
    return 'Bot is running!'

# === MAIN ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
