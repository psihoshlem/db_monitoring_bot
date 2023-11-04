import subprocess

def start_postgresql_with_restore(container_name, database_name):
    try:
        start_command = f"docker start {container_name}"
        subprocess.run(start_command, shell=True)

        restore_command = f"docker exec -i {container_name} psql -U postgres {database_name} < backup.sql"
        subprocess.run(restore_command, shell=True)

        print("База данных успешно включена с восстановлением данных.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


container_name = "db_monitoring_bot-db-1"
database_name = "test_db"


start_postgresql_with_restore(container_name, database_name)
