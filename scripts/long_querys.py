import psycopg2

def make_long_query(time: int):
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

    cur.execute(f"SELECT pg_sleep({time});")
    print("Задержка в 50 секунд")
    conn.commit()

    cur.close()
    conn.close()

print("start")
make_long_query(50)
print("stop")
