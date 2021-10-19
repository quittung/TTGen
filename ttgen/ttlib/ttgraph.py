import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import random

pio.templates.default = "plotly_dark"



def graph(timetable): # HACK everything about this, especially hard coding line names
    stations = ["HAR", "ERI", "TRQ", "ACT", "CLU", "ACT"]

    # Create figure with secondary y-axis
    fig = make_subplots()

    # Add traces
    for l in timetable.values():
        line_trains = l["trains"]
        line_separation = l["separation"] * 60
        line_hourly_deps = int(3600 / line_separation)
        cycle_duration = line_separation * line_trains
        line_color = "#%06x" % random.randint(0, 0xFFFFFF)

        line_stations = []
        line_timing = []
        for s in l["stops"]:
            line_stations.append(s["id"])
            line_timing.append(s["arr"])
            line_stations.append(s["id"])
            line_timing.append(s["dep"])

        # removing time wrap for better plotting
        for i in range(1, len(line_timing)):
            while line_timing[i] < line_timing[i - 1]:
                line_timing[i] += 3600

        
        # extend timing by two cycles
        for i in range(1, 2):
            line_stations += line_stations
            line_timing += [t +  cycle_duration * i for t in line_timing]


        for i in range(line_trains):
            line_timing_variation = [t + i * line_separation for t in line_timing]
            fig.add_trace(go.Scatter(x = line_stations, y = line_timing_variation, name = l["id"], line=dict(color=line_color)))

    # Add figure title
    fig.update_layout(
        title_text="graphic timetable"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="station")
    fig.update_xaxes(categoryorder = 'array', categoryarray = stations)

    # Set y-axes titles
    fig.update_yaxes(title_text="time (s)")
    fig.update_yaxes(range = [3600, 7200])


    fig.show()