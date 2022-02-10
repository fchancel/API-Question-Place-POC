from general.nodes.base_node import NodeBase
from neomodel import StringProperty, db


class DistinctionNode(NodeBase):
    name = StringProperty(required=True)

    @classmethod
    def get_node_with_name(cls, name):
        return cls.nodes.first_or_none(name=name)

    @classmethod
    def get_distinctions_number(cls, username):
        params = {'username': username}
        results, meta = db.cypher_query("""
            MATCH (user:UserNode)-[:RECEIVED]->(feedback:FeedbackNode)-[:EXTENDED_BY]->(distinction:DistinctionNode)
            WHERE user.username = $username
            RETURN distinction.name, count(distinction)""", params)

        if len(results) > 0:
            distinctions = [row[0] for row in results]
            numbers = [row[1] for row in results]
            return {
                'distinctions': distinctions,
                'numbers': numbers
            }
        else:
            return None
