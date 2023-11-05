import psycopg2

def calculate_buffer_usage():
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

    cur.execute("""
        SELECT buffers_backend, buffers_alloc
        FROM pg_stat_bgwriter;
    """)

    result = cur.fetchone()
    if result is not None:
        buffers_backend, buffers_alloc = result
        if buffers_alloc > 0:
            buffer_percent = (buffers_backend / buffers_alloc) * 100
            return buffer_percent

    cur.close()
    conn.close()

    return None

buffer_percent = calculate_buffer_usage()
if buffer_percent is not None:
    print(f"Процент загруженности буфера: {buffer_percent:.2f}%")
else:
    print("Данные о загрузке буфера недоступны.")
