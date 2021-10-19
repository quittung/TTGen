from . import time3600 as t36



verbose = False
time_step = 15 # HACK


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


    def __repr__(self) -> str:
        return self.__str__()


    def __str__(self) -> str:
        return str(self.__dict__)

    
    def __add__(self, other):
        result = Conflict()

        result.wait_station_buffer = self.wait_station_buffer + other.wait_station_buffer
        result.wait_station_nobuffer = self.wait_station_nobuffer + other.wait_station_nobuffer
        result.block_station = self.block_station + other.block_station 
        result.block_travel = self.block_travel + other.block_travel 

        return result
    

def time_add(time, duration, delta):
    time = t36.timeShift(time, delta)
    duration += delta

    return time, duration
