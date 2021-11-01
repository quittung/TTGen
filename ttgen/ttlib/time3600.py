"""Handles time that wraps around after an hour."""
import math


def timeShift(time: float, delta:float) -> float:
    """Shifts time by a specified time delta.
        Takes time wrap into account.

    Args:
        time (float): Start time.
        delta (float): Time delta relative to start time.

    Returns:
        float: Resulting time.
    """    
    return (time + delta) % 3600


def timeDiff(timeA: float, timeB: float) -> float:
    """Calculates difference between to time points.
        Assumes timeB occured after timeA.
        Takes time wrap into account.
        Does not support time delta greater than 2 h.

    Args:
        timeA (float): First time point.
        timeB (float): Second time point.

    Returns:
        float: Time delta.
    """    
    if timeB < timeA:
        timeB += 3600
    return timeB - timeA


def timeFormat(time: float) -> str:
    """Formats time in mm:ss format.

    Args:
        time (float): Reference time.

    Returns:
        str: Formatted time.
    """    
    seconds  = time
    minutes = math.floor(seconds / 60)
    seconds -= minutes * 60
    minutes -= math.floor(minutes / 60) * 60

    return(str(minutes).zfill(2) + ":" + str(seconds).zfill(2))


def timeSlot(time: float, timeStep: int) -> int:
    """Gets time slot for time.

    Args:
        time (float): Reference time.
        timeStep (int): Time delta between slots.

    Returns:
        int: Corresponding time slot.
    """    
    return time - time % timeStep