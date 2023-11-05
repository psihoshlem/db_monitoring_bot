import psycopg2
import json
import matplotlib.pyplot as plt
import io
from data_funcs import get_ten_last_records
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


def get_active_sessions() -> int:
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT numbackends FROM pg_stat_database " +
            "WHERE datname = 'test_db';"
        )
        result = cur.fetchone()
        return result[0]


def get_lwlock_count() -> int:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM pg_stat_activity" +
            " WHERE wait_event_type = 'LWLock';"
        )
        result = cur.fetchall()
        return result[0][0]


def get_the_longest_query():
    with conn.cursor() as cur:
        cur.execute(
            "SELECT query, total_exec_time FROM pg_stat_statements " +
            "ORDER BY total_exec_time DESC LIMIT 1;"
        )
        query, exec_time = cur.fetchone()
    return query, exec_time

def is_above_avg(exec_time: int):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT sum(total_exec_time) AS average_execution_time" + 
            " FROM pg_stat_statements;"
        )
        sum_time = cur.fetchone()[0] - exec_time
        cur.execute(
            "SELECT sum(calls) AS total_calls " + 
            "FROM pg_stat_statements;"
        )
        all_count = int(cur.fetchone()[0]) - 1
    return exec_time > (sum_time/all_count)*1000


def terminate_process(id: int):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT pg_terminate_backend(pid)" + 
            f" FROM pg_stat_activity WHERE pid = {id};"
        )


def track_long_running_queries():
    long_running_queries = []

    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )

        with conn.cursor() as cur:
            cur.execute(
                "SELECT pid, now() - pg_stat_activity.query_start AS " +
                "duration, query FROM pg_stat_activity WHERE state = 'active' " +
                "AND now() - pg_stat_activity.query_start > interval '10 seconds';"
            )
            query_info = cur.fetchall()
            for pid, duration, query in query_info:
                long_running_queries.append((pid, duration, query))
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if conn:
            conn.close()

    return long_running_queries


def terminate_long_running_queries():
    long_running_queries = []

    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )

        with conn.cursor() as cur:
            cur.execute(
                "SELECT pid, now() - pg_stat_activity.query_start AS duration "
                + "FROM pg_stat_activity WHERE state = 'active' AND now() - "
                + "pg_stat_activity.query_start > interval '10 seconds';"
            )
            long_running_queries = cur.fetchall()
            for pid, duration in long_running_queries:
                # print(f"Прерывание запроса с PID {pid}, который выполняется уже {duration}.")
                cur.execute(f"SELECT pg_terminate_backend({pid});")
                conn.commit()
                # print(f"Запрос с PID {pid} прерван.")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if conn:
            conn.close()

    return long_running_queries


def get_average_execution_time_and_reset_stats():
    average_execution_time_seconds=[]

    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )

        with conn.cursor() as cur:
            cur.execute("SELECT AVG(total_exec_time / 1000) AS average_execution_time_seconds FROM pg_stat_statements;")
            result = cur.fetchone()
            average_execution_time_seconds = result[0]

            cur.execute("SELECT pg_stat_statements_reset();")
            conn.commit()
            if average_execution_time_seconds is not None:
                formated_time = "{:.5f}".format(average_execution_time_seconds)
                return average_execution_time_seconds


    except Exception as e:
        print(f"Ошибка: {e}")
        return None




# def terminate_long_running_queries():
#     with conn.cursor() as cur:
#         cur.execute("SELECT pid, now() - pg_stat_activity.query_start AS duration FROM pg_stat_activity WHERE state = 'active' AND now() - pg_stat_activity.query_start > interval '10 seconds';")
#         long_running_queries = cur.fetchall()
#         pid, duration = long_running_queries[0]
#         return pid, duration
#         # f"Прерывание запроса с PID {pid}, который выполняется уже {duration}.




def get_statistic_chart(table, db_name: str = "test_db"):
    translate = {
        "active_sessions": "Активные сессии",
        "lwlock_sessions": "Сессии с lwlock",
        "bg_processess": "Процент буферов занятых фоновыми процессами",
        "avg_time": "Среднее время транзакции"
    }
    data = get_ten_last_records(table, db_name)
    x = [i+1 for i in range(len(data))]
    plt.figure()
    plt.plot(x, data)
    plt.title(translate[table])

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf


if __name__=="__main__":
    # print(get_lwlock())
    # print(get_pg_stat_activity())
    # terminate_process()
    # q, t = get_the_longest_query()
    # print(t)
    # print(is_above_avg(t))
    track_long_running_queries()