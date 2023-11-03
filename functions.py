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
        cur.execute("SELECT count(*) FROM pg_stat_activity;")
        result = cur.fetchall()
        return result[0][0]



def get_lwlock():
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
        query, exec_time = cur.fetchall()



def terminate_process(id: int):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT pg_terminate_backend(pid)" + 
            f" FROM pg_stat_activity WHERE pid = {id};"
        )


if __name__=="__main__":
    # print(get_lwlock())
    # print(get_pg_stat_activity())
    terminate_process()