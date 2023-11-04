import psycopg2
import time

def create_and_populate_table(create=True):
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

    if create:
        cur.execute("""
            CREATE TABLE numbers (
                id serial PRIMARY KEY,
                value integer
            );
        """)

        for i in range(101):
            cur.execute("INSERT INTO numbers (value) VALUES (%s)", (i,))

        conn.commit()

    cur.close()
    conn.close()

def view_table_contents():
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

    cur.execute("SELECT * FROM numbers;")
    results = cur.fetchall()

    for result in results:
        print(result)

    cur.close()
    conn.close()


def check_active_session():
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

    cur.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'active';")
    # count = cur.fetchone()[0]
    # print(f"Количество активных сессий: {count}")

    session_ids = cur.fetchall()
    for session_id in session_ids:
        print(f"Session ID (PID): {session_id[0]}")

    cur.close()
    conn.close()



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

    cur.execute("SELECT pid, now() - pg_stat_activity.query_start AS duration FROM pg_stat_activity WHERE state = 'active' AND now() - pg_stat_activity.query_start > interval '30 seconds';")
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

def check_last_connections():
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

    cur.execute("SELECT query, sum(total_exec_time) AS total_time, sum(rows) AS total_rows, sum(calls) AS total_calls FROM pg_stat_statements GROUP BY query;")

    results = cur.fetchall()

    for result in results:
        query, total_time, total_rows, total_calls = result
        print(f"Query: {query}, Total Time: {total_time} ms")

    cur.close()
    conn.close()

def get_the_longest_querys():
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
    cur.execute(
        "SELECT query, total_exec_time FROM pg_stat_statements " +
        "ORDER BY total_exec_time DESC LIMIT 1;"
    )
    query, exec_time = cur.fetchone()
    cur.execute(
        "SELECT sum(total_exec_time) AS average_execution_time" + 
        " FROM pg_stat_statements;"
    )
    sum_time = cur.fetchone()
    cur.execute("SELECT sum(calls) AS total_calls FROM pg_stat_statements;")
    total_calls = cur.fetchone()

    return query, exec_time, sum_time[0], total_calls[0]

def test_function():
    check_active_session()

    provoke_delay_50_seconds()
    time.sleep(10)

    terminate_long_running_queries()

    time.sleep(5)
    check_active_session()
    # check_last_connections()



# create_and_populate_table(create=True)
# view_table_contents()
check_active_session()
# provoke_delay_50_seconds()
# terminate_long_running_queries()
# check_active_session()
# check_last_connections()
# print(get_the_longest_querys())
# test_function()

# test.py
# kill_long_querys.py
# long_querys.py