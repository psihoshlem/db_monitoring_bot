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

cur.execute("SELECT avg(total_exec_time) AS average_execution_time FROM pg_stat_statements;")
average_result = cur.fetchone()
if average_result:
    average_time = average_result[0]
    print(f"Average Execution Time: {average_time} ms")

cur.execute("SELECT sum(calls) AS total_calls FROM pg_stat_statements;")
total_calls_result = cur.fetchone()
if total_calls_result:
    total_calls = total_calls_result[0]
    print(f"Total Number of Queries: {total_calls}")

cur.close()
conn.close()
