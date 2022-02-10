from general.nodes.base_node import NodeBase
from neomodel import StringProperty


class PlaceNode(NodeBase):
    google_place_id = StringProperty(unique_index=True, required=True)

    @classmethod
    def get_node_with_google_place_id(cls, id):
        return cls.nodes.first_or_none(google_place_id=id)

    @classmethod
    def get_or_create_node_with_google_place_id(cls, id):
        node = cls.get_node_with_google_place_id(id)
        if not node:
            node = cls(google_place_id=id)
            node.save()
        return node
