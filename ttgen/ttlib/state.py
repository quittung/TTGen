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

            # look at the target signals listed for each of the current stops departure signal
            # if the all connect over the same track, they should have the same target signals
            # if not, there are multiple ways to reach the next stop
            next_list = [dep_sig["next"] for dep_sig in connections[i_curr].values()]
            targets_set = set([signal for arrivals in next_list for signal in arrivals])
            for arrivals in next_list:
                if set(arrivals) != targets_set:
                    print("It looks like there is more than one way to reach stop number " + str(i))
                    print("This kind of infrastructure is not supported at this point")
                    return


            # next check for differences between the reachable targets and available arrivals at the next stop
            # first remove all arrival signals that are not targeted
            targets_list_reverse = self.get_reverse_signals(targets_set)
            targets_list_combined = list(targets_set) + targets_list_reverse
            arrivals_dict: dict = connections[i_next]
            arrivals_list = list(arrivals_dict.keys())
            arrivals_list_reverse = self.get_reverse_signals(arrivals_list)
            arrivals_list_combined = arrivals_list + arrivals_list_reverse

            # find all arrivals that are not targeted
            arrivals_untargeted = [s for s in arrivals_list if not s in targets_list_combined]
            # remove those from the arrival dict
            if len(arrivals_untargeted) > 0:
                [arrivals_dict.pop(s) for s in arrivals_untargeted]

            # find all targeted signals that do not have an available arrival signal
            # those signals are on tracks that are dead ends or go to another station
            targets_invalid = [s for s in targets_set if not s in arrivals_list_combined]
            # go through the departure signals and remove those targets from their next list
            if len(targets_invalid) > 0:
                for dep_sig in connections[i_curr].values():
                    [dep_sig["next"].remove(s) for s in targets_invalid if s in dep_sig["next"]]

            # since you remove options based on the next stop
            # information propagates backwards
            # so iterate backwards as well

        

        # generate paths
        for stop in connections:
            for dep_sig in stop.values():
                dep_sig["next"] = [{
                        "id": arr_sig,
                        "path": sigsearch.search(self.sigdata, self.sigdata[dep_sig["id"]], lambda s: s == arr_sig)["path"]
                    } for arr_sig in dep_sig["next"]]


        return connections

    def get_reverse_signals(self, signal_list):
        # not useful for incomplete station data or terminus stations
        # arrivals_reachable_reverse = [self.sigdata[arr_sig]["reverse"] for arr_sig in targets_reachable]
        # arrivals_reachable_reverse = [arr_sig for arr_sig in arrivals_reachable_reverse if arr_sig != None]

        reverse_list = []
        for signal in signal_list:
            signal_reverse = "N" if signal[0] == "K" else "K"
            signal_reverse += signal[1:]
            reverse_list.append(signal_reverse)
            
        return reverse_list