from config import BOT_TOKEN, ADMIN_PASSWORD
import telebot
from telebot import types
from functions import write_admin
import json
from functions import terminate_long_running_queries

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
    elif message.text == "Обновить БД":
        rebase_db(message)
    # elif message.text == "Спровоцировать ошибку":
    #     error_msg(message)
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


def warning_session_message(id, number):
    fix_button = telebot.types.InlineKeyboardButton('Починить', callback_data='fix_logs')
    keyboard = telebot.types.InlineKeyboardMarkup().add(fix_button)
    bot.send_message(id, f'Чиним БД {number}', reply_markup=keyboard)


def warning_long_query_message(id, pid, number, query):
    fix_button = telebot.types.InlineKeyboardButton('🔧 Устранить', callback_data='fix_logs')
    keyboard = telebot.types.InlineKeyboardMarkup().add(fix_button)
    bot.send_message(id, f'⚠️ <b>Выполняется слишком долгий запрос:</b>\n<b>PID: </b>{pid}\n<b>Время запроса: </b>{number}\n<b>Имя запроса:</b>{query}', reply_markup=keyboard, parse_mode="HTML")


def check_login(message):
    if message.text == ADMIN_PASSWORD:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Обновить БД")
        btn2 = types.KeyboardButton("Cписок команд")
        # bth3 = types.KeyboardButton("Спровоцировать ошибку")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, 'Вход успешен', reply_markup=markup)
        write_admin(message.chat.id)
    else:
        sent = bot.send_message(message.chat.id, 'Пароль неверен, введите ещё раз')
        bot.register_next_step_handler(sent, check_login)


def rebase_db(message):
    print("DROP DATABASE")
    # Подключение к базе данных
    # conn = psycopg2.connect(
    #     dbname="название_базы_данных",
    #     user="имя_пользователя",
    #     password="пароль",
    #     host="хост",
    #     port="порт"
    # )
    # Создание объекта курсора
    # cur = conn.cursor()
    # try:
        # Остановка активных сеансов базы данных
        # cur.execute("SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'название_базы_данных';")
        # conn.commit()
        # Удаление и создание базы данных
        # cur.execute("DROP DATABASE IF EXISTS название_базы_данных;")
        # cur.execute("CREATE DATABASE название_базы_данных;")
        # conn.commit()
        # Восстановление базы данных из резервной копии
    #     cur.execute("pg_restore --dbname=название_базы_данных --verbose путь_к_резервной_копии")
    #     conn.commit()
    # except (Exception, psycopg2.DatabaseError) as error:
    #     print("Ошибка при восстановлении базы данных:", error)
    # finally:
        # Закрытие соединения и курсора
        # if conn is not None:
        #     conn.close()
        # if cur is not None:
        #     cur.close()


@bot.callback_query_handler(func=lambda call: call.data == 'my_button')
def process_callback_button(call):
    keyboard = create_inline_keyboard()
    bot.send_message(call.message.chat.id, 'Cписок всех бд', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'fix_logs')
def show_logs(call):
    long_query = terminate_long_running_queries()
    if long_query:
        for pid, duration in long_query:
            bot.send_message(call.message.chat.id, f"✅ Прерван запрос <b>PID: </b>{pid}\n<b>Запрос выполнялся: </b>{duration}.", parse_mode="HTML")
    else:
        bot.send_message(call.message.chat.id, "✅ Все запросы остановлены")
        # f"Прерывание запроса с PID {pid}, который выполняется уже {duration}.


@bot.callback_query_handler(func=lambda call: call.data.startswith('test_db'))
def process_callback(call):
    button_number = call.data
    bot.send_message(call.message.chat.id, 'БД = {}'.format(button_number))


def create_inline_keyboard():
    with open("data.json", "r") as file:
        dbs = json.loads(file.read())["databases"]
    keyboard = types.InlineKeyboardMarkup()
    buttons = []
    for db in dbs:
        btn = create_inline_button(db, db)
        buttons.append(btn)
    for button in buttons:
        keyboard.row(button)
    return keyboard

def create_inline_button(text, data):
    return types.InlineKeyboardButton(text, callback_data=data)

if __name__=="__main__":
    bot.infinity_polling(timeout=10, long_polling_timeout=5)