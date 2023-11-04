import psycopg2
import random
import time

def simulate_user():
    conn = psycopg2.connect(
        dbname="test_db",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )

    try:
        cur = conn.cursor()

        while True:
            cur.execute("SELECT * FROM numbers;")
            result = cur.fetchone()
            if result:
                print(f"Значение: {result[0]}")

            time.sleep(random.uniform(1, 5))

            cur.execute("SELECT SUM(value) FROM numbers")
            total_sum = cur.fetchone()
            if total_sum:
                print(f"Сумма всех чисел: {total_sum[0]}")

            time.sleep(random.uniform(1, 5))

            cur.execute("SELECT * FROM numbers;")
            result = cur.fetchone()
            if result:
                print(f"Значение: {result[0]}")

            time.sleep(random.uniform(1, 5))

            cur.execute("SELECT SUM(value) FROM numbers")
            total_sum = cur.fetchone()
            if total_sum:
                print(f"Сумма всех чисел: {total_sum[0]}")

            cur.execute(f"SELECT pg_sleep(30);")


            time.sleep(random.uniform(1, 5))


    except Exception as e:
        print(f"Ошибка: {e}")

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    simulate_user()
