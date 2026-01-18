import math

def prob_hour_to_prob_ms(p_hour: float):
    return 1-math.pow(1-p_hour,1/3600000)


def prob_hour_to_prob_sec(p_hour: float):
    return 1-math.pow(1-p_hour, 1/3600)

def prob_hour_to_prob_min(p_hour: float):
    return 1-math.pow(1-p_hour, 1/60)