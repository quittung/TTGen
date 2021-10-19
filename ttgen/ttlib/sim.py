from . import time3600 as t36
from . import state as m_state
from . import schedule as m_sched
from . import sigsearch



verbose = False
time_step = 15 # HACK

def time_add(time, duration, delta):
    time = t36.timeShift(time, delta)
    duration += delta

    return time, duration

def simulate_state(state: m_state.State):
    blockTable = generateBlocktable(time_step)

    conflict_schedule = Conflict()

    for line in state.linedata.values():
        if verbose: print("processing line " + line["id"])

        sLine: m_sched.LineSchedule = state.schedule[line["id"]]
        timetable = {"stops": [{} for i in range(len(line["stops"]))]}
        state.timetable[line["id"]] = timetable
    
        time = sLine.startTime
        total_duration = 0

        conflict_line = Conflict()

        # choose where to start
        # FIXME: why are the depSigs in a dict instead of a list?
        startSignal = list(line["routing"][0].values())[sLine.startTrack]

        for i in range(0, len(line["stops"])):
            iNext = (i + 1) % len(line["stops"])

            stop = line["stops"][i]
            path = startSignal["next"][sLine.branch[i]]["path"] 

            conflict_stop = Conflict()

            # TODO: Review this
            if path[-1] in line["routing"][iNext]:
                startSignal = line["routing"][iNext][path[-1]]
            else:
                for s in line["routing"][iNext]:
                    if state.sigdata[s]["reverse"] == path[-1]:
                        startSignal = s

            # waiting at stop

            if i > 0:
                wait_station = sLine.waitTime[i]
                time, total_duration, block_station = wait_stop(stop["stop_time"], wait_station, time, total_duration, blockTable, path)
                
                conflict_stop.block_station = block_station
                if line["stops"][i]["buffer_stop"]: # current stop is designated buffer stop
                    conflict_stop.wait_station_buffer = sLine.waitTime[i]
                else:
                    conflict_stop.wait_station_nobuffer = sLine.waitTime[i]

            timetable["stops"][i]["dep"] = time


            # traveling to next stop
            time, total_duration, block_travel = travel(state.sigdata, path, time, total_duration, blockTable)
            
            conflict_stop.block_travel = block_travel
            timetable["stops"][iNext]["arr"] = time

            # wrapping up
            conflict_line += conflict_stop
            

        #TODO wait at first stop
        timetable["duration"] = total_duration
        
        # correcting first arrival time
        separation = line["separation"] * 60
        """separation between trains on same route"""
        cycle_duration = total_duration - total_duration % separation + separation
        """time between visits of a specific train at a station"""

        first_arrival = timetable["stops"][0]["arr"]
        first_arrival = t36.timeShift(first_arrival, - cycle_duration)
        timetable["stops"][0]["arr"] = first_arrival

        # old information, ignore
        # if verbose: print(line["id"] + " -> " + str(total_duration) + "s, of that " + str(wait_line_station) + "s waiting for other trains, of that " + str(wait_line_station_nobuffer) + "s outside of buffer stations")
        # if verbose: print("")

        # wrapping up
        conflict_schedule += conflict_line
        

    # score for how good this plan is, lower is better
    # basically weights no buffer waits at twice the severity
    score = conflict_schedule.wait_station_nobuffer * 0.5 + conflict_schedule.block_travel + conflict_schedule.block_station * 3
    return score

class Conflict:
    def __init__(self, ref = None) -> None:
        self.wait_station_buffer: float = 0
        self.wait_station_nobuffer: float = 0
        self.block_station: float = 0
        self.block_travel: float = 0
        
        if not ref == None:
            self.wait_station_buffer = ref.wait_station_buffer
            self.wait_station_nobuffer = ref.wait_station_nobuffer
            self.block_station = ref.block_station
            self.block_travel = ref.block_travel
    
    def __add__(self, other):
        result = Conflict()

        result.wait_station_buffer = self.wait_station_buffer + other.wait_station_buffer
        result.wait_station_nobuffer = self.wait_station_nobuffer + other.wait_station_nobuffer
        result.block_station = self.block_station + other.block_station 
        result.block_travel = self.block_travel + other.block_travel 

        return result

    





def wait_stop(wait_plan, wait_schedule, time, total_duration, block_table, path):
    waitTime = wait_plan + wait_schedule
    time_blocked = 0

    while waitTime > 0:
        # wait while advancing time and blocking
        time_slot = t36.timeSlot(time, time_step)
        for direction in ["N", "K"]:
            if block_path("*|" + direction + "_" + path[0][2:], time_slot, block_table):
                time_blocked += time_step

        ts = min(waitTime, time_step)
        waitTime -= ts
        time, total_duration = time_add(time, total_duration, ts)

    return time, total_duration, time_blocked


def travel(sigdata, path, time, total_duration, block_table, block = True, wait = True):
    time_conflict = 0
    timeStart = time

    for i in range(0, len(path) - 1):
        sigPath = path[i] + "|" + path[i + 1]

        #traveling through signal path
        time_path = 45 #placeholder for calculation of travel time for signal path

        #blocking current and related paths
        if block:
            while time_path > 0:
                time_path_partial = min(time_path, time_step)
                time_path -= time_path_partial

                blocklist = sigsearch.sigpath_obj(sigdata, sigPath)["blocks"] + [sigPath]

                for path_to_block in blocklist:
                    if block_path(path_to_block, time, block_table):
                        time_conflict += time_path_partial

                time, total_duration = time_add(time, total_duration, time_path_partial)
        else:
            time, total_duration = time_add(time, total_duration, time_path)

    return time, total_duration, time_conflict


def block_path(path, time, block_table) -> bool:
    """reserves a path and returns if there were any conflicts"""
    time_slot = t36.timeSlot(time, time_step)
    conflict = is_blocked(path, time_slot, block_table)
    block_table[time_slot].add(path)

    return conflict

def is_blocked(sigPath, time_slot, blockTable):
    if sigPath in blockTable[time_slot]: return True
    
    depSig, arrSig =  sigPath.split("|")
    if depSig + "|*" in blockTable[time_slot]: return True
    if "*|" + arrSig in blockTable[time_slot]: return True

    return False


def generateBlocktable(timeStep):
    bt = {}
    for t in range(0, 3600, timeStep):
        bt[t] = set()
    return bt
