import os
import threading
from flask import Flask
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN не найден в Environment!")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# === БАЗА ГРУЗОВ - тут добавляй свои ===
# Формат: "номер телефона": {"адрес": "...", "статус": "...", "время": "...", "курьер": "..."}
CARGO_DB = {
    "0550997099": {"адрес": "ул. Касымалы Баялинов 89", "статус": "в пути", "время": "18:00", "курьер": "Арген"},
    "0772132289": {"адрес": "ул. Махатма Ганди 73", "статус": "на складе в Оше", "время": "15:00", "курьер": "Байэл"},
    "0550123456": {"адрес": "ул. Ленина 123", "статус": "принят", "время": "10:00", "курьер": "Нурбек"},
}

@app.route('/')
def home():
    return "BAGYT Bot is running ✅"

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📦 Проверить груз"))
    markup.add(types.KeyboardButton("📍 Адрес"), types.KeyboardButton("📞 Связаться"))
    
    bot.send_message(
        message.chat.id, 
        "Привет! Это бот BAGYT EXPRESS 🚚\n\nНажми '📦 Проверить груз' и отправь номер телефона клиента.",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == "📦 Проверить груз")
def ask_number(message):
    bot.send_message(message.chat.id, "Отправь номер телефона клиента (например 0550997099):")

@bot.message_handler(func=lambda m: m.text == "📍 Адрес")
def address(message):
    bot.send_message(message.chat.id, "📍 Наш склад: г. Ош, ул. Касымалы Баялинов 89\n🕘 Работаем 9:00-18:00")

@bot.message_handler(func=lambda m: m.text == "📞 Связаться")
def contact(message):
    bot.send_message(message.chat.id, "📞 Связь: +996 555 123 456\n👨‍💼 Менеджер: @bagyt_manager")

@bot.message_handler(func=lambda m: True)
def check_cargo(message):
    phone = message.text.strip().replace(" ", "").replace("+996", "0")
    # берем последние 10 цифр
    if len(phone) > 10:
        phone = phone[-10:]
    
    cargo = CARGO_DB.get(phone)
    
    if cargo:
        text = f"""📦 ГРУЗ НАЙДЕН

📱 Номер: {phone}
🏠 Адрес: {cargo['адрес']}
📋 Статус: {cargo['статус']}
⏰ Время доставки: {cargo['время']}
🚚 Курьер: {cargo['курьер']}"""
        bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, f"❌ Груз по номеру {phone} не найден.\nПроверь номер и попробуй еще раз.")

def run_bot():
    print("Bot started successfully!")
    bot.infinity_polling(none_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
