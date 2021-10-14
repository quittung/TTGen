from . import time3600 as t36
from . import state as m_state
from . import schedule as m_sched
from . import sigsearch



verbose = False
timeStep = 15 # HACK


def simulate_state(state: m_state.State):
    blockTable = generateBlocktable(timeStep)

    scheduleWait = 0
    scheduleWaitNoBuffer = 0

    for line in state.linedata.values():
        if verbose: print("processing line " + line["id"])

        sLine: m_sched.LineSchedule = state.schedule[line["id"]]
    
        time = sLine.startTime
        total_duration = 0
        total_wait = 0
        total_wait_nobuffer = 0

        # choose where to start
        # FIXME: why are the depSigs in a dict instead of a list?
        startSignal = list(line["routing"][0].values())[sLine.startTrack]

        for i in range(0, len(line["stops"])):
            iNext = (i + 1) % len(line["stops"])

            stop = line["stops"][i]
            path = startSignal["next"][sLine.branch[i]]["path"] 

            if path[-1] in line["routing"][iNext]:
                startSignal = line["routing"][iNext][path[-1]]
            else:
                for s in line["routing"][iNext]:
                    if state.sigdata[s]["reverse"] == path[-1]:
                        startSignal = s
        
            # waiting for first departure
            if i == 0:
                while isBlocked("*|" + path[0], time, blockTable):
                    time = t36.timeShift(time, timeStep)
                if time > 0:
                    startTime = time
                    if verbose: print("  can't start until " + t36.timeFormat(time))

            # waiting at stop
            waitTime = stop["stop_time"] + sLine.waitTime[i]
            while waitTime > 0:
                # wait while advancing time and blocking
                blockTable[t36.timeSlot(time, timeStep)].add("*|N_" + path[0][2:])
                blockTable[t36.timeSlot(time, timeStep)].add("*|K_" + path[0][2:])

                ts = min(waitTime, timeStep)
                waitTime -= ts
                time = t36.timeShift(time, ts)

            # traveling to next stop
            travelData = travelPath(state.sigdata, path, time, blockTable)

            time = t36.timeShift(time, travelData["duration"])
            total_duration += travelData["duration"]
            total_wait += travelData["wait"]
            if not line["stops"][iNext]["buffer_stop"]:
                total_wait_nobuffer += travelData["wait"] + sLine.waitTime[i]


        if verbose: print(line["id"] + " -> " + str(total_duration) + "s, of that " + str(total_wait) + "s waiting for other trains, of that " + str(total_wait_nobuffer) + "s outside of buffer stations")
        if verbose: print("")

        scheduleWait += total_wait
        scheduleWaitNoBuffer += total_wait_nobuffer

    # score for how good this plan is, lower is better
    # basically weights no buffer waits at twice the severity
    score = scheduleWait + scheduleWaitNoBuffer
    return score


def travelPath(sigdata, path, time, blockTable, block = True, wait = True):
    duration = 0
    totalWait = 0
    timeStart = time

    for i in range(0, len(path) - 1):
        sigPath = path[i] + "|" + path[i + 1]

        #waiting until signal path is no longer blocked
        if wait:
            waitDuration = 0
            while isBlocked(sigPath, time, blockTable):
                time = t36.timeShift(time, timeStep)
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
                time = t36.timeShift(time, ts)
        else:
            time = t36.timeShift(time, spDuration)

    duration = t36.timeDiff(timeStart, time)

    return {
        "duration": duration,
        "wait": totalWait,
        "blockTable": blockTable
    }


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
