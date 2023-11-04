import psycopg2
import json

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
    with open("data.json", "r") as file:
        data = json.loads(file.read())
    data["admins"].append(id)
    with open("data.json", "w") as file:
        file.write(json.dumps(data))


def track_long_running_queries():
    with conn.cursor() as cur:
        cur.execute(
            "SELECT pid, now() - pg_stat_activity.query_start AS " + 
            "duration, query FROM pg_stat_activity WHERE state = 'active' " + 
            "AND now() - pg_stat_activity.query_start > interval '10 seconds';"
        )
        results = []
        long_running_queries = cur.fetchall()
        for query_info in long_running_queries:
            pid, duration, query = query_info
            return pid, duration, query
        else:
            return 
            # print(f"Длинный запрос с PID {pid} выполняется уже {duration}.")
            # print(f"Запрос: {query}\n")


def terminate_long_running_queries():
    with conn.cursor() as cur:
        cur.execute("SELECT pid, now() - pg_stat_activity.query_start AS duration FROM pg_stat_activity WHERE state = 'active' AND now() - pg_stat_activity.query_start > interval '10 seconds';")
        long_running_queries = cur.fetchall()
        pid, duration = long_running_queries[0]
        return pid, duration
        # f"Прерывание запроса с PID {pid}, который выполняется уже {duration}.



if __name__=="__main__":
    # print(get_lwlock())
    # print(get_pg_stat_activity())
    # terminate_process()
    # q, t = get_the_longest_query()
    # print(t)
    # print(is_above_avg(t))
    track_long_running_queries()