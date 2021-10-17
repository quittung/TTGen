from copy import deepcopy
import random as rnd

from . import schedule, sim, state as m_state, time3600 as t36



def smash_schedules(linedata, s1, s2, pr = 0.02):
    """mixes two schedules with a chance of random mutation"""
    s = mix_schedules(s1, s2, 0.5)

    #sr = schedule.generateRandomSchedule(linedata)
    sr = disturb_schedule(linedata, s)
    s = mix_schedules(sr, s, pr)
    
    return s


def mix_schedules(s1, s2, p = 0.5):
    """mixes two schedules with configurable weighting"""
    s = deepcopy(s1)
    s_list = [s1, s2]

    rnd_01 = lambda p: 1 if rnd.random() >= p else 0
    rnd_s = lambda p, l: s_list[rnd_01(p)][l]

    for l in s:
        s[l].startTime = rnd_s(p, l).startTime
        s[l].startTrack = rnd_s(p, l).startTrack
        for i in range(0, len(s[l].waitTime)):
            s[l].waitTime[i] = rnd_s(p, l).waitTime[i]
        for i in range(0, len(s[l].branch)):
            s[l].branch[i] = rnd_s(p, l).branch[i]
    
    return s


def disturb_schedule(linedata, s, energy = 1):
    """less agressive randomization of schedule by modifying an existing one"""
    s = deepcopy(s)
    sr = schedule.generateRandomSchedule(linedata)

    rnd_pm = lambda: rnd.choice([-1,1])

    for l in s:
        s[l].startTime = t36.timeShift(s[l].startTime, rnd_pm() * 10 * energy)
        s[l].startTrack = sr[l].startTrack
        for i in range(0, len(s[l].waitTime)):
            s[l].waitTime[i] = max(0, s[l].waitTime[i] + rnd_pm() * 10 * energy)
        for i in range(0, len(s[l].branch)):
            s[l].branch[i] = sr[l].branch[i]

    return s


def gmo_search(state: m_state.State) -> m_state.State:
    """randomly mutates a population of schedules and uses evolutionary mechanisms to find a solution"""
    population = 25

    schedule_list = [schedule.generateRandomSchedule(state.linedata) for i in range(0, population)]

    iteration = 0
    score_history = []
    while True:
        # testing of fitness of current generation
        schedule_scores = {}
        for i in range(0, len(schedule_list)):
            state.schedule = schedule_list[i]
            schedule_scores[i] = sim.simulate_state(state)
        

        # evaluation
        ranking = list(range(0,population))
        ranking.sort(key = lambda i: schedule_scores[i])

        averageScore = sum(schedule_scores.values()) / population
        score_history.append(averageScore)
        averageScore_rolling = rolling_avg(score_history)
        
        print("Score @ " + str(iteration) + ": " + format(averageScore_rolling, '.1f'))
        if schedule_scores[ranking[0]] < 5:
            print(schedule_scores[ranking[0]])
            if schedule_scores[ranking[0]] == 0:
                visualize_progress(score_history)
                state.schedule = schedule_list[ranking[0]]
                return state

        # creation of next generation
        ranking = ranking[0:int(population / 2)]
        ranking = [schedule_list[i] for i in ranking]
        schedule_list = [smash_schedules(state.linedata, rnd.choice(ranking), rnd.choice(ranking)) for i in range(0, population)]

        iteration += 1


def sample_last(data: list, lookback: int = 10):
    lookback = min(lookback, len(data))
    return data[-lookback:]


def rolling_avg(data: list, lookback: int = 10):
    sample = sample_last(data, lookback)
    return sum(sample) / len(sample)


def visualize_progress(score_history):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.io as pio
    pio.templates.default = "plotly_dark"

    # Create figure with secondary y-axis
    fig = make_subplots()

    # Add traces
    fig.add_trace(go.Scatter(y = score_history, name="score history"))

    # Add figure title
    fig.update_layout(
        title_text="gmo seach"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="iteration")

    # Set y-axes titles
    fig.update_yaxes(title_text="average score")

    fig.show()