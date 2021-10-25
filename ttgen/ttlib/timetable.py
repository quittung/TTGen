"""Turning states into finished timetables."""
import math
from copy import deepcopy
from . import fileops, state as m_state, time3600 as t36

def dump(timetable: dict) -> None:
    """Writes timetable to disk in standard directory.

    Args:
        timetable (dict): Timetable dict to write.
    """  
    # create copy of timetable so time format can be changed without modifying the original 
    timetable = deepcopy(timetable)

    for l, tt_line in timetable.items():
        # make time human readable
        for i in range(len(tt_line["stops"])):
            tt_line["stops"][i]["arr"] = t36.timeFormat(tt_line["stops"][i]["arr"])
            tt_line["stops"][i]["dep"] = t36.timeFormat(tt_line["stops"][i]["dep"])

        fileops.dump_json(tt_line, fileops.data_dir + "timetables/" + l + ".json")

        print(tt_line)
        print("")


def collect_timetable(state: m_state.State, dump_file: bool = False) -> dict:    
    """Generates timetable from state. Optionally write timetable to file.

    Args:
        state (m_state.State): State to get data from.
        dump_file (bool, optional): Flag for writing timetable to file. Defaults to False.

    Returns:
        dict: Dictionary containing completed timetable.
    """    
    tt_collection = {}

    for l, t in state.timetable.items():
        stops = state.linedata[l]["stops"]
        routing = state.linedata[l]["routing"]
        branching = state.schedule[l].branch

        separation = state.linedata[l]["separation"]
        trains = math.ceil(t["duration"] / (separation * 60))

        tt_line = {
            "id": l,
            "separation": separation,
            "trains": trains,
            "stops": [{
                "id": stops[i]["id"],
                "track": int(list(routing[i].keys())[branching[(i - 1) % len(stops)]][-2:]),
                "arr": t["stops"][i]["arr"],
                "dep": t["stops"][i]["dep"]
            } for i in range(len(t["stops"]))]
        }

        tt_collection[l] = tt_line
    
    if dump_file:
        dump(tt_collection)

    return tt_collection

