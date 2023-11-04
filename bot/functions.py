import psycopg2
import json
import matplotlib.pyplot as plt
import io

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
            "SELECT count(*) FROM pg_stat_activity " +
            "WHERE state='active';"
        )
        result = cur.fetchall()
        return result[0][0]


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


def write_admin(id: int):
    data = get_data_json
    data["admins"].append(id)
    write_data_json(data)


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
            cur.execute("SELECT pid, now() - pg_stat_activity.query_start AS duration FROM pg_stat_activity WHERE state = 'active' AND now() - pg_stat_activity.query_start > interval '10 seconds';")
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



# def terminate_long_running_queries():
#     with conn.cursor() as cur:
#         cur.execute("SELECT pid, now() - pg_stat_activity.query_start AS duration FROM pg_stat_activity WHERE state = 'active' AND now() - pg_stat_activity.query_start > interval '10 seconds';")
#         long_running_queries = cur.fetchall()
#         pid, duration = long_running_queries[0]
#         return pid, duration
#         # f"Прерывание запроса с PID {pid}, который выполняется уже {duration}.


def get_data_json():
    with open("data.json", "r") as file:
        data = json.loads(file.read())
    return data


def write_data_json(data):
    with open("data.json", "w") as file:
        file.write(json.dumps(data))
    

def get_statistic_chart(db_name: str = "test_db"):
    active_sessions = get_data_json()["databases"]["test_db"]["active_sessions"]
    lwlock_sessions = get_data_json()["databases"]["test_db"]["lwlock_sessions"]
    x = [i+1 for i in range(len(active_sessions))]
    plt.plot(x, active_sessions)
    plt.title("Активные сессии")

    buf1 = io.BytesIO()
    plt.savefig(buf1, format='png')
    buf1.seek(0)

    plt.plot(x, lwlock_sessions)
    plt.title("Сессии lwlock")

    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png')
    buf2.seek(0)
    return buf1, buf2


if __name__=="__main__":
    # print(get_lwlock())
    # print(get_pg_stat_activity())
    # terminate_process()
    # q, t = get_the_longest_query()
    # print(t)
    # print(is_above_avg(t))
    track_long_running_queries()