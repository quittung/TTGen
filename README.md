# TTGen
 Python scripts for generating Train Time Tables

## ok, so check it
This is intended to become a general purpose train scheduler, mainly aimed at simulations, but maybe also model railroads.

## General Process
### Data
 - Infrastructure data describing the track layout and signals is generated. This can be done manually with a generation tool (station_gen.py) and, hopefully in the future, direct export for sims like Transport Fever 2.
 - Train routes are specified without specific platforms or departure times.
### Processing
 - Train routes are validated and a very basic first schedule is created.
 - Parameters such as exact routing and wait times are magically (i.e. I haven't figured that out yet) changed until the overall wait time of all trains outside of designated stations has been minimized.
 - The finished schedules are exported. Probably as text for now, maybe they can be exported directly into some sims in the future.