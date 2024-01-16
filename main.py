import random

import telebot
from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage

import sqlite3

from random import choice

from hashlib import md5

import string

from api_token import API_TOKEN

ally = string.digits + string.ascii_uppercase + string.ascii_lowercase + string.punctuation


def generator_password(len_password, password=''):
    password += choice(string.ascii_uppercase)
    for _ in range(len_password - 1):
        password += choice(ally)
    if not (any(digit in password for digit in string.digits)):
        index_digit = random.randint(0, len_password)
        digit = random.choice(string.digits)
        password = list(password)
        password.pop(index_digit)
        password.insert(index_digit, digit)
        password = ''.join(password)
    return password


state_storage = StateMemoryStorage()

bot = telebot.TeleBot(API_TOKEN, state_storage=state_storage)


class MyState(StatesGroup):
    len_password = State()
    password = State()


class Db:

    def __init__(self, chat_id):
        self.chat_id = chat_id

    def create(self):
        with sqlite3.connect('Passwords.db') as db:
            cursor = db.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS password(
            ig INTEGER PRIMARY KEY AUTOINCREMENT,
            id_tg INTEGER UNIQUE,
            password TEXT UNIQUE
            )""")
            db.commit()
            try:
                cursor.execute(f"INSERT INTO password (id_tg) VALUES ({self.chat_id})")
            except sqlite3.IntegrityError:
                cursor.execute(f"UPDATE password SET id_tg = {self.chat_id} WHERE id_tg = {self.chat_id}")
            finally:
                db.commit()

    def insert_password(self, password):
        password = md5(password.encode())
        with sqlite3.connect('Passwords.db') as db:
            cursor = db.cursor()
            cursor.execute(
                f"UPDATE password SET password = '{password.hexdigest()}' WHERE id_tg = {self.chat_id}")
            db.commit()


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    create_table = Db(message.chat.id)
    create_table.create()

    markup = telebot.types.InlineKeyboardMarkup()
    bt_start = telebot.types.InlineKeyboardButton('Начать', callback_data='ready')
    markup.add(bt_start)

    bot.send_message(message.chat.id, 'Привет! Я помогу тебе сгенерировать пароль 🔑', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['ready', 'new_password'])
def callback_1(call: telebot.types.CallbackQuery):
    bot.set_state(call.from_user.id, MyState.len_password, call.message.chat.id)

    bot.send_message(call.message.chat.id, 'Введи желаемую длину пароля (длина пароля не меньше 8 символов) 💬')


@bot.message_handler(state=MyState.len_password)
def generator(message: telebot.types.Message):
    if message.text.isdigit() and int(message.text) >= 8:
        markup = telebot.types.InlineKeyboardMarkup()
        bt_password = telebot.types.InlineKeyboardButton('Сгенерировать новый пароль', callback_data='new_password')
        markup.add(bt_password)

        password = generator_password(int(message.text))

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['password'] = password
            bot.send_message(message.chat.id, f'<b>Сгенерированный пароль:</b> <code>{data['password']}</code> 🎁',
                             reply_markup=markup, parse_mode='html')

        add_password = Db(message.chat.id)
        add_password.insert_password(password)

        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Необходимо ввести целое число (длина пароля не меньше 8 символов) ❌')


@bot.message_handler(content_types=['text'])
def error_message(message: telebot.types.Message):
    bot.send_message(message.chat.id, 'Неверная команда 🚫')


if __name__ == '__main__':
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.add_custom_filter(custom_filters.IsDigitFilter())

    bot.infinity_polling()
