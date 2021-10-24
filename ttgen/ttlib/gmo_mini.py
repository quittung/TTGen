from copy import deepcopy
import random as rnd
from multiprocessing.dummy import Pool as ThreadPool
from time import perf_counter

from . import schedule, sim, state as m_state, time3600 as t36, statistics
from .simhelper import SimStats

default_scoring = SimStats(
    block_travel=1,
    block_station=3
)

def smash_schedules(linedata, s1, s2, pr = 0.02, related: bool = True):
    """mixes two schedules with a chance of random mutation"""
    s = mix_schedules(s1, s2, 0.5)

    #sr = schedule.generateRandomSchedule(linedata)
    sr = disturb_schedule(linedata, s) if related else schedule.generate_schedule(linedata, True)
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


def disturb_schedule(linedata, sched_in, energy = 1):
    """less agressive randomization of schedule by modifying an existing one"""
    sched_out = deepcopy(sched_in)
    sched_random = schedule.generate_schedule(linedata, True)

    rnd_pm = lambda: rnd.choice([-1,1,2])

    for line in sched_out:
        sched_out[line].startTime = t36.timeShift(sched_out[line].startTime, rnd_pm() * 15 * energy)
        sched_out[line].startTrack = sched_random[line].startTrack
        for i in range(0, len(sched_out[line].waitTime)):
            sched_out[line].waitTime[i] = max(0, sched_out[line].waitTime[i] + rnd_pm() * 15 * energy)
        sched_out[line].branch = [sched_out[line].random_branch(i) for i in range(len(sched_out[line].branch))]

    return sched_out


def gmo_search(state_template: m_state.State, pop_size: int = 25, survival = 0.5, max_iter: int = 5000, scoring: SimStats = default_scoring, visualize: bool = True) -> m_state.State:
    """randomly mutates a population of schedules and uses evolutionary mechanisms to find a solution"""

    schedule_list = [schedule.generate_schedule(state_template.linedata, True) for i in range(0, pop_size)]
    pool = ThreadPool()

    iteration = 0
    stats = statistics.Statistics()
    while True:
        # testing of fitness of current generation
        start_time = perf_counter()

        state_list = [m_state.State(state_template, s) for s in schedule_list]
        schedule_stats = list(map(sim.simulate_state, state_list)) # single thread version for debugging
        #schedule_stats: list[SimStats] = pool.map(sim.simulate_state, state_list) # multi thread version for better performance
        schedule_scores = [s * scoring for s in  schedule_stats]

        stats.log("sim_time", perf_counter() - start_time)

        # evaluation
        ranking = list(range(0,pop_size))
        ranking.sort(key = lambda i: schedule_scores[i])

        # statistics
        score_best = schedule_scores[ranking[0]]
        stats.log("score", score_best)
        score_average = sum(schedule_scores) / pop_size
        stats.log("score_pop", score_average)
        averageScore_rolling = stats.rolling_avg("score_pop")
        stats.log("score_pop_rol", averageScore_rolling)
        score_trend = stats.trend("score", 50)
        stats.log("score_trend", score_trend)

        stag_staleness = score_best / score_average
        stats.log("stag_staleness", stag_staleness)

        stats_best = schedule_stats[ranking[0]]
        stats.log_dict(stats_best.__dict__)
        
        state = m_state.State(state_template, schedule_list[ranking[0]])
        message = "Score @ " + str(iteration) + ": " + format(averageScore_rolling, '.1f') + ", " + format(score_average, '.1f')
        #message += "\r\n" + "Calc time: " + format(duration, '.4f') + "\r\n"
        print(message)

        if iteration % 500 == 0 and iteration != 0:
            print("lowest score: " + str(schedule_scores[ranking[0]]))
            sim.simulate_state(state, True)
            stats.plot()
            show_timetable(state)


        # terminate search if conditions are met
        no_conflicts = stats_best.block_station == 0 and stats_best.block_travel == 0


        if (max_iter != -1 and iteration >= max_iter         # max iterations reached
            or schedule_scores[ranking[0]] == 0              # perfect solution found
            or (no_conflicts and abs(score_trend) < 0.001)): # acceptable solution and no progress

            print(schedule_scores[ranking[0]])
            if visualize or True: 
                sim.simulate_state(state, True)
                stats.plot()
                #show_timetable(state)
            return state


        # creation of next generation
        ranking = ranking[0:int(max(pop_size * survival, min(pop_size, 5)))]
        ranking = [schedule_list[i] for i in ranking]

        smash = lambda n, randomness = 0.02, related = True: [smash_schedules(state.linedata, rnd.choice(ranking), rnd.choice(ranking), pr = randomness, related = related) for i in range(n)]
        
        stag_staleness_avg = stats.rolling_avg("stag_staleness")


        if (score_trend > -0.025):
            if stag_staleness_avg > 0.975:
                print("Stale gene pool ({:.1f}%) detected in generation {}, introducing randomness.".format(stag_staleness_avg * 100, iteration))
                schedule_list = smash(pop_size, 0.05, False)
            else:
                print("Progress slowing down in generation {}, increasing mutation.".format(iteration))
                schedule_list = smash(pop_size, 0.02, True)
        else:
            schedule_list = smash(pop_size)

        iteration += 1


def sample_last(data: list, lookback: int = 10):
    lookback = min(lookback, len(data))
    return data[-lookback:]


def rolling_avg(data: list, lookback: int = 10):
    sample = sample_last(data, lookback)
    return sum(sample) / len(sample)


def show_timetable(state):
    from . import timetable, ttgraph
    tt = timetable.collect_timetable(state)
    ttgraph.graph(tt)


def visualize_progress(score_history):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # Create figure with secondary y-axis
    fig = make_subplots()

    # Add traces
    fig.add_trace(go.Scatter(y = score_history, name="score history"))

    # Add figure title
    fig.update_layout(
        title_text="gmo seach",
        theme="plotly_dark"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="iteration")

    # Set y-axes titles
    fig.update_yaxes(title_text="average score")

    fig.show()