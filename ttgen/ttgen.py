import os
from ttlib import state as m_state, gmo_mini



# settings
timeStep = 15 # FIXME: Actually apply these
verbose = False

state = m_state.State()
gmo_mini.gmo_search(state)
