from ...common.decorators import *
from ...common.errors import *
from enum import IntEnum
from .data_element import DataElement
from decimal import *
import json
import dateutil.parser

class CorrelationQueryValue:
    def __init__(self, value=None, datatype=None):
        if type(value) == DataElement:
            self.dataelement = value
        else:
            self.dataelement = DataElement(value=value, datatype=datatype)

    @staticmethod
    def from_dict(dct):
        val = None
        try:
            de = DataElement.from_dict(dct)
            val = InActionQueryValue(value=de)
        except Exception as e:
            raise DeserializationError(CorrelationQueryValue, 'dict', dct) from e
        return val

    def to_dict(self):
        dct = {}
        try:
            dct = self.dataelement.to_dict()
        except Exception as e:
            raise SerializationError(CorrelationQueryValue, 'dict') from e
        return dct


class CorrelationQueryResult(IntEnum):
    INSTANCE = 1
    ACTION = 2
    TOPOLOGY = 4

    def to_string_list(val):
        lst = []
        if (val&CorrelationQueryResult.INSTANCE) == CorrelationQueryResult.INSTANCE:
            lst.append("Instance")
        if (val&CorrelationQueryResult.ACTION) == CorrelationQueryResult.ACTION:
            lst.append("Action")
        if (val&CorrelationQueryResult.TOPOLOGY) == CorrelationQueryResult.TOPOLOGY:
            lst.append("Topology")
        return lst


    @staticmethod
    def from_string_list(lst):
        val = 0
        for e in lst:
            if e == "Instance":
                val |= CorrelationQueryResult.INSTANCE
            elif e == "Action":
                val |= CorrelationQueryResult.ACTION
            elif e == "Topology":
                val |= CorrelationQueryResult.TOPOLOGY
        return val


class CorrelationQuery:
    def __init__(self, elements=None, query_results=CorrelationQueryResult.INSTANCE):
        self.elements = elements
        self.query_results = query_results

    @staticmethod
    def from_dict(dct):
        retval = None
        try:
            if type(dct).__name__ == 'list':
                retval = []
                for d in dct:
                    retval.append(CorrelationQuery.from_dct(d))
            else:
                elements = list(map(CorrelationQueryValue.from_dict, dct['data'])) if 'data' in dct else None
                query_result = CorrelationQueryResult.from_string_list(dct.get('link', []))
                retval = CorrelationQuery(elements, query_results)
        except Exception as e:
            raise DeserializationError(CorrelationQuery, 'dict', dct) from e
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


