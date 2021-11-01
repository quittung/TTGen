# Control Flow Overview
This document outlines what how the different parts of the script call each other. For more details refer to other documentation or the code itself.

## Top Level Control Flow
- `state` - load state from disk
    - `fileops` - load files
    - `state.validateLine` - generate metadata for lines
    
- `gmo_mini` - search for time table
    - randomly generate a set of schedules
    - MAIN LOOP
        - `sim` - simulate schedules -> see `Simulation Control Flow`
        - score schedules
        - sort schedules by rank
        - check termination conditions
        - kill of inferior schedules
        - `gmo_mini.smash_schedules` - generate next generation of schedules
    - return best schedule

- `timetable` - condense timetable info from state into single object
- `ttgraph` - graph time table

## Simulation Control Flow
- `simulate_state` - fully simulate the path of each line and keep track of conflicts
- for each line
    - for each stop
        - `wait_stop` - wait at the stop and keep track of conflicts
        - `travel` - travel to next stop and keep track of conflicts
    - close loop and wait until the first departure
- sum time spent in conflict and return it 