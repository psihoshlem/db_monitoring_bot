import psycopg2

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

        for i in range(1, 1001):  # Изменим диапазон от 1 до 1000
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

if __name__=="__main__":
    create_and_populate_table()