import subprocess

def backup_and_restart_postgresql(container_name, database_name):
    try:
        stop_command = f"docker stop {container_name}"
        subprocess.run(stop_command, shell=True)

        backup_command = f"docker exec -i {container_name} pg_dump -U postgres {database_name} > backup.sql"
        subprocess.run(backup_command, shell=True)

        start_command = f"docker start {container_name}"
        subprocess.run(start_command, shell=True)

        restore_command = f"docker exec -i {container_name} psql -U postgres {database_name} < backup.sql"
        subprocess.run(restore_command, shell=True)

        print("База данных успешно выключена, скопирована и включена.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

container_name = "db_monitoring_bot-db-1"
database_name = "test_db"
backup_and_restart_postgresql(container_name, database_name)