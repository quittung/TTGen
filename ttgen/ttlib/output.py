import math
from . import fileops, state as m_state, time3600 as t36

def dump(timetable):
    """writes complete timetable to file"""
    for l, tt_line in timetable.items():
        for i in range(len(tt_line["stops"])):
            tt_line["stops"][i]["arr"] = t36.timeFormat(tt_line["stops"][i]["arr"])
            tt_line["stops"][i]["dep"] = t36.timeFormat(tt_line["stops"][i]["dep"])

        fileops.dump_json(tt_line, fileops.data_dir + "timetables/" + l + ".json")

        print(tt_line)
        print("")


def collect_timetable(state: m_state.State, dump_file: bool = False):
    """collects all relevant info from a state obj and generates a stand alone timetable"""
    tt_collection = {}

    for l, t in state.timetable.items():
        stops = state.linedata[l]["stops"]
        separation = state.linedata[l]["separation"]
        trains = math.ceil(t["duration"] / (separation * 60))

        tt_line = {
            "id": l,
            "separation": separation,
            "trains": trains,
            "stops": [{
                "id": stops[i]["id"],
                "arr": t["stops"][i]["arr"],
                "dep": t["stops"][i]["dep"]
            } for i in range(len(t["stops"]))]
        }

        tt_collection[l] = tt_line
    
    if dump_file:
        dump(tt_collection)

    return tt_collection

