import telebot

BOT_TOKEN = "твій_токен_тут"
WEBHOOK_URL = "https://telegram-payment-bot-v0hn.onrender.com/webhook"

bot = telebot.TeleBot(BOT_TOKEN)

bot.remove_webhook()
result = bot.set_webhook(url=WEBHOOK_URL)
print("Webhook set result:", result)
