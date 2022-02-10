from general.nodes.base_node import NodeBase
from general.utils.utils import field_in_node_model
from neomodel import (BooleanProperty, EmailProperty, Relationship,
                      RelationshipTo, StringProperty, UniqueIdProperty, db)
from passlib.context import CryptContext
from users.nodes.gamification_node import GamificationNode
from users.nodes.profile_node import ProfileNode
from users.nodes.statistic_profile_node import StatisticProfileNode
from users.relations.users_rel import (ExtendedByRelation, FollowedByRelation,
                                       FollowRelation, IsFriendRelation,
                                       blockedRelation)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserNode(NodeBase):
    uid = UniqueIdProperty()
    email = EmailProperty(unique_index=True, required=True)
    username = StringProperty(unique_index=True, required=True)
    last_name = StringProperty(required=True)
    password = StringProperty(required=True)
    first_name = StringProperty(required=True)
    private_profile = BooleanProperty(default=False)
    is_active = BooleanProperty(default=True)
    email_verified = BooleanProperty(default=False)
    is_verified = BooleanProperty(default=False)
    picture = StringProperty(default='media/picture/default.jpg')

    profile = RelationshipTo(ProfileNode, 'EXTENDED_BY', model=ExtendedByRelation)
    gamification = RelationshipTo(GamificationNode, 'EXTENDED_BY', model=ExtendedByRelation)
    statistic_profile = RelationshipTo(StatisticProfileNode, 'EXTENDED_BY', model=ExtendedByRelation)

    blocked = Relationship('UserNode', 'BLOCKED', model=blockedRelation)
    friend = Relationship('UserNode', 'IS_FRIEND', model=IsFriendRelation)
    follow = RelationshipTo('UserNode', 'FOLLOW', model=FollowRelation)
    followed_by = RelationshipTo('UserNode', 'FOLLOWED_BY', model=FollowedByRelation)

    @classmethod
    def get_node_with_uid(cls, uid):
        return cls.nodes.first_or_none(uid=uid)

    @classmethod
    def get_node_with_email(cls, email):
        return cls.nodes.first_or_none(email=email)

    @classmethod
    def get_node_with_username(cls, username, need_active: bool = False, need_email_verified: bool = False):
        return cls.nodes.first_or_none(username=username)

    @classmethod
    def get_user_actif_only_with_username(cls, username):
        return cls.nodes.first_or_none(username=username, is_active=True, email_verified=True)

    def verify_password(self, plain_password):
        return pwd_context.verify(plain_password, self.password)

    @classmethod
    def get_user_full_profile(cls, username):
        user = cls.nodes.first_or_none(username=username)
        if user:
            response = user.dict()

            profile = user.profile.single().dict()
            response = dict(response, **profile)

            stat_profile = user.statistic_profile.single().dict()
            response = dict(response, **stat_profile)

            return response
        return None

    @classmethod
    def search_profile(cls, query: str, limit: int = 10, fields: list[str] = None):
        """
        Notes: The equivalent with neomodel is 10x times slower. Mainly because we have
        to loop over all retrieved users for quering their profiles and statistics.
        """
        import time
        start = time.time()

        match_profile = match_stat = ''
        if not fields or field_in_node_model(fields, ProfileNode):
            match_profile = 'MATCH (u)-[:EXTENDED_BY]->(p:ProfileNode)'
        if not fields or field_in_node_model(fields, StatisticProfileNode):
            match_stat = 'MATCH (u)-[:EXTENDED_BY]->(s:StatisticProfileNode)'

        results, _ = db.cypher_query(f"""
                MATCH (u:UserNode) {match_profile} {match_stat}
                WHERE toLower(u.first_name) STARTS WITH toLower($query)
                OR toLower(u.last_name) STARTS WITH toLower($query)
                RETURN *
                LIMIT {limit}
                """, {"query": query})
        profile_list = []

        for result in results:
            user = {}
            # Here result is a list of 3 dicts : UserNode, ProfileNode, StatisticProfileNode
            for r in result:
                user = dict(user, **r)

            filtered_user = {}
            for field in fields:
                filtered_user[field] = user[field]
            profile_list.append(filtered_user)
        print(f'Search user by term: "{query}":  {time.time() - start}')
        return profile_list
