from ...common.decorators import *
from ...common.errors import *
import json

@valid_field_filters('id', 'components')
class Topology:
    def __init__(self, id=None, components=None, labels=None, constraining_actions=None, applying_actions=None):
        self.id = id
        self.components = components
        self.labels = labels
        self.constraining_actions = constraining_actions
        self.applying_actions = applying_actions

    @staticmethod
    def from_dict(dct):
        retval = None
        try:
            if type(dct).__name__ == 'list':
                retval = []
                for d in dct:
                    retval.append(Topology.from_dict(d))
            else:
                retval = Topology(dct.get('id', None),
                                  list(map(ComponentType.from_string, dct['components'])) if 'components' in dct else None,     # !!! TEMPORARY FIX !!!
                                  dct.get('labels', None),
                                  dct.get('constraining_actions', None),
                                  dct.get('applying_actions', None))
        except Exception as e:
            raise DeserializationError(Topology, 'dict', dct) from e
        return retval


    @staticmethod
    def from_json(json_string):
        retval = None
        try:
            data = json.loads(json_string)
            retval = Topology.from_dict(data)
        except Exception as e:
            raise DeserializationError(Topology, 'json', json_string) from e
        return retval

    def to_dict(self, include_components=True, include_labels=True, include_constraining=True, include_applying=True):
        dct = None
        try:
            dct = {}
            if self.id is not None:
                dct['id'] = self.id
            if include_components and self.components is not None:
                dct['components'] = list(map(str, self.components))
            if include_labels and self.labels is not None:
                dct['labels'] = self.labels
            if include_constraining and self.constraining_actions is not None:
                dct['constraining_actions'] = self.constraining_actions
            if include_applying and self.applying_actions is not None:
                dct['applying_actions'] = self.applying_actions
        except Exception as e:
            raise SerializationError(Topology, 'dict') from e
        return dct


    def to_json(self, include_components=True, include_labels=True, include_constraining=True, include_applying=True):
        json_string = ""
        try:
            dct = self.to_dict(include_components, include_labels, include_constraining, include_applying)
            json_string = json.dumps(dct)
        except Exception as e:
            raise SerializationError(Topology, 'json') from e
        return json_string



