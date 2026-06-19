import telebot
import random

TOKEN = "8037523480:AAEJiBMKH461dtrP4PTyszzuULS-4d3Xj4U"
bot = telebot.TeleBot(TOKEN)
users = {}

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "👋 Hola! Usa /ver para ganar USDT")

@bot.message_handler(commands=['ver'])
def ver(m):
    uid = m.from_user.id
    if uid not in users:
        users[uid] = 0.0
    g = round(random.uniform(0.02, 0.08), 3)
    users[uid] += g
    bot.reply_to(m, f"📺 Ganaste +{g} USDT\n💰 Saldo: {users[uid]:.3f}")

@bot.message_handler(commands=['saldo'])
def saldo(m):
    uid = m.from_user.id
    bot.reply_to(m, f"💰 Saldo: {users.get(uid, 0.0):.3f} USDT")

print("🤖 Bot activo")
bot.infinity_polling()
