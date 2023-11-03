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

cur.execute("SELECT query, sum(total_exec_time) AS total_time, sum(rows) AS total_rows, sum(calls) AS total_calls FROM pg_stat_statements GROUP BY query;")

results = cur.fetchall()

for result in results:
    query, total_time, total_rows, total_calls = result
    print(f"Query: {query}, Total Time: {total_time} ms, Total Rows: {total_rows}, Total Calls: {total_calls}")

cur.close()
conn.close()