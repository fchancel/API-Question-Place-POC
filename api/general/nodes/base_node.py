from neomodel import StructuredNode


class NodeBase(StructuredNode):
    __abstract_node__ = True

    def dict(self):
        return self.__properties__
