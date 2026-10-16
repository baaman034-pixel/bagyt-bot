import os, telebot
TOKEN=os.getenv("BOT_TOKEN")
bot=telebot.TeleBot(TOKEN)
@bot.message_handler(commands=['start'])
def s(m): bot.send_message(m.chat.id,"Бот BAGYT работает! ✅")
print("Bot started")
bot.infinity_polling()
