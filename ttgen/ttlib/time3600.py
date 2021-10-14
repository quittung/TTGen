import math



def timeShift(time, diff):
    return (time + diff) % 3600


def timeDiff(timeA, timeB):
    """this function assumes timeB is after timeA"""
    if timeB < timeA:
        timeB += 3600
    return timeB - timeA


def timeFormat(seconds):
    minutes = math.floor(seconds / 60)
    seconds -= minutes * 60
    minutes -= math.floor(minutes / 60) * 60
    return(str(minutes).zfill(2) + ":" + str(seconds).zfill(2))


def timeSlot(time, timeStep):
    return time - time % timeStep