from config import BOT_TOKEN
import telebot
from telebot import types

bot = telebot.TeleBot(BOT_TOKEN)
const_for_send_msg = True


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, text="Привет, <b>{0.first_name}</b>!".format(message.from_user), reply_markup=button_for_start(), parse_mode="HTML")


@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == "Вход в систему":
        button_for_auth(message)
    elif message.text == "Cписок команд":
        show_all_commands(message)
    elif message.text == "Спровоцировать ошибку":
        error_msg(message)
    else:
        bot.send_message(message.chat.id, text="На такую команду я не запрограммирован...")


def show_all_commands(message):
    button = telebot.types.InlineKeyboardButton('Показать все БД', callback_data='my_button')
    button2 = telebot.types.InlineKeyboardButton('Логи последней ошибки', callback_data='my_button')
    keyboard = telebot.types.InlineKeyboardMarkup().add(button, button2)
    bot.send_message(message.chat.id, 'Cписок команд', reply_markup=keyboard)


def button_for_start():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Вход в систему")
    markup.add(btn1)
    return markup


def button_for_auth(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    exit_btn = types.KeyboardButton('Выход')
    markup.add(exit_btn)
    sent = bot.send_message(message.chat.id, 'Введите пароль для входа в систему', reply_markup=markup)
    bot.register_next_step_handler(sent, check_login)


def error_msg(message):
    check_logs = types.InlineKeyboardButton('Посмотреть логи', callback_data='check_logs')
    markup = types.InlineKeyboardMarkup().add(check_logs)
    bot.send_message(message.chat.id, 'Ошибка!\nБД-1', reply_markup=markup)

def check_login(message):
    if message.text == 'admin':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Профиль")
        btn2 = types.KeyboardButton("Cписок команд")
        bth3 = types.KeyboardButton("Спровоцировать ошибку")
        markup.add(btn1, btn2, bth3)
        bot.send_message(message.chat.id, 'Вход успешен', reply_markup=markup)
    else:
        sent = bot.send_message(message.chat.id, 'Пароль неверен, введите ещё раз')
        bot.register_next_step_handler(sent, check_login)


@bot.callback_query_handler(func=lambda call: call.data == 'my_button')
def process_callback_button(call):
    keyboard = create_inline_keyboard(5)
    bot.send_message(call.message.chat.id, 'Cписок всех бд', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'check_logs')
def show_logs(call):
    bot.send_message(call.message.chat.id, 'logs: накрылось чета-чета')


@bot.callback_query_handler(func=lambda call: call.data.startswith('button_'))
def process_callback(call):
    button_number = call.data.split('_')[1]
    bot.send_message(call.message.chat.id, 'БД = {}'.format(button_number))


def create_inline_keyboard(amount):
    keyboard = types.InlineKeyboardMarkup()
    buttons = []
    for i in range(amount):
        button_number = i + 1
        button_text = f'Button {button_number}'
        button_data = f'button_{button_number}'
        button = create_inline_button(button_text, button_data)
        buttons.append(button)
    keyboard.add(*buttons)
    return keyboard

def create_inline_button(text, data):
    return types.InlineKeyboardButton(text, callback_data=data)


bot.infinity_polling(timeout=10, long_polling_timeout=5)