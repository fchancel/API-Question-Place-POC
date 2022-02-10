from neomodel import DateTimeProperty, StructuredRel


class WhereQuestion(StructuredRel):
    pass


class CreatedRel(StructuredRel):
    created = DateTimeProperty(default_now=True)
    edited = DateTimeProperty()


class FollowRel(StructuredRel):
    created = DateTimeProperty(default_now=True)
