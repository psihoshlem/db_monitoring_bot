import psycopg2

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

cur.execute("SELECT * FROM pg_stat_activity;")

result = cur.fetchall()

for row in result:
    print(row)

cur.close()

conn.close()
