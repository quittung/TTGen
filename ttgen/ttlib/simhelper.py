from . import time3600 as t36
from dataclasses import dataclass


verbose = False
time_step = 15 # HACK


def block_path_recurring(path, time, separation, block_table, verbose = False):
    hourly_deps = int(3600 / separation)
    conflicts = 0

    for i in range(hourly_deps):
        if block_path(path, t36.timeShift(time, separation * i), block_table, verbose): 
            conflicts += 1
    
    return conflicts


def block_path(path, time, block_table, verbose = False) -> bool:
    """reserves a path and returns if there were any conflicts"""
    time_slot = t36.timeSlot(time, time_step)
    conflict = is_blocked_verbose(path, time_slot, block_table, verbose)
    block_table[time_slot].add(path)

    return conflict


def is_blocked(sigPath, time_slot, blockTable):
    if sigPath in blockTable[time_slot]: return True
    
    depSig, arrSig =  sigPath.split("|")
    if depSig + "|*" in blockTable[time_slot]: return True
    if "*|" + arrSig in blockTable[time_slot]: return True

    return False


def is_blocked_verbose(sigPath, time_slot, blockTable, verbose = True):
    if sigPath in blockTable[time_slot]: 
        if verbose:
            print("conflict: " + sigPath + " at " + t36.timeFormat(time_slot) + " with itself")
        return True
    
    depSig, arrSig =  sigPath.split("|")
    if depSig + "|*" in blockTable[time_slot]: 
        if verbose:
            print("conflict: " + sigPath + " at " + t36.timeFormat(time_slot) + " with end signal")
        return True
    if "*|" + arrSig in blockTable[time_slot]: 
        if verbose:
            print("conflict: " + sigPath + " at " + t36.timeFormat(time_slot) + " with target signal")
        return True

    return False

def generateBlocktable(timeStep):
    bt = {}
    for t in range(0, 3600, timeStep):
        bt[t] = set()
    return bt

@dataclass
class SimStats:
    wait_station_buffer: float = 0
    wait_station_nobuffer: float = 0
    block_station: float = 0
    block_travel: float = 0
    
    def __add__(self, other):
        result = SimStats()
        self_dict = self.__dict__
        other_dict = other.__dict__
        result_dict = result.__dict__

        for k in self_dict:
            result_dict[k] = self_dict[k] + other_dict[k]

        return result

    def __mul__(self, other):
        result = 0
        self_dict = self.__dict__
        other_dict = other.__dict__

        for k in self_dict:
            result += self_dict[k] * other_dict[k]

        return result

    __rmul__ = __mul__
    

def time_add(time, duration, delta):
    time = t36.timeShift(time, delta)
    duration += delta

    return time, duration
