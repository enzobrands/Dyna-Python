from ...common.decorators import *
from ...common.errors import *
from .instance_element import InstanceElement
from .topology import Topology
import json
import dateutil.parser

@valid_field_filters('id', 'action_id', 'topology_id')
class Instance:
    def __init__(self, id=None, timestamp=None, status=None, action_id=None, topology_id=None, data=None):
        self.id = id
        self.timestamp = timestamp
        self.status = status
        self.action_id = action_id
        self.topology_id = topology_id
        self.data = data

    @staticmethod
    def from_dict(dct):
        retval = None
        try:
            if type(dct).__name__ == 'list':
                retval = []
                for d in dct:
                    retval.append(Instance.from_dict(d))
            else:
                ts = dct.get('timestamp', None)
                retval = Instance(dct.get('id', None),
                                  dateutil.parser.parse(ts) if ts is not None else None,
                                  dct.get('status', None),
                                  dct['action_id'],
                                  dct['topology_id'],
                                  list(map(InstanceElement.from_dict, dct['data'])))
        except Exception as e:
            raise DeserializationError(Instance, 'dict', dct) from e
        return retval

    @staticmethod
    def from_json(json_string):
        instance = None
        try:
            data = json.loads(json_string)
            instance = Instance.from_dict(data)
        except Exception as e:
            raise DeserializationError(Instance, 'json', data) from e
        return instance

    def to_dict(self):
        dct = None
        try:
            dct = {
                'action_id': self.action_id,
                'topology_id': self.topology_id,
                'data': list(map(lambda o: o.to_dict(), self.data))
            }
            if self.id is not None:
                dct['id'] = self.id
            if self.timestamp is not None:
                dct['timstamp'] = str(self.timestamp)
            if self.status is not None:
                dct['status'] = self.status
        except Exception as e:
            raise SerializationError(Topology, 'dict') from e
        return dct


    def to_json(self):
        json_string = ""
        try:
            dct = self.to_dict()
            json_string = json.dumps(dct)
        except Exception as e:
            raise SerializationError(Topology, 'json') from e
        return json_string

