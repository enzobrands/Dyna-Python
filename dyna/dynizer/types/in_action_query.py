from ...common.decorators import *
from ...common.errors import *
from enum import IntEnum
from .data_element import DataElement
from decimal import *
import json
import dateutil.parser

class InActionQueryValue:
    def __init__(self, value=None, datatype=None, textsearch=False, position=None):
        if type(value) == DataElement:
            self.dataelement = value
        else:
            self.dataelement = DataElement(value=value, datatype=datatype)
        self.textsearch = textsearch
        self.position = position

    @staticmethod
    def from_dict(dct):
        val = None
        try:
            de = DataElement.from_dict(dct)
            val = InActionQueryValue(value=de,
                                     textsearch=get(dct, 'textsearch', false),
                                     position=get(dct, 'position', None))
        except Exception as e:
            raise DeserializationError(InstanceElement, 'dict', dct) from e
        return val

    def to_dict(self):
        dct = {}
        try:
            dct = self.dataelement.to_dict()
            dct['textsearch'] = self.textsearch
            if not self.position is None:
                dct['position'] = self.position
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
                    retval.append(InActionQuery.from_dct(d))
            else:
                and_set = list(map(InActionQueryValue.from_dict, dct['and'])) if 'and' in dct else None
                or_set = list(map(InActionQueryValue.from_dict, dct['or'])) if 'or' in dct else None
                not_set = list(map(InActionQueryValue.from_dict, dct['not'])) if 'not' in dct else None

                retval = InActionQuery(and_set, or_set, not_set,
                                       dct.get('action_id', None),
                                       dct.get('toplogy_id', None))
        except Exception as e:
            raise DeserializationError(InActionQuery, 'dict', dct) from e
        return retval


    @staticmethod
    def from_json(json_string):
        query = None
        try:
            data = json.loads(json_string)
            query = InActionQuery.from_dict(data)
        except Exception as e:
            raise DeserializationError(InActionQuery, 'json', json_string) from e
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
            raise SerializationError(InActionQuery, 'dict') from e
        return dct

    def to_json(self):
        json_string = ""
        try:
            dct = self.to_dict()
            json_string = json.dumps(dct)
        except Exception as e:
            raise SerializationError(InActionQuery, 'json') from e
        return json_string

