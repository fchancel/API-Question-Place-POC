from neomodel import DateTimeProperty, StructuredRel


class CreatedRel(StructuredRel):
    created = DateTimeProperty(default_now=True)
    edited = DateTimeProperty()
