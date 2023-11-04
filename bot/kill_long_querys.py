import psycopg2
import time

def terminate_long_running_queries():
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

    cur.execute("SELECT pid, now() - pg_stat_activity.query_start AS duration FROM pg_stat_activity WHERE state = 'active' AND now() - pg_stat_activity.query_start > interval '10 seconds';")
    long_running_queries = cur.fetchall()

    print("Проверка на задержку...")

    for query_info in long_running_queries:
        pid, duration = query_info
        print(f"Прерывание запроса с PID {pid}, который выполняется уже {duration}.")
        cur.execute(f"SELECT pg_terminate_backend({pid});")
        conn.commit()
        print(f"Запрос с PID {pid} прерван.")

    cur.close()
    conn.close()



terminate_long_running_queries()
