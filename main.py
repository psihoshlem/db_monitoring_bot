from config import BOT_TOKEN
import telebot
from telebot import types
import requests

bot = telebot.TeleBot(BOT_TOKEN)
const_for_send_msg = True


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Вход в систему")
    markup.add(btn1)
    bot.send_message(message.chat.id, text="Привет, <b>{0.first_name}</b>!".format(message.from_user), reply_markup=markup, parse_mode="HTML")

@bot.message_handler(content_types=['text'])
def func(message):
    global const_for_send_msg
    if(message.text == "Вход в систему"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        exit = types.KeyboardButton('Выход')
        markup.add(exit)
        sent = bot.send_message(message.chat.id, 'Введите пароль для входа в систему', reply_markup=markup)
        bot.register_next_step_handler(sent, check_login)
    elif(message.text == "Cписок команд"):
        show_all_comands(message)
    else:
        bot.send_message(message.chat.id, text="На такую комманду я не запрограммирован...")


def check_login(message):
        if message.text == 'admin':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Профиль")
            btn2 = types.KeyboardButton("Cписок команд")
            markup.add(btn1, btn2)
            bot.send_message(message.chat.id, 'Вход успешен', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Пароль неверен')

@bot.callback_query_handler(func=lambda call: call.data == 'my_button')
def process_callback_button(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, 'Cписок всех бд', reply_markup=test_add_db_list([4]))

@bot.callback_query_handler(func=lambda call: call.data == 'check_db')
def check_test(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, 'Информация по db')


def show_all_comands(message):
    button = telebot.types.InlineKeyboardButton('Показать все БД', callback_data='my_button')
    button2 = telebot.types.InlineKeyboardButton('Логи последней ошибки', callback_data='my_button')
    keyboard = telebot.types.InlineKeyboardMarkup().add(button, button2)
    bot.send_message(message.chat.id, 'Cписок команд', reply_markup=keyboard)

def test_add_db_list(number):
    for item in number:
        button = telebot.types.InlineKeyboardButton('db{}'.format(item), callback_data='check_db')
        keyboard = telebot.types.InlineKeyboardMarkup().add(button)
    return keyboard

bot.infinity_polling(timeout=10, long_polling_timeout = 5)

# при первом запуске спрашивает пароль
# если ок то выходит список команд (показать все базы данных)
# показать все базы данных