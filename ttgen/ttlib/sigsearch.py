def search(sigdata, pos, ontgt, length = 0, maxlength = 1000):
    # target found
    if ontgt(pos["id"]):
        return {"path":[pos["id"]], "length": length}

    # dead end
    if len(pos["next"]) == 0 or length > maxlength:
        return None

    # run through options
    results = []
    for next in pos["next"]:
        if not next["id"] in sigdata.keys(): continue
        res = search(sigdata, sigdata[next["id"]], ontgt, length + 1)
        if res != None: results.append(res)
    
    if len(results) == 0:
        return None
    else:
        results.sort(key = lambda r : r["length"])
        results[0]["path"].insert(0, pos["id"])
        return results[0]


def findTracks(sigdata, sta_start, sta_end): 
    """finds all combinations of starting and departure signals that connect two stations"""
    startSignals = getStationSignals(sigdata, sta_start)
    endSignals = getStationSignals(sigdata, sta_end)

    connections = {}
    for ss in startSignals:
        connection = {"id": ss, "next": []}
        
        for es in endSignals:
            if search(sigdata, sigdata[ss], lambda s: s == es) != None:
                connection["next"].append(es)
        
        if len(connection["next"]) != 0:
            connections[ss] = connection
    
    return connections


def getStationSignals(sigdata, station):
    return [s for s in sigdata.keys() if in_station(s, station)]


def in_station(sig, station):
    return is_depsig(sig) and station in sig


def is_depsig(sig):
 return sig[1] == "_" and (sig[0] == "N" or sig[0] == "K")


def sigpath_obj(sigdata: dict, sigPath: str):
    """gets signal path object for a path id"""
    depSig, arrSig = sigPath.split("|")
    depSig = sigdata[depSig]
    return [s for s in depSig["next"] if s["id"] == arrSig][0]