import random
from copy import deepcopy
from . import time3600 as t36



timeStep = 15 # HACK


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


def generate_schedule(linedata, random = False):
    sr = {}
    for line in linedata.values():
        sr[line["id"]] = LineSchedule(line, random)
    return sr
