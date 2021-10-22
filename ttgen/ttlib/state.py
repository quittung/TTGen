import os
from . import fileops, sigsearch, schedule as schd


class State:
    """contains complete world state, including infrastructure, line templates and schedules"""
    
    def __init__(self, template = None, schedule = None) -> None:
        self.sigdata = {}
        """contains all signals in a dictionary. key is signal id"""
        if template == None:
            for sig in fileops.load_json_dir(fileops.data_dir + "signals"):
                self.sigdata[sig["id"]] = sig
        else:
            self.sigdata = template.sigdata

        self.linedata = {}
        """contains all line data in a dictionary"""
        if template == None:
            for line in fileops.load_json_dir(fileops.data_dir + "lines"):
                self.linedata[line["id"]] = line
                line["routing"] = self.validateLine(line)
        else:
            self.linedata = template.linedata


        self.schedule = None
        """contains all decisions for all lines"""
        if schedule == None:
            if template == None:
                self.schedule = schd.generate_schedule(self.linedata)
            else:
                self.schedule = template.schedule
        else:
            self.schedule = schedule


        self.timetable = {}
        """contains final timetable after simulation"""
        if not template == None:
            self.timetable == template.timetable

    
    def validateLine(self, line): 
        """
        makes sure a line's route is actually connected and returns a list of possible routes
        """
        # find all possible connections between stops
        connections = []
        for i in range(0, len(line["stops"])):
            iNext = (i + 1) % len(line["stops"])
            connection = sigsearch.findTracks(self.sigdata, line["stops"][i]["id"], line["stops"][iNext]["id"])

            if len(connection) == 0:
                return None
            else:
                connections.append(connection)

        # reject all signals not connected to next and last stop
        for i in range(len(connections), -1, -1):
            i_curr = i % len(connections)
            i_next = (i + 1) % len(connections)

            # look at the arrival signals listed for each of the current stops departure signal
            # if the all connect over the same track, they should have the same arrival signals
            # if not, there are multiple ways to reach the next stop
            arrivals_list = [dep_sig["next"] for dep_sig in connections[i_curr].values()]
            arrivals_reachable = set([signal for arrivals in arrivals_list for signal in arrivals])
            for arrivals in arrivals_list:
                if set(arrivals) != arrivals_reachable:
                    print("It looks like there is more than one way to reach stop number " + str(i))
                    print("This kind of infrastructure is not supported at this point")
                    return


            # next check if that set of common arrival signals corresponds with the departure signals of the next one
            # if some arrival signals are missing, then those are going to another station
            # remove them from the list of arrival signals
            arrivals_reachable_reverse = [self.sigdata[arr_sig]["reverse"] for arr_sig in arrivals_reachable]
            arrivals_reachable_reverse = [arr_sig for arr_sig in arrivals_reachable_reverse if arr_sig != None]
            arrivals_reachable.update(arrivals_reachable_reverse)

            arrivals_invalid = [arr_sig for arr_sig in connections[i_next] if not arr_sig in arrivals_reachable]
            [connections[i_next].pop(sig) for sig in arrivals_invalid]


            # since you remove options based on the next stop
            # meaning information propagates backwards
            # it would make sense to iterate backwards as well

        

        # generate paths
        for stop in connections:
            for dep_sig in stop.values():
                dep_sig["next"] = [{
                        "id": arr_sig,
                        "path": sigsearch.search(self.sigdata, self.sigdata[dep_sig["id"]], lambda s: s == arr_sig)["path"]
                    } for arr_sig in dep_sig["next"]]


        return connections