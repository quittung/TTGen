import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

pio.templates.default = "plotly_dark"



def graph(timetable): # HACK everything about this, especially hard coding line names
    stations = ["HAR", "ERI", "TRQ", "ACT", "CLU", "ACT"]

    # Create figure with secondary y-axis
    fig = make_subplots()

    # Add traces
    for l in timetable.values():
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

        fig.add_trace(go.Scatter(x = line_stations, y = line_timing, name = l["id"]))

    # Add figure title
    fig.update_layout(
        title_text="graphic timetable"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="station")
    fig.update_xaxes(categoryorder = 'array', categoryarray = stations)

    # Set y-axes titles
    fig.update_yaxes(title_text="time (s)")

    fig.show()