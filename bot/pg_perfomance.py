import psycopg2

def get_buffer_usage_percent():
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
        SELECT buffers_backend / NULLIF(buffers_alloc, 0) * 100 AS buffers_backend_percent
        FROM pg_stat_bgwriter;
    """)

    buffer_percent = cur.fetchone()[0]

    cur.close()
    conn.close()

    return buffer_percent

buffer_percent = get_buffer_usage_percent()
print(f"Процент загруженности буфера: {buffer_percent:.2f}%")
