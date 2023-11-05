import subprocess


def stop_postgresql_with_backup(database_name):
    container_name = "db_monitoring_bot-db-1"
    try:
        start_command = f"docker start {container_name}"
        subprocess.run(start_command, shell=True)
        
        checkpoint_command = f"docker exec -i {container_name} psql -U postgres {database_name} -c 'CHECKPOINT;'"
        subprocess.run(checkpoint_command, shell=True)

        backup_command = f"docker exec -i {container_name} pg_dump -U postgres {database_name} > backup.sql"
        subprocess.run(backup_command, shell=True)

        stop_command = f"docker stop {container_name}"
        subprocess.run(stop_command, shell=True)

        return database_name
    except Exception as e:
        return(f"Произошла ошибка: {e}")


# stop_postgresql_with_backup(database_name)