# config.py

# 🔐 Дані бота
BOT_TOKEN = "7915072837:AAEa8tNscTu-bPdQr0lpCBO68vaVkhiSBus"
MERCHANT_ACCOUNT = "7de8a72b71369907282f75c00bb050e8"
MERCHANT_SECRET_KEY = "8600b023c86794b0496293e6b907aee895baa8e0"

# 📦 Курси
COURSES = {
    "gym": {"name": "Тренування в залі", "price": 400, "description": "Програма тренувань у залі."},
    "bodybuilding": {"name": "Бодібілдинг", "price": 500, "description": "Класичний набір маси."},
    "power": {"name": "Пауерліфтинг", "price": 600, "description": "Жим, присід, тяга для сили."},
    "home": {"name": "Домашні тренування", "price": 0, "description": "Безкоштовна програма вдома."},
    "food": {"name": "План Харчування", "price": 300, "description": "Раціон для росту та сушки."},
    "steroids": {"name": "Стероїди", "price": 200, "description": "Правда про фарму."},
    "coach_chat": {"name": "Чат з тренером", "price": 100, "description": "2 дні особистих відповідей."}
}

# 📍 ID або @юзернейми каналів (перевір, що бот є адміністратором кожного!)
CHANNELS = {
    "gym": -1001111111111,
    "bodybuilding": -1002222222222,
    "power": -1003333333333,
    "home": -1002544564658,
    "food": -1005555555555,
    "steroids": -1006666666666,
    "coach_chat": -1007777777777
}
