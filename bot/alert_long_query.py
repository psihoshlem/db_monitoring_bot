import psycopg2
import time

def track_long_running_queries():
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

    cur.execute("SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE state = 'active' AND now() - pg_stat_activity.query_start > interval '10 seconds';")
    long_running_queries = cur.fetchall()

    print("Отслеживание длинных запросов...")

    for query_info in long_running_queries:
        pid, duration, query = query_info
        print(f"Длинный запрос с PID {pid} выполняется уже {duration}.")
        print(f"Запрос: {query}\n")

    cur.close()
    conn.close()

def main_function():
    duration = 120
    interval = 10

    while duration > 0:
        track_long_running_queries()
        time.sleep(interval)
        duration -= interval

if __name__ == "__main__":
    main_function()
