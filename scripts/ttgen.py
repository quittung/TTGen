from copy import deepcopy
import json
import math
import os
import random

from copy import deepcopy
import util.time3600 as t36



def load_json(fname):
    with open(fname, 'r') as fobj:
        return json.loads(fobj.read())


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

def timeSlot(time):
    return time - time % timeStep

def getSigPath(sigPath):
    depSig, arrSig = sigPath.split("|")
    depSig = sigdata[depSig]
    return [s for s in depSig["next"] if s["id"] == arrSig][0]

def travelPath(path, time, blockTable, block = True, wait = True):
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
                blockSlot = blockTable[timeSlot(time)]
                blockSlot.add(sigPath)
                [blockSlot.add(s) for s in getSigPath(sigPath)["blocks"]]

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
    if sigPath in blockTable[timeSlot(time)]: return True
    
    depSig, arrSig =  sigPath.split("|")
    if depSig + "|*" in blockTable[timeSlot(time)]: return True
    if "*|" + arrSig in blockTable[timeSlot(time)]: return True

    return False


class LineSchedule:
    """Contains all data on what the line will do at what point"""

    def __init__(self, line, randomize = False) -> None:
        self.line = line
        numberStops = len(line["stops"])

        if randomize:
            self.startTime = random.randrange(0, 3600)
            self.startTrack = random.randrange(0, len(line["routing"][0]))
            self.waitTime = [random.randrange(0, 300) for i in range(0, numberStops)]
            self.branch = [0] * numberStops
        else:
            self.startTime = 0
            self.startTrack = 0
            self.waitTime = [0] * numberStops
            self.branch = [0] * numberStops

        #self.verifyBranching(True)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def __deepcopy__(self, memo):
        lstmp = LineSchedule(self.line)
        lstmp.startTime = self.startTime
        lstmp.startTrack = self.startTrack
        lstmp.waitTime = deepcopy(self.waitTime, memo)
        lstmp.branch = deepcopy(self.branch, memo)
        return lstmp

    def verifyBranching(self):
        """ disconnected = False
        for i in range(0, len(self.branch)):
            checkIfTheNext
        pass """
        # TODO: idk, is this necessary?
        pass


def mutateLineSchedule(ls: LineSchedule, line):
    while True:
        action = random.randint(0,3)
        stop = random.randrange(0, len(ls.waitTime))
        if action == 0:
            # modify start time
            ls.startTime = t36.timeShift(ls.startTime, timeStep * random.choice([-1,1]))
            break
        elif action == 1:
            # modify start track
            oldStart = ls.startTrack
            ls.startTrack = random.randrange(0, len(line["routing"][0]))
            if not oldStart == ls.startTrack:
                break
        elif action == 2:
            # modify a random waitTime
            ls.waitTime[stop] = max(0, ls.waitTime[stop] + timeStep * random.choice([-1,1]))
            break
        else:
            # modify a random branching instruction
            # mutation.branch[stop] =
            pass 

    return ls


def mutateSchedule(scheduleList):
    line = random.randrange(0, len(linedata))
    newList = deepcopy(scheduleList)

    mutateLineSchedule(list(newList.values())[line], linedata[line])
    
    return newList


def loadLines():
    line_raw = []
    schedule ={}

    for fname in os.listdir("data/lines"):
        line_raw.append(load_json("data/lines/" + fname))

    line_raw.sort(key = lambda l: l["prio"], reverse = True)

    for line in line_raw:
        line["routing"] = validateLine(line)
        schedule[line["id"]] = LineSchedule(line, True)

    return line_raw, schedule


def generateBlocktable(timeStep):
    bt = {}
    for t in range(0, 3600, timeStep):
        bt[t] = set()
    return bt


def simulateSchedule(schedule):
    blockTable = generateBlocktable(timeStep)

    scheduleWait = 0
    scheduleWaitNoBuffer = 0

    for line in linedata:
        if verbose: print("processing line " + line["id"])

        sLine: LineSchedule = schedule[line["id"]]
    
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
                    if sigdata[s]["reverse"] == path[-1]:
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
                blockTable[timeSlot(time)].add("*|N_" + path[0][2:])
                blockTable[timeSlot(time)].add("*|K_" + path[0][2:])

                ts = min(waitTime, timeStep)
                waitTime -= ts
                time = t36.timeShift(time, ts)

            # traveling to next stop
            travelData = travelPath(path, time, blockTable)

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


def randoSearch(mutateSchedule, simulateSchedule, schedule):
    score = simulateSchedule(schedule)
    print(score)

    iteration = 0
    while(True):
        iteration += 1
        scheduleNew = mutateSchedule(schedule)
        scoreNew = simulateSchedule(scheduleNew)

        print("Score @ " + str(iteration) + ": " + str(score) + " -> " + str(scoreNew) + "\r\n\r\n")

        if scoreNew < score:
            schedule = scheduleNew
            score = scoreNew


def generateRandomSchedule():
    sr = {}
    for line in linedata:
        sr[line["id"]] = LineSchedule(line, True)
    return sr


def smashSchedules(s1, s2, pr = 0.02):
    sr = generateRandomSchedule() # TODO: Make less random
    sl = [sr, s1, s2]
    s = deepcopy(s1)
    
    p1 = (1 - pr)/ 2 + pr
    iRand = lambda p: 0 if p < pr else 1 if p < p1 else 2
    sRand = lambda: sl[iRand(random.random())]

    for l in s:
        s[l].startTime = sRand()[l].startTime
        s[l].startTrack = sRand()[l].startTrack
        for i in range(0, len(s[l].waitTime)):
            s[l].waitTime[i] = sRand()[l].waitTime[i]
        for i in range(0, len(s[l].branch)):
            s[l].branch[i] = sRand()[l].branch[i]
    
    return s

def gmoSearch():
    population = 25

    scheduleList = [generateRandomSchedule() for i in range(0, population)]

    iteration = 0
    while True:
        iteration += 1
        scoredSchedules = {}
        for i in range(0, len(scheduleList)):
            scoredSchedules[i] = simulateSchedule(scheduleList[i])
        
        averageScore = sum(scoredSchedules.values()) / population
        print("Score @ " + str(iteration) + ": " + str(averageScore))

        ranking = list(range(0,population))
        ranking.sort(key = lambda i: scoredSchedules[i])
        ranking = ranking[0:int(population / 2)]
        ranking = [scheduleList[i] for i in ranking]
        scheduleList = [smashSchedules(random.choice(ranking), random.choice(ranking)) for i in range(0, population)]

    
# Loading infrastructure data
sigdata = {}
for fname in os.listdir("data/signals"):
    for sig in load_json("data/signals/" + fname):
        sigdata[sig["id"]] = sig

# settings
timeStep = 15
verbose = False

# loading and processing lines
paths = {}
linedata, schedule = loadLines()

#randoSearch(schedule)
gmoSearch()
