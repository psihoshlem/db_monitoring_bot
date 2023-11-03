from functions import (
    get_lwlock_count, 
    get_the_longest_query, 
    is_above_avg,
    get_active_sessions
)
from time import sleep

monitoring_data = {
    "active_sessions": [],
    "lwlock_sessions": []
}

def write_to_store(key: str, value: int) -> bool:
    warn = False
    if sum(monitoring_data[key])/len(monitoring_data[key])*3<value:
        warn = True
    monitoring_data[key].append(value)
    if len(monitoring_data) > 10:
        monitoring_data[key].pop(0)
    return warn

while True:
    if write_to_store("active_sessions", get_active_sessions()):
        pass
    if write_to_store("lwlock_sessions", get_lwlock_count()):
        pass
    query, time = get_the_longest_query()
    if is_above_avg(time):
        pass
    sleep(60)