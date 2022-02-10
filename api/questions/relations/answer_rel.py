from neomodel import (BooleanProperty, DateTimeProperty, StringProperty,
                      StructuredRel)


class VotedRel(StructuredRel):
    type_vote = StringProperty(required=True)


class CreatedRel(StructuredRel):
    created = DateTimeProperty(default_now=True)
    edited = DateTimeProperty()


class CommentRel(StructuredRel):
    pass


class AnswerRel(StructuredRel):
    pass


class ValidatedRel(StructuredRel):
    deprecated = BooleanProperty(default=False)
