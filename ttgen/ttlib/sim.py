from . import time3600 as t36
from . import state as m_state
from . import schedule as m_sched
from . import sigsearch



verbose = False
timeStep = 15 # HACK

def time_add(time, duration, delta):
    time = t36.timeShift(time, delta)
    duration += delta

    return time, duration

def simulate_state(state: m_state.State):
    blockTable = generateBlocktable(timeStep)

    wait_schedule_station = 0
    wait_schedule_travel = 0
    wait_schedule_station_nobuffer = 0
    wait_schedule_travel_nobuffer = 0

    for line in state.linedata.values():
        if verbose: print("processing line " + line["id"])

        sLine: m_sched.LineSchedule = state.schedule[line["id"]]
        timetable = {"stops": [{} for i in range(len(line["stops"]))]}
        state.timetable[line["id"]] = timetable
    
        time = sLine.startTime
        total_duration = 0

        wait_line_station = 0
        wait_line_travel = 0
        wait_line_station_nobuffer = 0
        wait_line_travel_nobuffer = 0

        # choose where to start
        # FIXME: why are the depSigs in a dict instead of a list?
        startSignal = list(line["routing"][0].values())[sLine.startTrack]

        for i in range(0, len(line["stops"])):
            iNext = (i + 1) % len(line["stops"])

            stop = line["stops"][i]
            path = startSignal["next"][sLine.branch[i]]["path"] 

            # TODO: Review this
            if path[-1] in line["routing"][iNext]:
                startSignal = line["routing"][iNext][path[-1]]
            else:
                for s in line["routing"][iNext]:
                    if state.sigdata[s]["reverse"] == path[-1]:
                        startSignal = s
        
            # waiting for first departure
            if i == 0:
                time = wait_first_departure(time, blockTable, path)

            # waiting at stop
            wait_station = sLine.waitTime[i]
            time, total_duration = wait_stop(stop["stop_time"], wait_station, time, total_duration, blockTable, path)
            timetable["stops"][i]["dep"] = time

            # traveling to next stop
            time, total_duration, wait_travel = travel(state.sigdata, path, time, total_duration, blockTable)
            timetable["stops"][iNext]["arr"] = time

            # classifying wait time
            wait_line_station += wait_travel + wait_station
            if not line["stops"][i]["buffer_stop"]:
                wait_line_station_nobuffer += wait_station
            else:
                wait_line_station += wait_station
            if not line["stops"][iNext]["buffer_stop"]:
                wait_line_travel_nobuffer += wait_travel
            else:
                wait_line_travel += wait_travel


        timetable["duration"] = total_duration


        # old information, ignore
        # if verbose: print(line["id"] + " -> " + str(total_duration) + "s, of that " + str(wait_line_station) + "s waiting for other trains, of that " + str(wait_line_station_nobuffer) + "s outside of buffer stations")
        # if verbose: print("")

        wait_schedule_station += wait_line_station
        wait_schedule_travel += wait_line_travel
        wait_schedule_station_nobuffer += wait_line_station_nobuffer
        wait_schedule_travel_nobuffer += wait_line_travel_nobuffer
        

    # score for how good this plan is, lower is better
    # basically weights no buffer waits at twice the severity
    score = wait_schedule_travel * 0.5 + wait_schedule_station_nobuffer + wait_schedule_travel_nobuffer * 3
    return score


def wait_stop(wait_plan, wait_schedule, time, total_duration, blockTable, path):
    waitTime = wait_plan + wait_schedule
    while waitTime > 0:
                # wait while advancing time and blocking
        blockTable[t36.timeSlot(time, timeStep)].add("*|N_" + path[0][2:])
        blockTable[t36.timeSlot(time, timeStep)].add("*|K_" + path[0][2:])

        ts = min(waitTime, timeStep)
        waitTime -= ts
        time, total_duration = time_add(time, total_duration, ts)
    return time, total_duration


def wait_first_departure(time, blockTable, path):
    while isBlocked("*|" + path[0], time, blockTable):
        time = t36.timeShift(time, timeStep)
    if time > 0:
                    #sLine.startTime = time
        if verbose: print("  can't start until " + t36.timeFormat(time))
    return time


def travel(sigdata, path, time, total_duration, blockTable, block = True, wait = True):
    totalWait = 0
    timeStart = time

    for i in range(0, len(path) - 1):
        sigPath = path[i] + "|" + path[i + 1]

        #waiting until signal path is no longer blocked
        if wait:
            waitDuration = 0
            while isBlocked(sigPath, time, blockTable):
                time, total_duration = time_add(time, total_duration, timeStep)
                waitDuration += timeStep
            if waitDuration > 0:
                if verbose: print("  waiting at " + sigPath + " for " + str(waitDuration) + "s")
                totalWait += waitDuration

        #traveling through signal path
        spDuration = 45 #placeholder for calculation of travel time for signal path

        #blocking current and related paths
        if block:
            while spDuration > 0:
                blockSlot = blockTable[t36.timeSlot(time, timeStep)]
                blockSlot.add(sigPath)
                [blockSlot.add(s) for s in sigsearch.sigpath_obj(sigdata, sigPath)["blocks"]]

                ts = min(spDuration, timeStep)
                spDuration -= ts
                time, total_duration = time_add(time, total_duration, ts)
        else:
            time, total_duration = time_add(time, total_duration, spDuration)

    return time, total_duration, totalWait


def isBlocked(sigPath, time, blockTable):
    if sigPath in blockTable[t36.timeSlot(time, timeStep)]: return True
    
    depSig, arrSig =  sigPath.split("|")
    if depSig + "|*" in blockTable[t36.timeSlot(time, timeStep)]: return True
    if "*|" + arrSig in blockTable[t36.timeSlot(time, timeStep)]: return True

    return False


def generateBlocktable(timeStep):
    bt = {}
    for t in range(0, 3600, timeStep):
        bt[t] = set()
    return bt
