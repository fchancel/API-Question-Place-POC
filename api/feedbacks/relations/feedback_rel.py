from neomodel import DateTimeProperty, StructuredRel


class GivenRelation(StructuredRel):
    pass


class ReceveidRelation(StructuredRel):
    date = DateTimeProperty(default_now=True)


class ConcernRelation(StructuredRel):
    pass


class FromRelation(StructuredRel):
    pass


class ExtendedBy(StructuredRel):
    pass
