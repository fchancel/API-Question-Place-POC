# import math
import random
from datetime import datetime, timedelta

from initial_data.generators.utils import random_datetime, random_timedelta
from users.nodes.statistic_profile_node import StatisticProfileNode
from users.nodes.user_node import UserNode

MAX_RESPONSE_TIME_DAYS = 3
MAX_TIME_SINCE_JOINED_YEARS = 5


def generate_statistic_profile(user: UserNode, verbose: bool = False):
    date_joined = random_datetime(timedelta(days=365 * MAX_TIME_SINCE_JOINED_YEARS))
    time_since_joined = datetime.now() - date_joined

    # the following code give more chance to an user to be rated up to 3.5.
    rating = None
    if random.randint(0, 3) == 0:
        rating = round(random.uniform(0, 3.5), 2)
    else:
        rating = round(random.uniform(3.5, 5), 2)

    sp = StatisticProfileNode(
        response_time=random_timedelta(timedelta(days=MAX_RESPONSE_TIME_DAYS)).total_seconds(),
        response_rate=random.randint(0, 100),
        rating=rating,
        last_connection=random_datetime(time_since_joined),
        date_joined=date_joined.date(),
    ).save()

    user.statistic_profile.connect(sp)

    if verbose:
        print(f"-> {user.username}")
        print(f'    response_time:   {timedelta(seconds=sp.response_time)}, response_rate: {sp.response_rate}%')
        print(f'    date_joined:     {sp.date_joined}, last_connection: {sp.last_connection}')
        print(f'    rating:          {sp.rating}')

    return sp
