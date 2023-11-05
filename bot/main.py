from telebot import types
import telebot

from config import BOT_TOKEN, ADMIN_PASSWORD

from functions import get_statistic_chart, get_lwlock_count, get_active_sessions
from functions import terminate_long_running_queries, get_average_execution_time_and_reset_stats
from shutdown_db import stop_postgresql_with_backup
from start_db import start_postgresql_with_restore
from restart_db import backup_and_restart_postgresql

from data_funcs import get_databases, add_admin, change_stats_check_time

bot = telebot.TeleBot(BOT_TOKEN)
const_for_send_msg = True

message_for_delete = []

@bot.message_handler(commands=['start'])
def start(message):
    sent = bot.send_message(message.chat.id, f'Привет, <b>{message.from_user.first_name}</b>! Введите пароль для входа в систему', parse_mode="HTML")
    bot.register_next_step_handler(sent, check_login)


@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == "Подробная информация по БД":
        show_all_commands(message)
    elif message.text == "Перезагрузить БД":
        rebase_db(message)
    elif message.text == "Выключить БД":
        off_db(message)
    elif message.text == "Включить БД":
        on_db(message)
    else:
        bot.send_message(message.chat.id, text="На такую команду я не запрограммирован...")


def show_all_commands(message):
    keyboard = create_inline_keyboard("show_bd_for_info")
    msg_info = bot.send_message(message.chat.id, 'Выберите нужную базу данных', reply_markup=keyboard)
    global message_for_delete
    message_for_delete = msg_info


def warning_session_message(id, number):
    fix_button = telebot.types.InlineKeyboardButton('Починить', callback_data='fix_logs')
    keyboard = telebot.types.InlineKeyboardMarkup().add(fix_button)
    bot.send_message(id, f'Чиним БД {number}', reply_markup=keyboard)


def warning_long_query_message(id, pid, number, query):
    fix_button = telebot.types.InlineKeyboardButton('🔧 Устранить', callback_data='fix_logs')
    keyboard = telebot.types.InlineKeyboardMarkup().add(fix_button)
    bot.send_message(
        id,
        f'⚠️ <b>Выполняется слишком долгий запрос:</b>\n<b>PID: </b>{pid}\n<b>Время запроса: </b>{number}\n<b>Имя запроса:</b>{query}', 
        reply_markup=keyboard, parse_mode="HTML"
    )


def check_login(message):
    if message.text == ADMIN_PASSWORD:
        global message_for_delete
        message_for_delete = message
        delete_or_edit_msg()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Выключить БД")
        btn2 = types.KeyboardButton("Перезагрузить БД")
        btn3 = types.KeyboardButton("Включить БД")
        btn4 = types.KeyboardButton("Подробная информация по БД")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, 'Вход успешен', reply_markup=markup)
        add_admin(message.chat.id)
    else:
        sent = bot.send_message(message.chat.id, 'Пароль неверен, введите ещё раз')
        bot.register_next_step_handler(sent, check_login)


def rebase_db(message):
    keyboard = create_inline_keyboard("show_bd_for_rebase")
    msg_info = bot.send_message(message.chat.id, 'Какую БД будем перезагружать?', reply_markup=keyboard)
    global message_for_delete
    message_for_delete = msg_info


def off_db(message):
    keyboard = create_inline_keyboard("show_bd_for_off")
    msg_info = bot.send_message(message.chat.id, 'Какую БД будем выключать?', reply_markup=keyboard)
    global message_for_delete
    message_for_delete = msg_info


def on_db(message):
    keyboard = create_inline_keyboard("show_bd_for_on")
    msg_info = bot.send_message(message.chat.id, 'Какую БД будем включать?', reply_markup=keyboard)
    global message_for_delete
    message_for_delete = msg_info


def delete_or_edit_msg():
    bot.delete_message(message_for_delete.chat.id, message_for_delete.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('avg_time'))
def process_callback_button(call):
    avarge_query_time = get_average_execution_time_and_reset_stats()
    bot.send_message(call.message.chat.id, text=f"Средняя продолжительность запросов: \n{avarge_query_time} секунд", parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data == 'fix_logs')
def show_logs(call):
    long_query = terminate_long_running_queries()
    if long_query:
        for pid, duration in long_query:
            bot.send_message(
                call.message.chat.id, f"✅ Прерван запрос <b>PID: </b>{pid}\n<b>Запрос выполнялся: </b>{duration}.",
                parse_mode="HTML"
            )
    else:
        bot.send_message(call.message.chat.id, "✅ Все запросы остановлены")


@bot.callback_query_handler(func=lambda call: call.data.startswith('show_all_db'))
def process_callback(call):
    delete_or_edit_msg()
    callback_data = call.data
    db_name = callback_data.split('-')[1]
    check_graf = telebot.types.InlineKeyboardButton('Графики', callback_data=f'check_graf-{db_name}')
    configuration = telebot.types.InlineKeyboardButton('Конфигурация', callback_data=f'configuration-{db_name}')
    avg_time = telebot.types.InlineKeyboardButton('Средняя продолжительность', callback_data=f'avg_time')
    keyboard = telebot.types.InlineKeyboardMarkup().add(check_graf, configuration)
    keyboard.row(avg_time)
    bot.send_message(
        call.message.chat.id,
        f"<b>db:</b> {db_name}\n" +
        f"<b>Сессии lwlock: </b> {get_lwlock_count()}\n" +
        f"<b>Активные сессии:</b> {get_active_sessions()}\n" +
        f"<b>Процент загруженности буфера: -</b>",
        reply_markup=keyboard, parse_mode="HTML"
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('check_graf'))
def process_callback_button(call):
    callback_data = call.data
    db_name = callback_data.split('-')[1]
    buttons = [
        types.InlineKeyboardButton('Сессии lwlock', callback_data=f'print_graf-lwlock_sessions-{db_name}'),
        types.InlineKeyboardButton('Активные сессии', callback_data=f'print_graf-active_sessions-{db_name}'),
        #types.InlineKeyboardButton('Процент загруженности буфера', callback_data=f'print_graf-bufer-{db_name}'),
        #types.InlineKeyboardButton('Средняя продолжительность запроса', callback_data=f'print_graf-avg-{db_name}')
    ]
    keyboard = telebot.types.InlineKeyboardMarkup()
    for button in buttons:
        keyboard.add(button)
    msg_info = bot.send_message(call.message.chat.id, 'Выберите график для вывода', reply_markup=keyboard)
    global message_for_delete
    message_for_delete = msg_info


@bot.callback_query_handler(func=lambda call: call.data.startswith('print_graf'))
def process_callback_button(call):
    delete_or_edit_msg()
    callback_data = call.data
    graf_name = callback_data.split('-')[1]
    db_name = callback_data.split('-')[2]
    buf = get_statistic_chart(graf_name, db_name)
    bot.send_photo(call.message.chat.id, photo=buf, caption=db_name)


@bot.callback_query_handler(func=lambda call: call.data.startswith('rebase_db'))
def process_callback_button(call):
    delete_or_edit_msg()
    callback_data = call.data
    db_name = callback_data.split('-')[1]

    restart_bd_message = backup_and_restart_postgresql(db_name)
    bot.send_message(call.message.chat.id, text=f"База данных <b>{restart_bd_message}</b> успешно выключена, скопирована и включена", parse_mode="HTML")



@bot.callback_query_handler(func=lambda call: call.data.startswith('off_db'))
def process_callback_button(call):
    delete_or_edit_msg()
    callback_data = call.data
    db_name = callback_data.split('-')[1]

    stop_bd_message = stop_postgresql_with_backup(db_name)
    bot.send_message(call.message.chat.id, text=f"База данных <b>{stop_bd_message}</b> успешно выключена и данные сохранены.", parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data.startswith('on_db'))
def process_callback_button(call):
    delete_or_edit_msg()
    callback_data = call.data
    db_name = callback_data.split('-')[1]

    start_bd_message = start_postgresql_with_restore(db_name)
    bot.send_message(call.message.chat.id, text=f"База данных {start_bd_message} успешно включена с восстановлением данных.", parse_mode="HTML")


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
    msg_info = bot.send_message(call.message.chat.id, 'Установите время для метрик', reply_markup=keyboard)
    global message_for_delete
    message_for_delete = msg_info


@bot.callback_query_handler(func=lambda call: call.data.startswith('set_time'))
def process_callback_button(call):
    delete_or_edit_msg()
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
    number_time = int(message.text)
    change_stats_check_time(number_time)
    bot.send_message(message.chat.id, f'Выбранно время <b>{message.text}</b>', parse_mode="HTML")


def create_inline_keyboard(key_value):
    dbs = get_databases()
    keyboard = types.InlineKeyboardMarkup()
    buttons = []
    if key_value == "show_bd_for_info":
        callback = "show_all_db"
    elif key_value == "show_bd_for_rebase":
        callback = "rebase_db"
    elif key_value == "show_bd_for_off":
        callback = "off_db"
    elif key_value == "show_bd_for_on":
        callback = "on_db"
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
