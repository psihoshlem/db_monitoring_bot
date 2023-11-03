import psycopg2
from config import (
    db_name,
    db_user,
    db_password,
    db_host,
    db_port
)

conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port
)


def get_pg_stat_activity():
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM pg_stat_activity;")
        result = cur.fetchall()
        for row in result:
            print(row)



def get_lwlock():
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM pg_stat_activity" +
            " WHERE wait_event_type = 'LWLock';"
        )
        result = cur.fetchall()
        return result[0][0]

print(get_lwlock())
# get_pg_stat_activity()
