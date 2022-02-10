from general.nodes.base_node import NodeBase
from neomodel import DateProperty, StringProperty


class ProfileNode(NodeBase):
    gender = StringProperty(required=True)
    birthdate = DateProperty(required=True)
    job = StringProperty()
    biography = StringProperty()
