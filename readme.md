# Umom Мониторинг

Наше программное решение "UmomМониторинг" представляет собой систему мониторинга и управления базой данных PostgreSQL с помощью Telegram бота. Бот предоставляет возможность отслеживать состояние базы данных, получать уведомления об ошибках и проблемах, а также запускать скрипты для их исправления.
### пароль для входа admin

## Запуск с докером

Вы можете использовать докер для запуска базы данных:
```bash
$ git clone https://github.com/psihoshlem/db_monitoring_bot.git
$ cd db_monitoring_bot
$ docker-compose up -d
```

## Запуск бота

```bash
$ git clone https://github.com/psihoshlem/db_monitoring_bot.git
$ cd db_monitoring_bot/bot
$ pyhon main.py
```
```bash
$ cd db_monitoring_bot/bot
$ pyhon db_checker.py
```