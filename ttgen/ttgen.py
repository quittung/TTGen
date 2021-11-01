from ttlib import state as m_state, gmo_mini, timetable as tt, ttgraph


# settings
timeStep = 15 # FIXME: Actually apply these
verbose = False

# calculate time table
state = m_state.State()
state = gmo_mini.gmo_search(state, visualize = False)

# show time table
timetable = tt.collect_timetable(state, True)
ttgraph.graph(timetable)

