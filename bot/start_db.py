import subprocess


def start_postgresql_with_restore(database_name):
    container_name = "db_monitoring_bot-db-1"
    try:
        start_command = f"docker start {container_name}"
        subprocess.run(start_command, shell=True)

        restore_command = f"docker exec -i {container_name} psql -U postgres {database_name} < backup.sql"
        subprocess.run(restore_command, shell=True)

        return database_name
    except Exception as e:
        return(f"Произошла ошибка: {e}")


# start_postgresql_with_restore(database_name)


