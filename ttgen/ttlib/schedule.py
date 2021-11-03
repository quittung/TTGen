"""Handles logic and data around the exact implementation of a line."""
import random
from copy import deepcopy



timeStep = 15 # HACK


class LineSchedule:
    """Specifies exact path, start time, additional wait and other things for a line."""

    def __init__(self, line, randomize = False) -> None:
        """Initializes the schedule based on line data.

        Args:
            line ([type]): Line data from state object.
            randomize (bool, optional): Randomize starting values. Defaults to False.
        """        
        self.line = line
        numberStops = len(line["stops"])

        if randomize:
            self.startTime = random.randrange(0, 3600)
            self.startTrack = random.randrange(0, len(line["routing"][0]))
            self.waitTime = [random.randrange(0, 300) for i in range(0, numberStops)]
            self.branch = [self.random_branch(i) for i in range(numberStops)]
        else:
            self.startTime = 0
            self.startTrack = 0
            self.waitTime = [0] * numberStops
            self.branch = [0] * numberStops


    def __repr__(self) -> str:
        return str(self.__dict__)


    def __deepcopy__(self, memo):
        lstmp = LineSchedule(self.line)
        lstmp.startTime = self.startTime
        lstmp.startTrack = self.startTrack
        lstmp.waitTime = deepcopy(self.waitTime, memo)
        lstmp.branch = deepcopy(self.branch, memo)
        return lstmp


    def random_branch(self, stop: int) -> dict:
        """Chooses a random branch originating from a given stop.

        Args:
            stop (int): Index of origin stop.

        Returns:
            dict: Path to next stop.
        """        
        next_stop = (stop + 1) % len(self.line["stops"])
        return random.randrange(0, len(self.line["routing"][next_stop]))


def generate_schedule(linedata: dict, random: bool = False):
    """Generates a set of line schedules for each line listed in the line data.

    Args:
        linedata (dict): Line data from state object.
        random (bool, optional): Randomize starting values. Defaults to False.

    Returns:
        [type]: [description]
    """    
    sr = {}
    for line in linedata.values():
        sr[line["id"]] = LineSchedule(line, random)
    return sr
