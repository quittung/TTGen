# TTGen
## Introduction
I am making this so I can generate schedules for my trains in Transport Fever 2. It only covers the planning part, the in game functionality is provided by [TPF2-Timetables](https://github.com/IncredibleHannes/TPF2-Timetables).

The scheduling algorithm is inspired by genetic search algorithms. It works for the test data, but it still needs improvement and rigorous testing.

TTGen may or may not be useful for other use cases in the future, like other games or model trains. Nothing so far is specific to TF2. 

## Current State
 - At the time of this update, the project is slowly approaching a very early alpha version
 - There is no usable UI
 - The scheduler works in general, but it still has lots of obvious flaws
 - All data has to be transferred between TTGen and the game manually
 - There is very little documentation outside of the code
 - The code is still very messy

## How to use
### Dependencies etc.
 - Because of type hinting the code requires Python 3.9 or greater
 - Visualization of the results requires plotly

### Basic testing
To try the script on sample data, follow the steps below. It contains 4 stations in a row and two lines.
 - Copy the contents of docs/testdata/ to /data
 - Run ttgen/ttgen.py
 - Wait (usually less than a minute)
 - Look at the graphs in your browser or the generated timetable at /data/timetables

## General Concepts
### Data
 - Infrastructure data
  - Location: data/signals/[station_id].json
  - Description: Paths between signals and information about other paths they block
  - Source: Manual creation or generation with ttgen/station_gen.py; TF2 export planned
 - Line data
  - Location: data/lines/[line_id].json
  - Description: Name, frequency and stops of a line
  - Source: Manual creation
  
### Processing
 1. A set of random schedules is generated based on the line data
 2. All schedules are simulated and ranked by the amount of time spent waiting outside of designated stops
 3. A new set of schedules is generated based on the better performing half, introducing some amount of random changes
 4. Go back to 2. until a solution has been found
 5. The best schedule is exported to data/timetables/[line_id].json
