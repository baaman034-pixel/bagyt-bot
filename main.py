import os
import threading
import time
import telebot
from telebot import types
from flask import Flask

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

cargo_db = {
    "0550997099": {"address": "Рынок Дордой 0 Проход", "status": "в пути", "time": "18:00", "courier": "Арген"},
    "0500315400": {"address": "Рынок Дордой 0 Проход", "status": "в пути", "time": "18:00", "courier": "Арген"}
}

ADRES_TEXT = "📍 Наш склад: Рынок Дордой 0 Проход\n🕘 9:00-18:00"
CONTACT_TEXT = "📞 Связь: 0550 99 70 99\n📞 Связь: 0500 31 54 00"

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📦 Проверить груз"))
    markup.add(types.KeyboardButton("📍 Адрес"), types.KeyboardButton("📞 Связаться"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Это BAGYT EXPRESS 📦\nОтправь номер для проверки груза.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "📍 Адрес")
def address_btn(message):
    bot.send_message(message.chat.id, f"{ADRES_TEXT}\n\n{CONTACT_TEXT}")

@bot.message_handler(func=lambda m: m.text == "📞 Связаться")
def contact_btn(message):
    bot.send_message(message.chat.id, CONTACT_TEXT)

@bot.message_handler(func=lambda m: m.text == "📦 Проверить груз")
def check_btn(message):
    bot.send_message(message.chat.id, "Отправь номер клиента (0550...):")

@bot.message_handler(func=lambda m: True)
def handle_number(message):
    digits = ''.join(filter(str.isdigit, message.text))
    if len(digits) < 9: return
    last9 = digits[-9:]
    for key in cargo_db:
        if key[-9:] == last9:
            info = cargo_db[key]
            bot.send_message(message.chat.id, f"📦 ГРУЗ НАЙДЕН\n\n🏠 Адрес: {info['address']}\n📋 Статус: {info['status']}\n⏰ Время: {info['time']}\n🚚 Курьер: {info['courier']}")
            return
    bot.send_message(message.chat.id, "❌ Груз не найден.")

@app.route('/')
def home():
    return "BAGYT BOT is live!"

def run_bot():
    # ВАЖНО - убираем конфликт
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(1)
    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Polling error: {e}, restart in 5 sec")
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
