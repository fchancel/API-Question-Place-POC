from neomodel import BooleanProperty, DateTimeProperty, StructuredRel


class blockedRelation(StructuredRel):
    since = DateTimeProperty(default_now=True)


class ExtendedByRelation(StructuredRel):
    pass


class FollowRelation(StructuredRel):
    since = DateTimeProperty(default_now=True)


class FollowedByRelation(StructuredRel):
    since = DateTimeProperty(default_now=True)


class IsFriendRelation(StructuredRel):
    accept = BooleanProperty(default=False)
    since = DateTimeProperty(default_now=True)
