import telebot

from db_utils import user_register
from cfg import TG_TOKEN

API_TOKEN = TG_TOKEN

bot = telebot.TeleBot(API_TOKEN)


# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'хуярт')
    user_info = {
        'user_id': message.from_user.id,
        'user_first_name': message.from_user.first_name,
        'user_last_name': message.from_user.last_name}
    user_register(user_info)


bot.infinity_polling()
