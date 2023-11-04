import sqlite3
from config import DB_NAMES
from datetime import datetime, timedelta


def clear_db():
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    for table in tables:
        cur.execute(f"DROP TABLE {table[0]};")
    conn.commit()
    conn.close()

def create_tables():
    # clear_db()
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS databases(name text);")
    for table_name in [
        "active_sessions", "lwlock_sessions", "bg_processess"
    ]:
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {table_name}" +
            "(db_name text, value integer, date text);"
        )
    for db_name in DB_NAMES:
        cur.execute(f"INSERT INTO databases VALUES ('{db_name}')")
    conn.commit()
    cur.close() 

def write_metrics_value(db_name: str, table: str, value: str):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    now = datetime.now()
    last = get_last_record(table, db_name)
    last = datetime.strptime(last[0], '%Y-%m-%d %H:%M:%S.%f') if last else None
    if last == None or len(get_ten_last_records(table, db_name)) < 10:
        cur.execute(
            f"INSERT INTO '{table}' VALUES ('{db_name}', '{value}', '{now}');"
        )
    elif now - last > timedelta(minutes=5):
        cur.execute(
            f"INSERT INTO {table} VALUES ('{db_name}', '{value}', '{now}');"
        )
    conn.commit()
    cur.close() 


def get_last_record(table: str, db_name: str):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute(
        f"SELECT date FROM {table} "+
        f"WHERE db_name='{db_name}' "
        "ORDER BY date DESC LIMIT 1;"
    )
    row = cur.fetchone()
    cur.close()
    return row


def get_ten_last_records(table: str, db_name: str):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute(
        f"SELECT value FROM {table} "+
        f"WHERE db_name='{db_name}' "
        "ORDER BY date DESC LIMIT 10;"
    )
    rows = cur.fetchall()
    cur.close()
    return [row[0] for row in rows]


create_tables()
# print(get_last_record("active_sessions", "test_db"))