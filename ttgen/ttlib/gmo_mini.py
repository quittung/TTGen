"""Coordinates search for a working schedule using mutation and selection."""
from copy import deepcopy
import random as rnd
from multiprocessing.dummy import Pool as ThreadPool
from time import perf_counter

from . import schedule, sim, state as m_state, time3600 as t36, statistics
from .simhelper import SimStats


default_scoring:SimStats = SimStats(
    block_travel=1,
    block_station=1,
    wait_station_nobuffer=1/15,
    wait_station_buffer=1/15/15
)
"""Default weights used for scoring a schedule."""


def smash_schedules(linedata: dict[str, dict], s1: dict[str, dict], s2: dict[str, dict], pr: float = 0.02, related: bool = True, energy: float = 1) -> dict[str, dict]:
    """Generates schedule based on two parents and random mutation.

    Args:
        linedata (dict[str, dict]): Line data from relevant state.
        s1 (dict[str, dict]): Parent A.
        s2 (dict[str, dict]): Parent B.
        pr (float, optional): Chance of random mutation. Defaults to 0.02.
        related (bool, optional): Base mutation on current values. Defaults to True.
        energy (float, optional): Strength of mutation. Defaults to 1.

    Returns:
        dict[str, dict]: Resulting child schedule.
    """
    s = mix_schedules(s1, s2, 0.5)

    #sr = schedule.generateRandomSchedule(linedata)
    sr = disturb_schedule(linedata, s, energy) if related else schedule.generate_schedule(linedata, True)
    s = mix_schedules(sr, s, pr)
    
    return s


def mix_schedules(s1: dict[str, dict], s2: dict[str, dict], p:float = 0.5) -> dict[str, dict]:
    """Mixes two schedules with configurable weighting.

    Args:
        s1 (dict[str, dict]): First base schedule.
        s2 (dict[str, dict]): Second base schedule.
        p (float, optional): Chance that any given trait is base of first schedule. Defaults to 0.5.

    Returns:
        dict[str, dict]: Mixed schedule.
    """    
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


def disturb_schedule(linedata: dict[str, dict], sched_in: dict[str, dict], energy: float = 1) -> dict[str, dict]:
    """Generates schedule with random incremental changes based on a reference schedule.

    Args:
        linedata (dict[str, dict]): Line data of relevant state.
        sched_in (dict[str, dict]): Reference schedule.
        energy (float, optional): Randomization strength. Defaults to 1.

    Returns:
        dict[str, dict]: [description]
    """
    sched_out = deepcopy(sched_in)
    sched_random = schedule.generate_schedule(linedata, True)

    rnd_time = lambda: rnd.randint(-energy, 2 * energy) * 15

    for line in sched_out:
        sched_out[line].startTime = t36.timeShift(sched_out[line].startTime, rnd_time())
        sched_out[line].startTrack = sched_random[line].startTrack
        for i in range(0, len(sched_out[line].waitTime)):
            sched_out[line].waitTime[i] = max(0, sched_out[line].waitTime[i] + rnd_time())
        sched_out[line].branch = [sched_out[line].random_branch(i) for i in range(len(sched_out[line].branch))]

    return sched_out


def gmo_search(state_template: m_state.State, pop_size: int = 25, survival = 0.5, max_iter: int = 5000, scoring: SimStats = default_scoring, visualize: bool = True) -> m_state.State:
    """Iterates through cycles of random mutation and selection to find a working schedule.

    Args:
        state_template (m_state.State): State to generate schedule for.
        pop_size (int, optional): Amount of schedules to work with in each generation. Defaults to 25.
        survival (float, optional): Share of each generation that survives. Defaults to 0.5.
        max_iter (int, optional): Max number of iteration before giving up. Defaults to 5000.
        scoring (SimStats, optional): Coefficients for scoring a schedule. Defaults to default_scoring.
        visualize (bool, optional): Additional visualization of progress. Defaults to True.

    Returns:
        m_state.State: State with the best solution.
    """    
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

        if (max_iter != -1 and iteration >= max_iter    # max iterations reached
            or schedule_scores[ranking[0]] == 0         # perfect solution found
            or (no_conflicts and iteration > 15 
                and abs(score_trend) < 0.001)):         # acceptable solution and no progress

            print(schedule_scores[ranking[0]])
            if visualize or True: 
                sim.simulate_state(state, True)
                stats.plot()
                #show_timetable(state)
            return state


        # creation of next generation
        ranking = ranking[0:int(max(pop_size * survival, min(pop_size, 5)))]
        ranking = [schedule_list[i] for i in ranking]
        stag_staleness_avg = stats.rolling_avg("stag_staleness")

        smash = lambda n, randomness = 0.02, related = True, energy = 1: [smash_schedules(state.linedata, rnd.choice(ranking), rnd.choice(ranking), randomness, related, energy) for i in range(n)]
        
        # decide level of randomization
        if (score_trend > -0.025 and not no_conflicts):
            if stag_staleness_avg > 0.975:
                schedule_list = smash(pop_size, 0.05, True, 30)
            else:
                schedule_list = smash(pop_size, 0.05, True, 6)
        else:
            schedule_list = smash(pop_size)


        iteration += 1


def show_timetable(state):
    """Graphs time table from a given state.

    Args:
        state ([type]): State to generate time table from.
    """
    from . import timetable, ttgraph
    tt = timetable.collect_timetable(state)
    ttgraph.graph(tt)
