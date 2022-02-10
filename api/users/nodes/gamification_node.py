from general.nodes.base_node import NodeBase
from neomodel import FloatProperty, IntegerProperty


class GamificationNode(NodeBase):
    level = IntegerProperty(default=0)
    experience = FloatProperty(default=0.0)
