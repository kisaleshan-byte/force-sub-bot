import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🚨 ඔයාගේ විස්තර මෙතනට විතරක් දාන්න
BOT_TOKEN = "8623321692:AAHHtt_ecypUdfvZIyN5BRnCoyyr43FUK2Y"
CHANNEL_USERNAME = "@linkgicsrilanka"
ADMIN_ID = 7189706919  # 🚨 ඔයාගේ ටෙලිග්‍රෑම් Chat ID එක මෙතනට දාන්න (බොට්ගෙන් ලින්ක් ගන්න පුළුවන් ඔයාට විතරක් වෙන්න)

bot = telebot.TeleBot(BOT_TOKEN)

# ෆයිල් තාවකාලිකව සේව් කරගන්න තැනක් (Memory Database)
file_database = {}
file_counter = 1000

# පරිශීලකයා චැනල් එකේ ඉන්නවාද බලන කෑල්ල
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

# /start ලින්ක් එකක් ක්ලික් කරන් ආවාම වෙන දේ
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    text = message.text.split()
    
    # සාමාන්‍යයෙන් බොට්ව ස්ටාර්ට් කරොත්
    if len(text) == 1:
        bot.send_message(message.chat.id, "👋 සාදරයෙන් පිළිගන්නවා! මම ෆයිල් ස්ටෝර් බොට් කෙනෙක්.")
        return

    # ලින්ක් එකක් හරහා ආවොත් (උදා: /start file_1001)
    file_id_key = text[1]
    
    if is_subscribed(user_id):
        # චැනල් එකේ ඉන්නවා නම් ෆයිල් එක දෙනවා
        send_stored_file(message.chat.id, file_id_key)
    else:
        # චැනල් එකේ නැත්නම් බලෙන් Join කරවනවා
        markup = InlineKeyboardMarkup()
        join_btn = InlineKeyboardButton("📢 Join Our Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")
        # මෙතන callback_data එකට අර ෆයිල් කෝඩ් එකත් එකතු කරනවා පස්සේ දෙන්න
        check_btn = InlineKeyboardButton("🔄 Check / Done", callback_data=f"check_{file_id_key}")
        
        markup.add(join_btn)
        markup.add(check_btn)
        
        bot.send_message(
            message.chat.id, 
            "⚠️ මෙම ෆයිල් එක ලබා ගැනීමට පෙර කරුණාකර අපගේ චැනල් එකට එකතු වී 'Check / Done' බටන් එක ඔබන්න!", 
            reply_markup=markup
        )

# 'Check / Done' බටන් එක එබුවම
@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def check_callback(call):
    user_id = call.from_user.id
    file_id_key = call.data.replace("check_", "")
    
    if is_subscribed(user_id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_stored_file(call.message.chat.id, file_id_key)
    else:
        bot.answer_callback_query(call.id, "❌ ඔයා තාමත් චැනල් එකට Join වුණේ නැහැ!", show_alert=True)

# ෆයිල් එක යවන ක්‍රියාවලිය
def send_stored_file(chat_id, file_key):
    if file_key in file_database:
        file_data = file_database[file_key]
        bot.send_document(chat_id, file_data['file_id'], caption=file_data['caption'])
    else:
        bot.send_message(chat_id, "❌ කණගාටුයි, මෙම ලින්ක් එක වලංගු නැත හෝ මකා දමා ඇත.")

# 👑 ඇඩ්මින් (ඔයා) බොට් වෙත ෆයිල් එකක් එවූ විට ලින්ක් එකක් සාදා දීම
@bot.message_handler(content_types=['document', 'video', 'audio'])
def handle_admin_files(message):
    global file_counter
    # එවන්නේ ඔයාමද කියලා චෙක් කරනවා
    if message.from_user.id == ADMIN_ID:
        file_id = message.document.file_id if message.document else (message.video.file_id if message.video else message.audio.file_id)
        caption = message.caption if message.caption else ""
        
        # ඩේටාබේස් එකට සේව් කිරීම
        file_key = f"file_{file_counter}"
        file_database[file_key] = {'file_id': file_id, 'caption': caption}
        file_counter += 1
        
        # ඔයාට ලින්ක් එක හදලා දෙනවා
        bot_info = bot.get_me()
        share_link = f"https://t.me/{bot_info.username}?start={file_key}"
        
        bot.reply_to(message, f"✅ ෆයිල් එක සේව් වුණා!\n\n🔗 මෙන්න වීඩියෝ එකේ දාන්න ඕනේ ලින්ක් එක:\n`{share_link}`", parse_mode="Markdown")

print("File Store + Force Sub Bot වැඩ...")
bot.infinity_polling()