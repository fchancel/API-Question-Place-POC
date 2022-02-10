from fastapi import HTTPException, status
from neomodel import IntegerProperty, StructuredNode


class MetaBase(StructuredNode):
    __abstract_node__ = True
    counter = IntegerProperty()

    @classmethod
    def get_node(cls):
        node = cls.nodes.first_or_none()
        if not node:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='meta node error')
        return node

    @classmethod
    def get_counter(cls):
        node = cls.get_node()
        return node.counter

    @classmethod
    def adding_one_counter(cls):
        node = cls.get_node()
        node.counter = node.counter + 1
        node.save()

    @classmethod
    def create_and_save_uid(cls, instance):
        counter = cls.get_counter()
        uid = str(counter) + str(instance.id)
        instance.uid = int(uid)
        instance.save()
        cls.adding_one_counter()
