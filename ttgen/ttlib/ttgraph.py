"""Handles plotting a timetable using plotly."""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import colorsys, datetime

pio.templates.default = "plotly_dark"



def graph(timetable) -> None: # HACK everything about this, especially hard coding line names
    """Plots a timetable using plotly. Will open a tab in the standard browser.

    Args:
        timetable ([type]): Time table to plot.
    """    

    fig = make_subplots()

    stations = ["HAR", "ERI", "TRQ", "ACT", "CLU", "ACT"] # Stations to include in graph
    hue = 0 # Hue of first trace

    # Add traces for each line
    for l in timetable.values():
        line_trains = l["trains"]
        line_separation = l["separation"] * 60 # time between trains on the same line
        cycle_duration = line_separation * line_trains # time a train takes to complete a full run 

        # set trace color
        c = colorsys.hsv_to_rgb(hue, 0.7, 0.7)
        line_color = '#%02x%02x%02x' % (int(c[0]*255), int(c[1]*255), int(c[2]*255))
        hue = (hue + 0.412345) % 1 

        # convert arrival and departure times into correct format for plotting
        line_stations = []
        line_timing = []
        line_tracks = []
        for s in l["stops"]:
            line_stations.append(s["id"])
            line_timing.append(s["arr"])
            line_stations.append(s["id"])
            line_timing.append(s["dep"])

            for _ in range(2):
                line_tracks.append(s["track"])

        # removing time wrap for better plotting
        for i in range(1, len(line_timing)):
            while line_timing[i] < line_timing[i - 1]:
                line_timing[i] += 3600

        
        # extend timing by three cycles so time axis can be scrolled
        for i in range(1, 4):
            line_stations += line_stations
            line_timing += [t +  cycle_duration * i for t in line_timing]
            line_tracks += line_tracks

        # prepare reference point for conversion of time entries to datetime
        today = datetime.datetime.now()
        today -= datetime.timedelta(hours = today.hour, minutes = today.minute, seconds = today.second, microseconds = today.microsecond)

        # add datapoints to trace
        for i in range(line_trains):
            line_timing_variation = [today + datetime.timedelta(seconds = t + i * line_separation) for t in line_timing]
            fig.add_trace(go.Scatter(   x = line_stations, 
                                        y = line_timing_variation, 
                                        name = l["id"], 
                                        line=dict(color=line_color),
                                        customdata=line_tracks,
                                        hovertemplate='track: %{customdata}'
                                    ))


    # Add figure title
    fig.update_layout(title_text="graphic timetable")

    # Set x-axis title
    fig.update_xaxes(title_text="station")
    fig.update_xaxes(categoryorder = 'array', categoryarray = stations)

    # Set y-axes titles
    fig.update_yaxes(title_text="time (s)")
    fig.update_yaxes(range = [today + datetime.timedelta(seconds = 3600*2), today + datetime.timedelta(seconds = 3600*3)])


    fig.show()