# TTGen
## Introduction
I am making this so I can generate schedules for my trains in Transport Fever 2. It only covers the planning part, the in game functionality is provided by [TPF2-Timetables](https://github.com/IncredibleHannes/TPF2-Timetables).

The scheduling algorithm is inspired by genetic search algorithms. It sort of works at the moment, but it's probably far from efficient.

TTGen may or may not be useful for other use cases in the future, like other games or model trains. Nothing so far is specific to TF2. 

## Current State
 - At the time of this update, the project is somewhere between a proof of concept and a very early alpha version
 - There is no usable UI
 - The scheduler sort of works, but it still has lots of obvious flaws
 - All data has to be transferred between TTGen and the game manually
 - There is basically no documentation outside of the code
 - The code is still very messy

## How to use
### Basic testing
To try the script on sample data, follow the steps below. It contains 4 stations in a row and two lines.
 - Copy the contents of docs/testdata/ to /data
 - Run ttgen/ttgen.py
 - Wait (usually just a few seconds)
 - Look at the generated timetable at /data/timetables

## How it works
 1. A set of random schedules is generated based on the line data
 2. All schedules are simulated and ranked by the amount of time spent waiting outside of designated stops
 3. A new set of schedules is generated based on the better performing half, introducing some amount of random changes
 4. Go back to 2. until a solution has been found
 5. The best schedule is exported to data/timetables/[line_id].json

If you want to know more, check out the docs or the code. I recommend starting with the [control flow overview][docs/control_flow.md]