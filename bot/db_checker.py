from functions import (
    get_lwlock_count, 
    get_the_longest_query, 
    is_above_avg,
    get_active_sessions
)
from time import sleep
from main import warning_session_message, warning_long_query_message
import json

monitoring_data = {
    "active_sessions": [],
    "lwlock_sessions": []
}

def write_to_store(key: str, value: int) -> bool:
    warn = False
    if monitoring_data[key]:
        if sum(monitoring_data[key])/len(monitoring_data[key])*3<value:
            warn = True
    monitoring_data[key].append(value)
    if len(monitoring_data[key]) > 10:
        monitoring_data[key].pop(0)
    return warn

if __name__=="__main__":
    with open("data.json", "r") as file:
        admins_ids = json.loads(file.read())["admins"]
    while True:
        active_sessions = get_active_sessions()
        if write_to_store("active_sessions", active_sessions):
            for id in admins_ids:
                warning_session_message(id, active_sessions)
        lwlock_count = get_lwlock_count()
        if write_to_store("lwlock_sessions", lwlock_count):
            for id in admins_ids:
                warning_session_message(id, lwlock_count)
        query, time = get_the_longest_query()
        if is_above_avg(time):
            warning_long_query_message(id, time, query)
        sleep(60)