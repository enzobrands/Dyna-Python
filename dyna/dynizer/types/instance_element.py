from ...common.errors import *
from .data_element import DataElement

class InstanceElement:
    def __init__(self, value=None, datatype=None, descriptive_actions=None):
        self.dataelement = DataElement(value=value, datatype=datatype)
        self.descriptive_actions = descriptive_actions

    @staticmethod
    def from_dict(dct):
        element = None
        try:
            de = DataElement.from_dict(dct)
            element = InstanceElement(descriptive_actions=dct['descriptive_actions'])
            element.dataelement = de
        except Exception as e:
            raise DeserializationError(InstanceElement, 'dict', dct) from e
        return element

    def to_dict(self):
        dct = {}
        try:
            dct = self.dataelement.to_dict()
            dct['descriptive_actions'] = [] if self.descriptive_actions is None else self.descriptive_actions
        except Exception as e:
            raise SerializationError(InstanceElement, 'dict') from e
        return dct

