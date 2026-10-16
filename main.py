import os
import threading
import telebot
from telebot import types
from flask import Flask

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# === БАЗА ГРУЗОВ ===
cargo_db = {
    "0550997099": {
        "address": "Рынок Дордой 0 Проход",
        "status": "в пути",
        "time": "18:00",
        "courier": "Арген"
    },
    "0500315400": {
        "address": "Рынок Дордой 0 Проход",
        "status": "в пути",
        "time": "18:00",
        "courier": "Арген"
    }
}

ADRES_TEXT = "📍 Наш склад: Рынок Дордой 0 Проход\n🕘 Работаем 9:00-18:00"
CONTACT_TEXT = "📞 Связь: 0550 99 70 99\n📞 Связь: 0500 31 54 00"

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📦 Проверить груз"))
    markup.add(types.KeyboardButton("📍 Адрес"), types.KeyboardButton("📞 Связаться"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Это бот BAGYT EXPRESS 📦\nНажми кнопку ниже и отправь номер клиента.",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda m: m.text == "📦 Проверить груз")
def check_btn(message):
    bot.send_message(message.chat.id, "Отправь номер телефона клиента (например 0550997099):")

@bot.message_handler(func=lambda m: m.text == "📍 Адрес")
def address_btn(message):
    bot.send_message(message.chat.id, f"{ADRES_TEXT}\n\n{CONTACT_TEXT}")

@bot.message_handler(func=lambda m: m.text == "📞 Связаться")
def contact_btn(message):
    bot.send_message(message.chat.id, CONTACT_TEXT)

@bot.message_handler(func=lambda m: True)
def handle_number(message):
    # оставляем только цифры, берем последние 9-10 цифр
    digits = ''.join(filter(str.isdigit, message.text))
    if len(digits) < 9:
        return

    last9 = digits[-9:]  # 550997099

    # ищем по последним 9 цифрам
    found_key = None
    for key in cargo_db:
        if key[-9:] == last9:
            found_key = key
            break

    if found_key:
        info = cargo_db[found_key]
        bot.send_message(
            message.chat.id,
            f"📦 ГРУЗ НАЙДЕН\n\n"
            f"🏠 Адрес: {info['address']}\n"
            f"📋 Статус: {info['status']}\n"
            f"⏰ Время доставки: {info['time']}\n"
            f"🚚 Курьер: {info['courier']}"
        )
    else:
        bot.send_message(message.chat.id, "❌ Груз не найден по этому номеру. Проверьте номер.")

@app.route('/')
def home():
    return "Bot is running 24/7"

def run_bot():
    bot.delete_webhook(drop_pending_updates=True)
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=10000)
