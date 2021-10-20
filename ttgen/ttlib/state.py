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
        # find connections between stops
        connections = []
        for i in range(0, len(line["stops"])):
            iNext = (i + 1) % len(line["stops"])
            connection = sigsearch.findTracks(self.sigdata, line["stops"][i]["id"], line["stops"][iNext]["id"])

            if len(connection) == 0:
                return None
            else:
                connections.append(connection)

        # make sure the line arrives at a track it can depart from & vise versa
        for i in range(len(connections), -1, -1):
            iCurr = i % len(connections)
            iNext = (i + 1) % len(connections)
            validArrivals = [s for s in connections[iNext]]

            targetedArrivals = []
            invalidDepartures = []
            for depSig in connections[iCurr]:
                invalidArrivals = []
                for arrSig in connections[iCurr][depSig]["next"]:
                    if arrSig in validArrivals:
                        targetedArrivals.append(arrSig)
                    elif self.sigdata[arrSig]["reverse"] in validArrivals:
                        targetedArrivals.append(self.sigdata[arrSig]["reverse"])
                    else:
                        invalidArrivals.append(arrSig)

                [connections[iCurr][depSig]["next"].remove(s) for s in invalidArrivals]
                if len(connections[iCurr][depSig]["next"]) == 0:
                    invalidDepartures.append(depSig)

            # remove departure signals that cannot reach the next station    
            [connections[iCurr].pop(s) for s in invalidDepartures]
            if len(connections[iCurr]) == 0: return None

            # remove arrival signals that cannot be reached by the last station
            [connections[iNext].pop(s) for s in list(set(validArrivals).difference(targetedArrivals))]

        # generate paths
        for i in range(0, len(connections)):
            iNext = (i + 1) % len(connections)
            for depSig in connections[i]:
                connections[i][depSig]["next"] = [{
                        "id": depSig,
                        "path": sigsearch.search(self.sigdata, self.sigdata[depSig], lambda s: s == arrSig)["path"]
                    } for arrSig in connections[i][depSig]["next"]]


        return connections