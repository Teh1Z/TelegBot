# -*- coding: utf-8 -*-
from io import BytesIO, StringIO

import requests
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from logic import build_table, OPS
from matrix import det


r = requests.get('https://www.meme-arsenal.com/memes/ddcf6ef709b8db99da11efd281abd990.jpg')
MEM_IMAGE = BytesIO(r.content)  # BytesIO creates file-object from bytes string

# generate supported operators description
ops_description = '\n'.join([f'<b>{op}</b> {op_data[3]}' for op, op_data in OPS.items()])


with open('token.txt') as tk:
    bot = telebot.TeleBot(tk.read().strip())


menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)  # this markup is bot menu
menu.add(KeyboardButton('/logic'))
menu.add(KeyboardButton('/matrix'))
menu.add(KeyboardButton('помощь'))


hide_menu = ReplyKeyboardRemove()  # sending this as reply_markup will close menu


@bot.message_handler(commands=['start'])
def start_message(message):
    send_mess = (f'<b>Привет, {message.from_user.first_name} {message.from_user.last_name}!</b>\n'
                 f'Используй клавиатуру или команды для вызова нужной фишки\n'
                 f'/help - вызов помощи')
    sent_value = bot.send_message(message.chat.id, send_mess, parse_mode='html', reply_markup=menu)
    bot.register_next_step_handler(sent_value, if_command)


def if_command(message):
    bot.send_message(message.chat.id, "Введите корректную команду")


@bot.message_handler(regexp='помощь|help')
def word_help(message):
    send_help(message)  # redirect this question to send_help


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id,
                     ('/matrix для нахождения определителя матрицы.\n'
                      '/logic для построения таблицы истинности логического выражения.\n'
                      'Описание допустимых логических операторов:\n'
                      f'{ops_description}'),
                     parse_mode='html')


@bot.message_handler(commands=['matrix', 'det'])
def matrix_input(message):
    send_matrix = bot.send_message(message.chat.id, 'Введите матрицу: (одним сообщением)', reply_markup=hide_menu)
    bot.register_next_step_handler(send_matrix, matrix_output)


def matrix_output(message):
    try:
        matrix = [[float(x) for x in row.split()] for row in message.text.split('\n')]
        answer = det(matrix)
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, 'Необходимо вводить числовую квадратную матрицу', reply_markup=menu)
    else:
        bot.send_message(message.chat.id, str(answer), reply_markup=menu)


@bot.message_handler(commands=['logic', 'exp'])
def logic_input(message):
    send_logic = bot.send_message(message.chat.id, 'Введите логическое выражение:', reply_markup=hide_menu)
    bot.register_next_step_handler(send_logic, logic_output)


def logic_output(message):
    try:
        table, variables = build_table(message.text)
        out = StringIO()  # abstract file (file-object)
        print(*variables, 'F', file=out, sep=' '*2)
        for row in table:
            print(*row, file=out, sep=' '*2)
        bot.send_message(message.chat.id, f'<code>{out.getvalue()}</code>', parse_mode='html', reply_markup=menu)
    except (AttributeError, SyntaxError):
        bot.send_message(message.chat.id, "Ошибка ввода данных", reply_markup=menu)


@bot.message_handler(regexp='ахуеть')  # отдельный хендлер картинки
def get_text_messages(message):
    bot.send_photo(message.chat.id, MEM_IMAGE)


bot.polling(none_stop=True)
