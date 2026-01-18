import math



def prob_hour_to_prob_ms(p_hour: float):
    """
    Converts a probability to something happening in a hour to a probability of the same thing happening in a millisecond.
    
    Parameters:
    p_hour (float): Probability per hour.
    
    Returns:
    float: Probability per millisecond.
    """

    return 1-math.pow(1-p_hour,1/3600000)

def prob_hour_to_prob_sec(p_hour: float):
    """
    Converts a probability to something happening in a hour to a probability of the same thing happening in a second.
    
    Parameters:
    p_hour (float): Probability per hour.
    
    Returns:
    float: Probability per second.
    """
    return 1-math.pow(1-p_hour, 1/3600)

def prob_hour_to_prob_min(p_hour: float):
    """
    Converts a probability to something happening in a hour to a probability of the same thing happening in a minute.
    
    Parameters:
    p_hour (float): Probability per hour.
    
    Returns:
    float: Probability per minute.
    """
    return 1-math.pow(1-p_hour, 1/60)