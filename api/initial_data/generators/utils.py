import math
import random
from datetime import datetime, timedelta


def random_datetime(delta: timedelta, reference: datetime = datetime.now()) -> datetime:
    """
        :param delta: the time delta from the reference
        :param reference: the date from which the delta will be subtracted, defalut: now
        :return: a datetime from date_max
        """
    seconds = random.randint(0, math.trunc(delta.total_seconds()))
    # print(f'generate random datetime between {(reference - delta).year} to {reference.year}')
    return reference - timedelta(seconds=seconds)


def random_timedelta(max_time: timedelta) -> timedelta:
    return timedelta(seconds=random.randint(0, math.trunc(max_time.total_seconds())))
