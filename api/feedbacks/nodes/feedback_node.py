from feedbacks.nodes.distinction_node import DistinctionNode
from feedbacks.relations.feedback_rel import (ConcernRelation, ExtendedBy,
                                              FromRelation, GivenRelation,
                                              ReceveidRelation)
from general.nodes.base_node import NodeBase
from neomodel import (IntegerProperty, RelationshipFrom, RelationshipTo,
                      StringProperty, db)
from places.nodes.place_node import PlaceNode
from users.nodes.user_node import UserNode


class FeedbackNode(NodeBase):
    rating = IntegerProperty(required=True)
    comment = StringProperty(required=True)

    user_given = RelationshipFrom(UserNode, 'GIVEN', model=GivenRelation)
    user_receveid = RelationshipFrom(UserNode, 'RECEIVED', model=ReceveidRelation)

    distinction = RelationshipTo(DistinctionNode, 'EXTENDED_BY', model=ExtendedBy)
    place = RelationshipTo(PlaceNode, 'FROM', model=FromRelation)

    @classmethod
    def create_and_save(cls, rating: int, comment: str):
        feedback_node = cls(rating=rating, comment=comment)
        feedback_node.save()
        return feedback_node

    @classmethod
    def get_feedbacks(cls, receiver: bool, username: str, skip: int, limit: int, sort_by: str, desc: str) -> dict:
        if receiver:
            user_match = 'user'
        else:
            user_match = 'user1'

        params = {
            'username': username,
            'skip': skip,
            'limit': limit
        }
        results, meta = db.cypher_query(f"""
            MATCH (user:UserNode)-[rel:RECEIVED]->(feedback:FeedbackNode)<-[:GIVEN]-(user1:UserNode)
            WITH count(feedback) as `total_feedback`, feedback, user, user1, rel
            (feedback)-[:EXTENDED_BY]->(distinction:DistinctionNode)
            WHERE {user_match}.username = $username
            RETURN feedback, rel.date, user1, place, distinction, total_feedback
            ORDER BY {sort_by} {desc}
            SKIP $skip
            LIMIT $limit
            """, params)

        if len(results) > 0:
            feedbacks = [cls.inflate(row[0]) for row in results]
            created_date = [row[1] for row in results]
            users = [UserNode.inflate(row[2]) for row in results]
            places = [PlaceNode.inflate(row[3]) for row in results]
            distinctions = [DistinctionNode.inflate(row[5]) for row in results]
            total_feedbacks = results[0][6]

            return {
                'feedbacks': feedbacks,
                'created_date': created_date,
                'users': users,
                'places': places,
                'distinctions': distinctions,
                'total_feedbacks': total_feedbacks
            }
        else:
            return None

    @classmethod
    def get_how_many_feedbacks(cls, receiver: bool, username: str):
        if receiver:
            relation = 'RECEIVED'
        else:
            relation = 'GIVEN'
        params = {'username': username}
        results, meta = db.cypher_query(f"""
            MATCH (user:UserNode)-[rel:{relation}]->(feedback:FeedbackNode)
            WHERE user.username = $username
            RETURN count(feedback) as `nb`
        """, params)
        if results[0][0] == 0:
            return None
        else:
            return results[0][0]

    @classmethod
    def get_how_many_rating(cls, username: str):
        params = {'username': username}
        results, meta = db.cypher_query("""
            MATCH (user:UserNode)-[:RECEIVED]->(feedback:FeedbackNode)
            WHERE user.username = $username
            RETURN feedback.rating, count(feedback.rating)
            ORDER BY feedback.rating DESC""", params)

        if len(results) > 0:
            ratings = [row[0] for row in results]
            numbers = [row[1] for row in results]
            return {
                'ratings': ratings,
                'numbers': numbers
            }
        else:
            return None
