from datetime import date

from general.nodes.base_node import NodeBase
from neomodel import (DateProperty, DateTimeProperty, FloatProperty,
                      IntegerProperty)


class StatisticProfileNode(NodeBase):
    response_time = IntegerProperty()  # average response time in seconds
    response_rate = IntegerProperty()  # response rate in percents
    rating = FloatProperty()
    last_connection = DateTimeProperty()
    date_joined = DateProperty(default=lambda: date.today())
