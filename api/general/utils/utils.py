
from neomodel import StructuredNode


def field_in_node_model(fields: list[str], model: StructuredNode):
    model_fields = [x for x in model.__dict__.keys() if not x.startswith("__")]
    return set(fields) & set(model_fields)
