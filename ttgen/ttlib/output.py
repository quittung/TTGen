import math
from . import fileops, state as m_state, time3600 as t36

def dump(state: m_state.State):
    for l, t in state.timetable.items():
        stops = state.linedata[l]["stops"]
        separation = state.linedata[l]["separation"]
        trains = math.ceil(t["duration"] / (separation * 60))

        tt_dict = {
            "id": l,
            "separation": separation,
            "trains": trains,
            "stops": [{
                "id": stops[i]["id"],
                "arr": t36.timeFormat(t["stops"][i]["arr"]),
                "dep": t36.timeFormat(t["stops"][i]["dep"])
            } for i in range(len(t["stops"]))]
        }

        fileops.dump_json(tt_dict, fileops.data_dir + "timetables/" + l + ".json")

        print(tt_dict)
        print("")

