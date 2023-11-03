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


if __name__=="__main__":
    # print(get_lwlock())
    # print(get_pg_stat_activity())
    # terminate_process()
    q, t = get_the_longest_query()
    print(t)
    print(is_above_avg(t))