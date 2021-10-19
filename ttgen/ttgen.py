import os
from ttlib import state as m_state, gmo_mini, timetable, ttgraph


# settings
timeStep = 15 # FIXME: Actually apply these
verbose = False

state = m_state.State()
state = gmo_mini.gmo_search(state, True)

timetable = timetable.collect_timetable(state, True)
ttgraph.graph(timetable)

