import json
import math
 
# Opening JSON file
f = open('line.json',)
 

data = json.load(f)

time_start = 0

time_min = 0
for stop in data["stops"]:
    time_min += stop["stop_time"] + stop["travel_time"]
 

time_sep = data["separation"] * 60
number_trains = math.ceil(time_min/time_sep)

buffer_time = number_trains * time_sep - time_min
buffer_stops = 0
for stop in data["stops"]:
    if stop["buffer_stop"]:
        buffer_stops += 1

def time_format(seconds):
    minutes = math.floor(seconds / 60)
    seconds -= minutes * 60
    minutes -= math.floor(minutes / 60) * 60
    return(str(minutes).zfill(2) + ":" + str(seconds).zfill(2))


print("Timetable buffer: " + time_format(buffer_time))
print("Number of Trains: " + str(number_trains))
print("")

time = time_start
for stop in data["stops"]:
    print(stop["id"])
    print(time_format(time))
    time += stop["stop_time"]
    if stop["buffer_stop"]:
        time += math.floor(buffer_time / buffer_stops)
    print(time_format(time))
    time += stop["travel_time"]
    print("")

# Closing file
f.close()