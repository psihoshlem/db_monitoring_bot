import psycopg2
import time

def provoke_delay_50_seconds():
    database_name = "test_db"
    user = "postgres"
    password = "1234"
    host = "localhost"
    port = "5432"

    conn = psycopg2.connect(
        dbname=database_name,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cur = conn.cursor()

    cur.execute("SELECT pg_sleep(50);")
    print("Задержка в 50 секунд")
    conn.commit()

    cur.close()
    conn.close()

provoke_delay_50_seconds()