from copy import deepcopy
import random

from . import schedule, sim
from . import state as m_state



def smashSchedules(linedata, s1, s2, pr = 0.02):
    sr = schedule.generateRandomSchedule(linedata) # TODO: Make less random
    sl = [sr, s1, s2]
    s = deepcopy(s1)
    
    p1 = (1 - pr)/ 2 + pr
    iRand = lambda p: 0 if p < pr else 1 if p < p1 else 2
    sRand = lambda: sl[iRand(random.random())]

    for l in s:
        s[l].startTime = sRand()[l].startTime
        s[l].startTrack = sRand()[l].startTrack
        for i in range(0, len(s[l].waitTime)):
            s[l].waitTime[i] = sRand()[l].waitTime[i]
        for i in range(0, len(s[l].branch)):
            s[l].branch[i] = sRand()[l].branch[i]
    
    return s


def gmoSearch(state: m_state.State):
    population = 25

    schedule_list = [schedule.generateRandomSchedule(state.linedata) for i in range(0, population)]

    iteration = 0
    score_history = []
    while True:
        scoredSchedules = {}
        for i in range(0, len(schedule_list)):
            state.schedule = schedule_list[i]
            scoredSchedules[i] = sim.simulate_state(state)
        
    
        ranking = list(range(0,population))
        ranking.sort(key = lambda i: scoredSchedules[i])


        averageScore = sum(scoredSchedules.values()) / population
        score_history.append(averageScore)
        averageScore_rolling = rolling_avg(score_history)
        print("Score @ " + str(iteration) + ": " + format(averageScore_rolling, '.1f'))
        
        # hook for debugging
        if averageScore < 30:
            print(scoredSchedules[ranking[0]])


        ranking = ranking[0:int(population / 2)]
        ranking = [schedule_list[i] for i in ranking]
        schedule_list = [smashSchedules(state.linedata, random.choice(ranking), random.choice(ranking)) for i in range(0, population)]

        iteration += 1

def sample_last(data: list, lookback: int = 10):
    lookback = min(lookback, len(data))
    return data[-lookback:]

def rolling_avg(data: list, lookback: int = 10):
    sample = sample_last(data, lookback)
    return sum(sample) / len(sample)