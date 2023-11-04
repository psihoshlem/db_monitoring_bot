from telebot import types
import telebot

from config import BOT_TOKEN, ADMIN_PASSWORD

from functions import write_admin
from functions import get_data_json, get_statistic_chart
from functions import terminate_long_running_queries, get_average_execution_time_and_reset_stats

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
    else:
        bot.send_message(message.chat.id, text="На такую команду я не запрограммирован...")


def show_all_commands(message):
    button = telebot.types.InlineKeyboardButton('Показать все БД', callback_data='my_button')
    keyboard = telebot.types.InlineKeyboardMarkup().add(button)
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
    keyboard = create_inline_keyboard("show_bd_for_rebase")
    bot.send_message(message.chat.id, 'Выберите db', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'my_button')
def process_callback_button(call):
    keyboard = create_inline_keyboard("show_bd_for_info")
    bot.send_message(call.message.chat.id, 'Cписок всех бд', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('rebase_db'))
def process_callback_button(call):
    callback_data = call.data
    db_name = callback_data.split('-')[1]
    avarge_query_time = get_average_execution_time_and_reset_stats()
    bot.send_message(call.message.chat.id, text=f"Средняя продолжительность запросов: \n{avarge_query_time} секунд", parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data.startswith('avg_time'))
def process_callback_button(call):
    avarge_query_time = get_average_execution_time_and_reset_stats()
    bot.send_message(call.message.chat.id, text=f"Средняя продолжительность запросов: \n{avarge_query_time} секунд", parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data == 'fix_logs')
def show_logs(call):
    long_query = terminate_long_running_queries()
    if long_query:
        for pid, duration in long_query:
            bot.send_message(call.message.chat.id, f"✅ Прерван запрос <b>PID: </b>{pid}\n<b>Запрос выполнялся: </b>{duration}.", parse_mode="HTML")
    else:
        bot.send_message(call.message.chat.id, "✅ Все запросы остановлены")


@bot.callback_query_handler(func=lambda call: call.data.startswith('show_all_db'))
def process_callback(call):
    callback_data = call.data
    db_name = callback_data.split('-')[1]
    check_graf = telebot.types.InlineKeyboardButton('Графики', callback_data=f'check_graf-{db_name}')
    configuration = telebot.types.InlineKeyboardButton('Конфигурация', callback_data=f'configuration-{db_name}')
    avg_time = telebot.types.InlineKeyboardButton('Средняя продолжительность', callback_data=f'avg_time')
    keyboard = telebot.types.InlineKeyboardMarkup().add(check_graf, configuration)
    keyboard.row(avg_time)
    bot.send_message(call.message.chat.id, f"<b>db:</b> {db_name}\n<b>Сессии lwlock:</b> ?\n<b>Активные сессии:</b> ?\n<b>Процент загруженности буфера: ?</b>",reply_markup=keyboard, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data.startswith('check_graf'))
def process_callback_button(call):
    callback_data = call.data
    db_name = callback_data.split('-')[1]
    buf1, buf2 = get_statistic_chart(db_name)
    bot.send_photo(call.message.chat.id, photo=buf1, caption=db_name)
    bot.send_photo(call.message.chat.id, photo=buf2, caption=db_name)


@bot.callback_query_handler(func=lambda call: call.data.startswith('configuration'))
def process_callback_button(call):
    buttons = [
        types.InlineKeyboardButton('Время для сессий lwlock', callback_data='set_time-lwlock'),
        types.InlineKeyboardButton('Время для активных сессий', callback_data='set_time-activate'),
        types.InlineKeyboardButton('Время для процента загруженности буфера', callback_data='set_time-bufer')
    ]
    keyboard = telebot.types.InlineKeyboardMarkup()
    for button in buttons:
        keyboard.add(button)
    bot.send_message(call.message.chat.id, 'Установите время для метрик', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('set_time'))
def process_callback_button(call):
    callback_data = call.data
    conf_param = callback_data.split('-')[1]
    if conf_param == "lwlock":
        sent = bot.send_message(call.message.chat.id, 'Введите время для сессий lwlock')
        output_msg = "lwlock"
    elif conf_param == "activate":
        sent = bot.send_message(call.message.chat.id, 'Введите время для активных сессий')
        output_msg = "activate"
    elif conf_param == "bufer":
        sent = bot.send_message(call.message.chat.id, 'Введите время для процента загруженности буфера')
        output_msg = "bufer"
    bot.register_next_step_handler(sent, set_time_params)


def set_time_params(message):
    bot.send_message(message.chat.id, f'Выбранно время {message.text}')

def create_inline_keyboard(key_value):
    dbs = get_data_json()["databases"].keys()
    keyboard = types.InlineKeyboardMarkup()
    buttons = []
    if key_value == "show_bd_for_info":
        callback = "show_all_db"
    else:
        callback = "rebase_db"
    for db in dbs:
        callback_data = f"{callback}-{db}"
        btn = create_inline_button(db, callback_data)
        buttons.append(btn)
    for button in buttons:
        keyboard.row(button)
    return keyboard


def create_inline_button(text, data):
    return types.InlineKeyboardButton(text, callback_data=data)


if __name__=="__main__":
    bot.infinity_polling(timeout=10, long_polling_timeout=5)