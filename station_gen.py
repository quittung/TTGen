import json
import os
debug = False

print("Station JSON Generator")

station_id = "DBG"
if not debug: 
    station_id = input("Please enter the station id: ")


def query_route(direction):
    d_route = input("Please enter the ID of a route in direction " + direction + ". Leave empty to complete. ")
    
    if d_route == "":
        return

    d_station = input("Enter the ID of the next station on that route: ")
    n_sig = input ("What's the next signal number on that route? ")
    tracks_out = [int(n) for n in input("Enter the tracks that can depart on that route, separated by commas: ").split(",")]
    tracks_in = [int(n) for n in input("What tracks can be reached from that route? ").split(",")]
    print("")

    return {
        "direction":direction,
        "route":d_route,
        "station":d_station,
        "signals":n_sig,
        "tracks_in":tracks_in,
        "tracks_out":tracks_out
    }


def collect_destinations(side):
    destinations = []
    while True:
        dest = query_route(side)
        if dest == None:
            break
        
        destinations.append(dest)

    return destinations



destinations = []

file_load = False
raw_fname = "data/stations_raw/" + station_id + ".json"
if (not debug) and os.path.exists(raw_fname):
    if input("Station data already exists. Recover? (y/n)") == "y":
        file_load = True
        with open(raw_fname, 'r') as fobj:
            destinations = json.loads(fobj.read())

if not debug and not file_load:
    print("Let's start with the N side of the station.")
    destinations += collect_destinations("N")
    print()
    print()
    print("Next is the K side.")
    destinations += collect_destinations("K")
else:
    destinations.append({
            "direction":"N",
            "route":"R1",
            "station":"B",
            "signals":3,
            "tracks_in":[3],
            "tracks_out":[1,2]
        })
    destinations.append({
            "direction":"N",
            "route":"R2",
            "station":"C",
            "signals":5,
            "tracks_in":[4],
            "tracks_out":[3,2]
        })
    destinations.append({
            "direction":"K",
            "route":"R1",
            "station":"D",
            "signals":4,
            "tracks_in":[1,2],
            "tracks_out":[3]
        })


with open(raw_fname, 'w') as json_file:
  json.dump(destinations, json_file, indent = 2)


print()
print()
print("Processing data...")
dirs = ["N", "K"]
dests_filtered = {}
tracks_in = {}
tracks_out = {}


def encode_signame(route, direction, reference, number)-> str:
    name_main = direction + "_" + reference + str(number).zfill(2)
    if route == None:
        return(name_main)
    else: 
        return(route + "_" + name_main)

for dir in [0,1]:
    dests_filtered[dir] = list(filter(lambda dest: dest["direction"] == dirs[dir], destinations))
    if len(dests_filtered[dir]) == 0: 
        tracks_in[dir]=[]
        tracks_out[dir]=[]
    else:    
        tracks_in[dir] = list(set([t for t_s in dests_filtered[dir] for t in t_s["tracks_in"]]))
        tracks_out[dir] = list(set([t for t_s in dests_filtered[dir] for t in t_s["tracks_out"]]))



sig_list = []
def create_sigdata (sig_name, sig_next, sig_reverse):

        sig_data = {
            "id":sig_name,
            "next":sig_next,
            "reverse":sig_reverse
        }

        sig_list.append(sig_data)
        print(sig_data)


for dir in [0,1]:
    if len(dests_filtered[dir]) == 0: continue

    #generating bare bones entries for outgoing signals
    for t in tracks_out[dir]:
        sig_name = encode_signame(None, dirs[dir], station_id, t)
        
        sig_next = []
        for dest in dests_filtered[dir]:
            if t in dest["tracks_out"]:
                dest_name = encode_signame(dest["route"], dirs[dir], dest["station"], dest["signals"])
                sig_next.append({
                    "id": dest_name,
                    "ete": 0,
                    "blocks": []
                })

        sig_reverse = None
        if t in tracks_out[1 - dir]:
            sig_reverse = encode_signame(None, dirs[1 - dir], station_id, t)
        
        create_sigdata(sig_name, sig_next, sig_reverse)

    #generating bare bones entries for incoming signals
    for dest in dests_filtered[dir]:
        if len(dest["tracks_in"]) > 0:
            sig_name = encode_signame(dest["route"], dirs[1 - dir], station_id, 0)



            sig_next = []
            for t in dest["tracks_in"]:
                dest_name = encode_signame(None, dirs[1 - dir], station_id, t)
                sig_next.append({
                    "id": dest_name,
                    "ete": 0,
                    "blocks": []
                })

        sig_reverse = None

        create_sigdata(sig_name, sig_next, sig_reverse)

    print("Please enter information about conflicting paths:")
    for s in sig_list:
        pass

    #generating open track signals
    for dest in dests_filtered[dir]:
        for i in range(int(dest["signals"]), 0, -1):
            sig_name = encode_signame(dest["route"], dirs[dir], dest["station"], i)

            sig_next = [{
                "id": encode_signame(dest["route"], dirs[dir], dest["station"], i - 1),
                "ete": 0,
                "blocks": []
            }]

            sig_reverse = None

            create_sigdata(sig_name, sig_next, sig_reverse)



json_fname = "data/signals/" + station_id + ".json"
print("Writing data as " + json_fname)
with open(json_fname, 'w') as json_file:
  json.dump(sig_list, json_file, indent = 2)