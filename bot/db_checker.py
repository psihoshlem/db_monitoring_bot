from functions import (
    get_lwlock_count, 
    get_the_longest_query, 
    is_above_avg,
    get_active_sessions,
    track_long_running_queries,
    get_data_json,
    write_data_json
)
from time import sleep
from main import warning_session_message, warning_long_query_message
import json

from data_funcs import write_metrics_value, get_ten_last_records

monitoring_data = {
    "active_sessions": [],
    "lwlock_sessions": []
}

def write_to_store(key: str, value: int) -> bool:
    data = get_data_json()
    monitoring_data = data["databases"]["test_db"]
    warn = False
    if monitoring_data[key]:
        if sum(monitoring_data[key])/len(monitoring_data[key])*3<value:
            warn = True
    monitoring_data[key].append(value)
    if len(monitoring_data[key]) > 10:
        monitoring_data[key].pop(0)
    data["databases"]["test_db"] = monitoring_data
    write_data_json(data)
    return warn

def write_to_store2(table, value, db_name = "test_db"):
    last_records = get_ten_last_records(table, db_name)
    if len(last_records)!=0 and sum(last_records)/len(last_records)*3<value:
        for id in admins_ids:
            warning_session_message(id, value)
    write_metrics_value(db_name, table, value)


if __name__=="__main__":
    with open("data.json", "r") as file:
        admins_ids = json.loads(file.read())["admins"]
    while True:
        # active_sessions = get_active_sessions()
        write_to_store2("active_sessions", get_active_sessions())
        # if write_to_store("active_sessions", active_sessions):
        #     for id in admins_ids:
        #         warning_session_message(id, active_sessions)
        write_to_store2("lwlock_sessions", get_lwlock_count())
        # lwlock_count = get_lwlock_count()
        # if write_to_store("lwlock_sessions", lwlock_count):
        #     for id in admins_ids:
        #         warning_session_message(id, lwlock_count)
        # query, time = get_the_longest_query()
        # if is_above_avg(time):
        #     for id in admins_ids:
        #         warning_long_query_message(id, pid, time, query)
        long_query = track_long_running_queries()
        if long_query:
            for pid, duration, query in long_query:
                for id in admins_ids:
                    warning_long_query_message(id, pid,duration, query)
            # pid, duration, query
        sleep(10)