import os, threading, time, requests, csv, io
import telebot
from telebot import types
from flask import Flask

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

SHEET_ID = "1pMTtrBhPOpTJmr6SzMXTolpvUVSt20ygTYFZZKaZPzc"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

cargo_db = {}

def load_from_sheet():
    global cargo_db
    try:
        r = requests.get(SHEET_URL, timeout=10)
        r.raise_for_status()
        f = io.StringIO(r.text)
        reader = csv.DictReader(f)
        new_db = {}
        for row in reader:
            phone_raw = row.get('phone','')
            phone = ''.join(filter(str.isdigit, str(phone_raw)))
            if not phone: continue
            new_db[phone] = {
                "address": row.get('address','Рынок Дордой 0 Проход') or "Рынок Дордой 0 Проход",
                "status": row.get('status','в пути') or "в пути",
                "time": row.get('time','18:00') or "18:00",
                "courier": row.get('courier','Арген') or "Арген"
            }
        if new_db:
            cargo_db = new_db
            print(f"Loaded {len(cargo_db)} cargos from Sheet")
    except Exception as e:
        print(f"Sheet error: {e}")

load_from_sheet()

def sheet_loop():
    while True:
        time.sleep(120) # обновление каждые 2 мин
        load_from_sheet()

ADRES_TEXT = "📍 Наш склад: Рынок Дордой 0 Проход\n🕘 9:00-18:00"
CONTACT_TEXT = "📞 Связь: 0550 99 70 99\n📞 Связь: 0500 31 54 00"

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📦 Проверить груз"))
    markup.add(types.KeyboardButton("📍 Адрес"), types.KeyboardButton("📞 Связаться"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! BAGYT EXPRESS 📦\nОтправь номер для проверки.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "📍 Адрес")
def address_btn(message):
    bot.send_message(message.chat.id, f"{ADRES_TEXT}\n\n{CONTACT_TEXT}")

@bot.message_handler(func=lambda m: m.text == "📞 Связаться")
def contact_btn(message):
    bot.send_message(message.chat.id, CONTACT_TEXT)

@bot.message_handler(func=lambda m: m.text == "📦 Проверить груз")
def check_btn(message):
    bot.send_message(message.chat.id, "Отправь номер клиента:")

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
def home(): return "BAGYT BOT live with Google Sheet!"

def run_bot():
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(1)
    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=60)
        except Exception as e:
            print(e); time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=sheet_loop, daemon=True).start()
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
