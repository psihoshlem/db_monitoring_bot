from functions import (
    get_lwlock_count,
    get_active_sessions,
    track_long_running_queries, get_average_execution_time_and_reset_stats
)
import json
from time import sleep
from main import warning_session_message, warning_long_query_message
from psycopg2 import OperationalError
from data_funcs import write_metrics_value, get_ten_last_records, get_admins


def write_to_store(table, value, db_name = "test_db"):
    last_records = get_ten_last_records(table, db_name)
    if len(last_records)!=0 and sum(last_records)/len(last_records)*3<value:
        for id in get_admins():
            warning_session_message(id, value, table)
    write_metrics_value(db_name, table, value)


if __name__=="__main__":
    with open("consts.json", "w") as file:
        json.dump({"STATS_CHECK_TIME": 3}, file)
    while True:
        try:
            write_to_store("active_sessions", get_active_sessions())
            write_to_store("lwlock_sessions", get_lwlock_count())
            write_to_store("avg_time", get_average_execution_time_and_reset_stats())
            long_query = track_long_running_queries()
            if long_query:
                for pid, duration, query in long_query:
                    for id in get_admins():
                        warning_long_query_message(int(id), pid,duration, query)
        except OperationalError:
            pass
        sleep(10)