import subprocess

def stop_postgresql_with_backup(container_name, database_name):
    try:
        backup_command = f"docker exec -i {container_name} pg_dump -U postgres {database_name} > backup.sql"
        subprocess.run(backup_command, shell=True)

        stop_command = f"docker stop {container_name}"
        subprocess.run(stop_command, shell=True)

        print("База данных успешно выключена и данные сохранены.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")



container_name = "db_monitoring_bot-db-1"
database_name = "test_db"

stop_postgresql_with_backup(container_name, database_name)