from . import time3600 as t36
from . import state as m_state
from . import schedule as m_sched
from . import sigsearch
from .simhelper import *


time_step = 15 # HACK


def simulate_state(state: m_state.State, verbose: bool = False, pin_first = True):
    blockTable = generateBlocktable(time_step)

    stats_schedule = SimStats()

    for line in state.linedata.values():
        if verbose: print("processing line " + line["id"])

        sLine: m_sched.LineSchedule = state.schedule[line["id"]]
        timetable = {"stops": [{} for i in range(len(line["stops"]))]}
        state.timetable[line["id"]] = timetable
        separation = line["separation"] * 60
    
        time = sLine.startTime
        total_duration = 0
        stats_line = SimStats()

        if pin_first:
            sLine.startTime = 0
            pin_first = False

        for i_stop in range(0, len(line["stops"])):
            i_next = (i_stop + 1) % len(line["stops"])

            start_signal = get_start_sig(line, sLine, i_stop)

            stop = line["stops"][i_stop]
            path = start_signal["next"][sLine.branch[i_stop]]["path"] 

            stats_stop = SimStats()

            # waiting at stop
            if i_stop > 0:
                if verbose and stop["id"] == "ACT":
                    print("somthing")
                if verbose: 
                    print("stopping at stop " + stop["id"] + " with index " + str(i_stop))

                wait_station = sLine.waitTime[i_stop]
                time, total_duration, block_station = wait_stop(stop["stop_time"], wait_station, time, total_duration, separation, blockTable, path, verbose = verbose)
                
                stats_stop.block_station = block_station
                if line["stops"][i_stop]["buffer_stop"]: # current stop is designated buffer stop
                    stats_stop.wait_station_buffer = sLine.waitTime[i_stop]
                else:
                    stats_stop.wait_station_nobuffer = sLine.waitTime[i_stop]

            timetable["stops"][i_stop]["dep"] = time


            # traveling to next stop
            time, total_duration, block_travel = travel(state.sigdata, path, time, total_duration, separation, blockTable, verbose = verbose)
            
            stats_stop.block_travel = block_travel
            timetable["stops"][i_next]["arr"] = time

            # wrapping up
            stats_line += stats_stop
            

        
        # correcting first arrival time
        separation = line["separation"] * 60 # separation between trains on same route
        cycle_duration = total_duration - total_duration % separation + separation # time between visits of a specific train at a station

        first_dep = timetable["stops"][0]["dep"]
        first_arr = timetable["stops"][0]["arr"]
        first_arr = t36.timeShift(first_arr, - cycle_duration)
        first_wait = t36.timeDiff(first_arr, first_dep)
        timetable["stops"][0]["arr"] = first_arr

        # blocking the first stop
        start_signal = get_start_sig(line, sLine, len(line["stops"]) - 1)
        path = start_signal["next"][sLine.branch[0]]["path"] 
        time, total_duration, block_station = wait_stop(0, first_wait, first_arr, total_duration, separation, blockTable, path, verbose = verbose)

        # TODO: Remove duplicate code 
        stats_line.block_station += block_station
        if line["stops"][0]["buffer_stop"]: # current stop is designated buffer stop
            stats_line.wait_station_buffer += sLine.waitTime[0]
        else:
            stats_line.wait_station_nobuffer += sLine.waitTime[0]

        # wrapping up
        timetable["duration"] = total_duration
        stats_schedule += stats_line
        

    if verbose:
    #    print(blockTable)
        print(stats_schedule)

    return stats_schedule

def get_start_sig(line: dict, sched_line: m_sched.LineSchedule, i_stop):
    """select start signal from branching data and target signals of last stop"""
    i_prev = (i_stop - 1) % len(line["stops"])

    target_signals = list(line["routing"][i_prev].values())[0]["next"]
    start_signal_str: str = target_signals[sched_line.branch[i_prev]]["id"]

    if not start_signal_str in line["routing"][i_stop]:
        start_signal_str_reverse = "N" if start_signal_str[0] == "K" else "K"
        start_signal_str_reverse += start_signal_str[1:]
        if start_signal_str_reverse in line["routing"][i_stop]:
            start_signal_str = start_signal_str_reverse
        else:
            return None

    return line["routing"][i_stop][start_signal_str]


def wait_stop(wait_plan, wait_schedule, time, total_duration, separation, block_table, path, verbose: bool = False):
    waitTime = wait_plan + wait_schedule
    time_blocked = 0

    while waitTime > 0:
        # wait while advancing time and blocking
        time_slot = t36.timeSlot(time, time_step)
        for direction in ["N", "K"]:
            path_to_block = "*|" + direction + "_" + path[0][2:]
            conflicts = block_path_recurring(path_to_block, time_slot, separation, block_table, verbose)
            if conflicts > 1:
                time_blocked += time_step * conflicts

        ts = min(waitTime, time_step)
        waitTime -= ts
        time, total_duration = time_add(time, total_duration, ts)

    return time, total_duration, time_blocked


def travel(sigdata, path, time, total_duration, separation, block_table, block = True, wait = True, verbose: bool = False):
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
                    conflicts = block_path_recurring(path_to_block, time, separation, block_table, verbose)
                    if conflicts > 1:
                        time_conflict += time_path_partial * conflicts

                time, total_duration = time_add(time, total_duration, time_path_partial)
        else:
            time, total_duration = time_add(time, total_duration, time_path)

    return time, total_duration, time_conflict
