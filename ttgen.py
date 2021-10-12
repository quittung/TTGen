import json
import math
import os

def load_json(fname):
    with open(fname, 'r') as fobj:
        return json.loads(fobj.read())


#Loading infrstructure data
sigdata = {}
for fname in os.listdir("data/signals"):
    for sig in load_json("data/signals/" + fname):
        sigdata[sig["id"]] = sig

linedata = []
for fname in os.listdir("data/lines"):
    linedata.append(load_json("data/lines/" + fname))


paths = {}

def search(pos, ontgt, length = 0, maxlength = 1000):
    # target found
    if ontgt(pos["id"]):
        return {"path":[pos["id"]], "length": length}

    # dead end
    if len(pos["next"]) == 0 or length > maxlength:
        return None

    # run through options
    results = []
    for next in pos["next"]:
        if not next["id"] in sigdata.keys(): continue
        res = search(sigdata[next["id"]], ontgt, length + 1)
        if res != None: results.append(res)
    
    if len(results) == 0:
        return None
    else:
        results.sort(key = lambda r : r["length"])
        results[0]["path"].insert(0, pos["id"])
        return results[0]

def is_depsig(sig):
 return sig[1] == "_" and (sig[0] == "N" or sig[0] == "K")

def in_station(sig, station):
    return is_depsig(sig) and station in sig

def build_start(start_list):
    return {"id":"start", "next":[{"id": s} for s in start_list]}

def getStationSignals(station):
    return [s for s in sigdata.keys() if in_station(s, station)]

def findTracks(sta_start, sta_end): 
    startSignals = getStationSignals(sta_start)
    endSignals = getStationSignals(sta_end)

    connections = {}
    for ss in startSignals:
        connections[ss] = {"id": ss, "next": []}
        
        for es in endSignals:
            if search(sigdata[ss], lambda s: s == es) != None:
                connections[ss]["next"].append(es)
        
        if len(connections[ss]["next"]) == 0:
            connections.pop(ss)
    
    return connections


def validateLine(line): 
    """
    makes sure a line's route is actually connected and returns a list of possible routes
    """
    # find connections between stops
    connections = []
    for i in range(0, len(line["stops"])):
        iNext = (i + 1) % len(line["stops"])
        connection = findTracks(line["stops"][i]["id"], line["stops"][iNext]["id"])

        if len(connection) == 0:
            return None
        else:
            connections.append(connection)

    # make sure the line arrives at a track it can depart from & vise versa
    for i in range(len(connections), -1, -1):
        iCurr = i % len(connections)
        iNext = (i + 1) % len(connections)
        validArrivals = [s for s in connections[iNext]]

        targetedArrivals = []
        invalidDepartures = []
        for depSig in connections[iCurr]:
            invalidArrivals = []
            for arrSig in connections[iCurr][depSig]["next"]:
                if arrSig in validArrivals:
                    targetedArrivals.append(arrSig)
                elif sigdata[arrSig]["reverse"] in validArrivals:
                    targetedArrivals.append(sigdata[arrSig]["reverse"])
                else:
                    invalidArrivals.append(arrSig)

            [connections[iCurr][depSig]["next"].remove(s) for s in invalidArrivals]
            if len(connections[iCurr][depSig]["next"]) == 0:
                invalidDepartures.append(depSig)

        # remove departure signals that cannot reach the next station    
        [connections[iCurr].pop(s) for s in invalidDepartures]
        if len(connections[iCurr]) == 0: return None

        # remove arrival signals that cannot be reached by the last station
        [connections[iNext].pop(s) for s in list(set(validArrivals).difference(targetedArrivals))]

    # generate paths
    for i in range(0, len(connections)):
        iNext = (i + 1) % len(connections)
        for depSig in connections[i]:
            connections[i][depSig]["next"] = [{
                    "id": depSig,
                    "path": search(sigdata[depSig], lambda s: s == arrSig)["path"]
                } for arrSig in connections[i][depSig]["next"]]


    return connections
        

def estimateTravelTime(path, time):
    """dummy thicc function"""

    duration = (len(path) - 1) * 45
    duration += min(duration / 3, 40)
    return duration


schedules = []
linedata.sort(key = lambda l: l["prio"], reverse = True)
for line in linedata:
    schedule = {}

    line["routing"] = validateLine(line)

    """
    basically the only things i can change are
      which routing to follow 
      how long to wait before departing
    so how about this:
      for now just use 0 wait and route choice 0
    """

    total_duration = 0
    for i in range(0, len(line["stops"])):
        iNext = (i + 1) % len(line["stops"])

        segment = list(line["routing"][i].values())[0]["next"][0]["path"]
        duration = estimateTravelTime(segment, 0)
        total_duration += duration

    print(line["id"] + " -> " + str(total_duration) + "s")
        

    time_start = 0


""" 
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
f.close() """