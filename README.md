# TTGen
## Introduction
I am making this so I can generate schedules for my trains in Transport Fever 2. It only covers the planning part, the in game functionality is provided by [TPF2-Timetables](https://github.com/IncredibleHannes/TPF2-Timetables).

The scheduling algorithm is inspired by genetic search algorithms. It sort of works at the moment, but it's probably far from efficient.

TTGen may or may not be useful for other use cases in the future, like other games or model trains. Nothing so far is specific to TF2. 

## Current State
 - At the time of this update, the project is basically a proof of concept.
 - There is no usable UI.
 - The scheduler sort of works, but it still has lots of obvious flaws.
 - All data has to be transferred between TTGen and the game manually.
 - There is basically no documentation outside of the code.
 - The code is still very messy and undocumented.

## General Concepts (outdated)
### Data
 - Infrastructure data describing the track layout and signals is generated. This can be done manually with a generation tool (station_gen.py) and, hopefully in the future, direct export for sims like TF2.
 - Train routes are specified without specific platforms or departure times.

### Processing
 - Train routes are validated and a very basic first schedule is created.
 - Parameters such as exact routing and wait times are magically (i.e. I haven't figured that out yet) changed until the overall wait time of all trains outside of designated stations has been minimized.
 - The finished schedules are exported. Probably as text for now, maybe they can be exported directly into some sims in the future.
