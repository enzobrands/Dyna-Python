from ..common.decorators import *
from ..common.errors import *
from enum import IntEnum
from decimal import *
import json
import dateutil.parser

class ComponentType(IntEnum):
    WHO = 1
    WHAT = 2
    WHERE = 3
    WHEN = 4

    def __str__(self):
        return self.name.title()

    @classmethod
    def from_string(cls, string):
        u_string = string.upper()
        for name, member in cls.__members__.items():
            if name == u_string:
                return member
        raise ComponentError()


class DataType(IntEnum):
    INTEGER = 1
    STRING = 2
    BOOLEAN = 3
    DECIMAL = 4
    TIMESTAMP = 5
    URI = 6
    VOID = 7

    def __str__(self):
        return 'URI' if self == DataType.URI else '{0}'.format(self.name).title()

    @classmethod
    def from_string(cls, string):
        u_string = string.upper()
        for name, member in cls.__members__.items():
            if name == u_string:
                return member
        raise DatatypeError()



@valid_field_filters('id', 'value', 'datatype')
class DataElement:
    def __init__(self, id=None, value=None, datatype=None):
        self.id = id
        self.value = DataElement._format_input_value(datatype, value)
        self.datatype = datatype


    @staticmethod
    def _format_input_value(datatype, value):
        if datatype == DataType.INTEGER:
            return int(value)
        if datatype == DataType.STRING:
            return str(value)
        if datatype == DataType.BOOLEAN:
            return bool(value)
        if datatype == DataType.DECIMAL:
            return Decimal(value)
        if datatype == DataType.TIMESTAMP:
            if type(value).__name__ == 'str':
                return dateutil.parser.parse(value)
            if type(value).__name__ == 'date' :
                return datetime.datetime(value.year, value.month, value.day)
            if type(value).__name__ == 'time':
                td = datetime.today()
                return datetime.datetime(td.year, td.month, td.day, value.hour, value.minute, value.second, value.microsecond)
            if type(value).__name__ == 'datetime':
                return value
            return datetime.min
        if datatype == DataType.URI:
            return str(value)
        return None


    @staticmethod
    def _convertfrom_json(datatype, value):
        if datatype == DataType.INTEGER:
            return int(value)
        if datatype == DataType.STRING:
            return str(value)
        if datatype == DataType.BOOLEAN:
            return value
        if datatype == DataType.DECIMAL:
            return Decimal(value)
        if datatype == DataType.TIMESTAMP:
            return dateutil.parser.parse(value)
        if datatype == DataType.URI:
            return str(value)
        return None

    @staticmethod
    def _convert_to_json(datatype, value):
        if datatype == DataType.INTEGER:
            return int(value)
        if datatype == DataType.STRING:
            return str(value)
        if datatype == DataType.BOOLEAN:
            return 'true' if value else 'false'
        if datatype == DataType.DECIMAL:
            return str(value)
        if datatype == DataType.TIMESTAMP:
            return str(value.isoformat())
        if datatype == DataType.URI:
            return str(value)
        return 'Void'

    @staticmethod
    def from_dict(dct):
        retval = None
        try:
            if type(dct).__name__ == 'list':
                retval = []
                for d in dct:
                    retval.append(DataElement.from_dict(d))
            else:
                retval = DataElement(dct.get('id', None),
                                     DataElement._convertfrom_json(DataType.from_string(dct['datatype']), dct['value']),
                                     DataType.from_string(dct['datatype']))
        except Exception as e:
            raise DeserializationError(DataElement, 'dict', dct) from e
        return retval

    @staticmethod
    def from_json(json_string):
        retval = None
        try:
            data = json.loads(json_string)
            retval = DataElement.from_dict(data)
        except Exception as e:
            raise DeserializationError(DataElement, 'json', json_string) from e
        return retval


    def to_dict(self):
        dct = None
        try:
            dct = {
                    'value': DataElement._convert_to_json(self.datatype, self.value),
                    'datatype': str(self.datatype)
                  }
            if self.id is not None:
                dct['id'] = self.id
        except Exception as e:
            raise SerializationError(DataElement, 'dict') from e
        return dct

    def to_json(self):
        json_String = ""
        try:
            dct = self.to_dict()
            json_string = json.dumps(dct)
        except Exception as e:
            raise SerializationError(DataElement, 'json') from e
        return json_string







@valid_field_filters('id', 'name', 'actiontype')
class Action:
    def __init__(self, id=None, name=None, actiontype=None):
        self.id = id
        self.name = name
        self.actiontype = actiontype

    @staticmethod
    def from_dict(dct):
        retval = None
        try:
            if type(dct).__name__ == 'list':
                retval = []
                for d in dct:
                    retval.append(Action.from_dict(d))
            else:
                retval = Action(dct.get('id', None),
                                dct['name'],
                                dct['actiontype'])
        except Exception as e:
            raise DeserializationError(Action, 'dict', dct) from e
        return retval

    @staticmethod
    def from_json(json_string):
        retval = None
        try:
            data = json.loads(json_string)
            retval = Action.from_dict(data)
        except Exception as e:
            raise DeserializationError(Action, 'json', json_string) from e
        return retval

    def to_dict(self):
        dct = None
        try:
            dct = {
                    'name': self.name,
                    'actiontype': self.actiontype
                  }
            if self.id is not None:
                dct['id'] = self.id
        except Exception as e:
            raise SerializationError(Action, 'dict') from e
        return dct

    def to_json(self):
        json_string = ""
        try:
            dct = self.to_dict()
            json_string = json.dumps(dct)
        except Exception as e:
            raise SerializationError(Action, 'json') from e
        return json_string




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


class InstanceElement:
    def __init__(self, value=None, datatype=None, descriptive_actions=None):
        self.value = value
        self.datatype = datatype
        self.descriptive_actions = descriptive_actions

    @staticmethod
    def from_dict(dct):
        element = None
        try:
            element = InstanceElement(DataElement._convertfrom_json(DataType.from_string(dct['datatype']), dct['value']),
                                      DataType.from_string(dct['datatype']),
                                      dct['descriptive_actions'])
        except Exception as e:
            raise DeserializationError(InstanceElement, 'dict', dct) from e
        return element

    def to_dict(self):
        dct = {}
        try:
            if self.value is not None:
                dct['value'] = DataElement._convert_to_json(self.datatype if self.datatype is not None else DataType.STRING, self.value)
                dct['datatype'] = str(self.datatype) if self.datatype is not None else str(DataType.STRING)
            dct['descriptive_actions'] = [] if self.descriptive_actions is None else self.descriptive_actions
        except Exception as e:
            raise SerializationError(InstanceElement, 'dict') from e
        return dct




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
                dct['status'] = status
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


class InActionQueryValue:
    def __init__(self, value=None, datatype=None, textsearch=False):
        self.value = value
        self.datatype = datatype
        self.textsearch = textsearch

    @staticmethod
    def from_dict(dct):
        val = None
        try:
            val = InActionQueryValue(DataElement._convertfrom_json(DataType.from_string(dct['datatype']), dct['value']),
                                     DataType.from_string(dct['datatype']),
                                     True if get(dct, 'textsearch', 'false') == 'true' else False)
        except Exception as e:
            raise DeserializationError(InstanceElement, 'dict', dct) from e
        return val

    def to_dict(self):
        dct = {}
        try:
            if self.value is not None:
                dct['value'] = DataElement._convert_to_json(self.datatype if self.datatype is not None else DataType.STRING, self.value)
                dct['datatype'] = str(self.datatype) if self.datatype is not None else str(DataType.STRING)
            if self.textsearch:
                dct['textsearch'] = 'true'
        except Exception as e:
            raise SerializationError(InstanceElement, 'dict') from e
        return dct


class InActionQueryResult(IntEnum):
    INSTANCES = 1
    ACTIONS = 2
    TOPOLOGIES = 4


class InActionQuery:
    def __init__(self, and_set=None, or_set=None, not_set=None, action_filter=None, topology_filter=None, query_results=InActionQueryResult.INSTANCES):
        self.and_set = and_set
        self.or_set = or_set
        self.not_set = not_set
        self.action_filter = action_filter
        self.topology_filter = topology_filter
        self.query_results = query_results

    @staticmethod
    def from_dict(dct):
        retval = None
        try:
            if type(dct).__name__ == 'list':
                retval = []
                for d in dct:
                    retval.append(InActionQuery.from_dct(dct))
            else:
                and_set = list(map(InActionQueryValue.from_dict, dct['and'])) if 'and' in dct else None
                or_set = list(map(InActionQueryValue.from_dict, dct['or'])) if 'or' in dct else None
                not_set = list(map(InActionQueryValue.from_dict, dct['not'])) if 'not' in dct else None

                retval = InActionQuery(and_set, or_set, not_set,
                                       dct.get('action_id', None),
                                       dct.get('toplogy_id', None))
        except Exception as e:
            raise DeserializationError(Instance, 'dict', dct) from e
        return retval


    @staticmethod
    def from_json(json_string):
        query = None
        try:
            data = json.loads(json_string)
            query = InActionQuery.from_dict(data)
        except Exception as e:
            raise DeserializationError(Instance, 'json', json_string) from e
        return query

    def to_dict(self):
        dct = None
        try:
            dct = {}
            if self.and_set is not None:
                dct['and'] = list(map(lambda o: o.to_dict(), self.and_set))
            if self.or_set is not None:
                dct['or'] = list(map(lambda o: o.to_dict(), self.or_set))
            if self.not_set is not None:
                dct['not'] = list(map(lambda o: o.to_dict(), self.not_set))
            if self.action_filter is not None:
                dct['action_id'] = self.action_filter
            if self.topology_filter is not None:
                dct['topology_id'] = self.topology_filter
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



