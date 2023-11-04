import psycopg2

def get_average_execution_time_and_reset_stats():
    conn = psycopg2.connect(
        dbname="test_db",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )

    try:
        cur = conn.cursor()

        cur.execute("SELECT AVG(total_exec_time / 1000) AS average_execution_time_seconds FROM pg_stat_statements;")
        result = cur.fetchone()
        average_execution_time_seconds = result[0]

        cur.execute("SELECT pg_stat_statements_reset();")

        conn.commit()

        cur.close()
        conn.close()

        if average_execution_time_seconds is not None:
            formated_time = "{:.5f}".format(average_execution_time_seconds)
            print(formated_time)
            return formated_time

    except Exception as e:
        print(f"Ошибка: {e}")
        return None


get_average_execution_time_and_reset_stats()
# average_time = get_average_execution_time_and_reset_stats()
# if average_time is not None:
#     formated_time = "{:.2f}".format(average_time)
#     print(f"Среднее время выполнения запросов: {formated_time} секунд")
# else:
#     print("Не удалось получить среднее время выполнения запросов.")
