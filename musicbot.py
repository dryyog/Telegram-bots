import telebot
import config
import time
import os
from SQLighter import SQLighter
import utils
import random
from telebot import types

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['game'])
def game(message):
    db_worker = SQLighter(config.database_name)
    row = db_worker.select_single(random.randint(1, utils.get_rows_count()))
    markup = utils.generate_markup(row[2], row[3])
    bot.send_voice(message.chat.id, row[1], reply_markup=markup)
    utils.set_user_game(message.chat.id, row[2])
    db_worker.close()

@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer(message):
    answer = utils.get_answer_for_user(message.chat.id)
    if not answer:
        bot.send_message(message.chat.id, 'To start the game, select a command /game')
    else:
        keyboard_hider = types.ReplyKeyboardRemove()
        if message.text == answer:
            bot.send_message(message.chat.id, 'Right!', reply_markup=keyboard_hider)
        else:
            bot.send_message(message.chat.id, 'Alas, you didnt guess. Try it again!', reply_markup=keyboard_hider)
        utils.finish_user_game(message.chat.id)     

@bot.message_handler(commands=['test'])
def find_file_ids(message):
    for file in os.listdir('music/'):
        if file.split('.')[-1] == 'ogg':
            f = open('music/'+file, 'rb')
            msg = bot.send_voice(message.chat.id, f, None)
            bot.send_message(message.chat.id, msg.voice.file_id, reply_to_message_id=msg.message_id)
        time.sleep(3)

if __name__ == '__main__':
    utils.count_rows()
    random.seed()
    bot.infinity_polling()