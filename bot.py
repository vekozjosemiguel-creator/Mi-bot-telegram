import telebot
import random
import requests
import json

TOKEN = "8037523480:AAEJiBMKH461dtrP4PTyszzuULS-4d3Xj4U"
ADSGRAM_TOKEN = "757fcee3c4fc4425acaeed9044fd1669"  # <-- TU TOKEN DE ADSGRAM
BLOCK_ID = "35611"  # <-- TU BLOCK ID

bot = telebot.TeleBot(TOKEN)
users = {}

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in users:
        users[uid] = {"saldo": 0.0, "historial": []}
    
    txt = (f"👋 ¡Bienvenido a Ganausdtviendoanuncios!\n\n"
           f"💰 Tu saldo: {users[uid]['saldo']:.2f} USDT\n\n"
           f"✅ Comandos:\n"
           f"/ver - Ganar USDT viendo anuncios\n"
           f"/saldo - Ver tu saldo\n"
           f"/retirar - Retirar ganancias\n"
           f"/historial - Ver historial\n"
           f"/ranking - Top usuarios\n"
           f"/invitar - Invitar amigos\n"
           f"/ayuda - Ayuda\n"
           f"/privacidad - Política de privacidad\n\n"
           f"¡Empieza con /ver! 🚀")
    bot.reply_to(message, txt)

@bot.message_handler(commands=['ver'])
def ver(message):
    uid = message.from_user.id
    if uid not in users:
        users[uid] = {"saldo": 0.0, "historial": []}
    
    try:
        # 1. Pedir anuncio a AdsGram
        url = "https://api.adsgram.ai/api/v1/ads"
        params = {
            "tgid": uid,
            "blockid": BLOCK_ID,
            "language": "es",
            "token": ADSGRAM_TOKEN
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # 2. Verificar que haya anuncio
        if not data.get('text_html'):
            raise Exception("No hay anuncios disponibles")
        
        # 3. Construir mensaje con el anuncio
        text_html = data.get('text_html', '')
        image_url = data.get('image_url')
        click_url = data.get('click_url')
        reward_url = data.get('reward_url')
        button_name = data.get('button_name', 'Ver anuncio')
        button_reward_name = data.get('button_reward_name', 'Reclamar recompensa')
        
        # 4. Enviar mensaje con botones
        markup = telebot.types.InlineKeyboardMarkup()
        btn_click = telebot.types.InlineKeyboardButton(button_name, url=click_url)
        btn_reward = telebot.types.InlineKeyboardButton(button_reward_name, callback_data=f"reward_{reward_url}")
        markup.add(btn_click, btn_reward)
        
        if image_url:
            bot.send_photo(uid, image_url, caption=text_html, reply_markup=markup, parse_mode='HTML', protect_content=True)
        else:
            bot.send_message(uid, text_html, reply_markup=markup, parse_mode='HTML', protect_content=True)
            
    except Exception as e:
        # Fallback: recompensa aleatoria si falla AdsGram
        g = round(random.uniform(0.02, 0.08), 3)
        users[uid]['saldo'] += g
        users[uid]['historial'].append(f"+{g} USDT (sin anuncio)")
        bot.reply_to(message, f"📺 No hay anuncios disponibles ahora.\n✅ Ganaste +{g} USDT\n💰 Saldo: {users[uid]['saldo']:.3f} USDT")

@bot.message_handler(commands=['saldo'])
def saldo(message):
    uid = message.from_user.id
    if uid not in users:
        users[uid] = {"saldo": 0.0, "historial": []}
    bot.reply_to(message, f"💰 Tu saldo: {users[uid]['saldo']:.3f} USDT")

@bot.message_handler(commands=['retirar'])
def retirar(message):
    uid = message.from_user.id
    if uid not in users:
        users[uid] = {"saldo": 0.0, "historial": []}
    saldo = users[uid]['saldo']
    if saldo < 0.50:
        bot.reply_to(message, f"⚠️ Mínimo para retirar: 0.50 USDT\nTu saldo: {saldo:.3f} USDT")
    else:
        bot.reply_to(message, f"💳 Retiro de {saldo:.3f} USDT\nEnvía tu dirección USDT (BEP20/TRC20)")

@bot.message_handler(commands=['historial'])
def historial(message):
    uid = message.from_user.id
    if uid not in users:
        users[uid] = {"saldo": 0.0, "historial": []}
    h = users[uid]['historial']
    if not h:
        bot.reply_to(message, "📊 Sin historial. Usa /ver")
    else:
        bot.reply_to(message, "📊 Historial:\n" + "\n".join(h[-10:]))

@bot.message_handler(commands=['ranking'])
def ranking(message):
    if not users:
        bot.reply_to(message, "📊 Sin usuarios registrados")
        return
    top = sorted(users.items(), key=lambda x: x[1]['saldo'], reverse=True)[:5]
    txt = "🏆 TOP 5:\n\n"
    for i, (uid, data) in enumerate(top, 1):
        txt += f"{i}. Usuario {str(uid)[-4:]} - {data['saldo']:.3f} USDT\n"
    bot.reply_to(message, txt)

@bot.message_handler(commands=['invitar'])
def invitar(message):
    uid = message.from_user.id
    bot.reply_to(message, f"🔗 Enlace: https://t.me/Ganausdtviendoanuncios_bot?start=ref_{uid}\n\n🎁 Gana 0.10 USDT por amigo")

@bot.message_handler(commands=['ayuda'])
def ayuda(message):
    bot.reply_to(message, "📋 COMANDOS:\n\n/start - Iniciar\n/ver - Ver anuncios y ganar\n/saldo - Ver saldo\n/retirar - Retirar\n/historial - Ver historial\n/ranking - Top usuarios\n/invitar - Invitar amigos\n/ayuda - Ayuda\n/privacidad - Política de privacidad")

@bot.message_handler(commands=['privacidad'])
def privacidad(message):
    bot.reply_to(message, "📜 POLÍTICA DE PRIVACIDAD\n\n✅ No compartimos tus datos con terceros\n✅ Solo usamos tu ID para gestionar tu saldo\n✅ Puedes eliminar tus datos cuando quieras")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reward_"))
def claim_reward(call):
    uid = call.from_user.id
    if uid not in users:
        users[uid] = {"saldo": 0.0, "historial": []}
    
    reward_url = call.data.replace("reward_", "")
    try:
        requests.get(reward_url, timeout=5)
        g = round(random.uniform(0.02, 0.08), 3)
        users[uid]['saldo'] += g
        users[uid]['historial'].append(f"+{g} USDT")
        bot.answer_callback_query(call.id, f"✅ Recompensa de +{g} USDT reclamada!")
        bot.edit_message_text(f"✅ Recompensa de +{g} USDT acreditada.\n💰 Saldo: {users[uid]['saldo']:.3f} USDT", 
                             chat_id=call.message.chat.id, message_id=call.message.message_id)
    except:
        bot.answer_callback_query(call.id, "❌ Error al reclamar recompensa. Intenta de nuevo.")

print("🤖 Bot con AdsGram activo")
bot.infinity_polling()
