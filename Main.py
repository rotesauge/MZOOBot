from conf import TOKEN,ADMIN_ID
from handlers import *
import telebot


Base.metadata.create_all(bind=engine)
bot = telebot.TeleBot(TOKEN)

"""
Params:
chat_id – Unique identifier for the target chat or username of the target channel (in the format @channelusername)
text – Text of the message to be sent
parse_mode – Mode for parsing entities in the message text.
entities – List of special entities that appear in message text, which can be specified instead of parse_mode
disable_web_page_preview – deprecated.
disable_notification – Sends the message silently. Users will receive a notification with no sound.
protect_content – Protects the contents of the sent message from forwarding and saving
reply_to_message_id – deprecated.
allow_sending_without_reply – deprecated.
reply_markup – Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
timeout – Timeout in seconds for the request.
message_thread_id – Identifier of a message thread, in which the message will be sent
reply_parameters – Reply parameters.
link_preview_options – Link preview options.
business_connection_id – Identifier of a business connection, in which the message will be sent
message_effect_id – Unique identifier of the message effect to be added to the message; for private chats only
allow_paid_broadcast – Pass True to allow up to 1000 messages per second, ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message. The relevant Stars will be withdrawn from the bot's balance
"""

@bot.message_handler(commands=['start','help','вернуться в гдавное меню'])
def begin(message: telebot.types.Message):
    start_help_handler(message,bot)

@bot.message_handler(commands=['message'])
def begin(message: telebot.types.Message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id,message)

@bot.message_handler(content_types=['text'])
def converter(message: telebot.types.Message):
    text_handler(message,bot)

@bot.message_handler(content_types=['photo', 'video', 'document', 'audio', 'sticker', 'animation', 'voice'])
def say_lmao(message: telebot.types.Message):
        bot.reply_to(message, 'Неверный тип данных!')

bot.polling(none_stop=True)
