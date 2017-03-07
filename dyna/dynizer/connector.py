from ..common.decorators import *
from ..common.errors import *
from .types import *
import http.client
from enum import Enum, IntEnum
import urllib
import re


class FilterOperator(Enum):
    EQ = 1
    LT = 2
    LTEQ = 3
    GT = 4
    GTEQ = 5
    NEQ = 6
    TSRCH = 7

    @staticmethod
    @static_func_vars(trmap={
        1: '=',
        2: '<',
        3: '<=',
        4: '>',
        5: '>=',
        6: '!=',
        7: '~='
    })
    def __to_str(v):
        return FilterOperator.__to_str.trmap[int(v)]

    def __str__(self):
        return FilterOperator.__to_str(self.value)

    def to_url_operator(self):
        if self.value == FilterOperator.EQ.value:
            return ''
        else:
            return FilterOperator.__to_str(self.value)

    @classmethod
    @static_func_vars(trmap={
        '=': 'EQ',
        '<': 'LT',
        '<=': 'LTEQ',
        '>': 'GT',
        '>=': 'GTEQ',
        '!=': 'NEQ',
        '~=': 'TSRCH'
    })
    def from_string(cls, string):
        op_name = FilterOperators.from_string.trmap[string]
        for name, member in cls.__member__.items():
            if name == op_name:
                return member
        raise TranslateError(FilterOperators, string)




class Filter:
    def __init__(self):
        pass

    def compose_filter(self, cls):
        pass

class FieldFilter(Filter):
    def __init__(self, field, op, value):
        self.field = field
        self.op = op
        self.value = value

    def compose_filter(self, cls):
        FieldFilter.__validate_field(cls, self.field)
        # Exception for components filter on Topology class
        if cls.__name__ == Topology.__name__ and self.field == 'components':
            return "{0}={1}'{2}'".format(self.field, self.op.to_url_operator(), self.value)
        else:
            return '{0}={1}{2}'.format(self.field, self.op.to_url_operator(), urllib.parse.quote(self.value))

    @staticmethod
    def __validate_field(cls, field):
        if not cls._can_filter_on(field):
            raise FilterError(cls, field)

class PaginationFilter(Filter):
    def __init__(self, offset, limit):
        self.offset = offset
        self.limit = limit

    def compose_filter(self, cls):
        return 'offset={0}&limit={1}'.format(self.offset, self.limit)








class DynizerConnection:
    def __init__(self, address, port=80, endpoint_prefix='/api'):
        self.dynizer_address = '{0}:{1}'.format(address,port)
        self.endpoint_prefix = endpoint_prefix
        self._headers = {
            'cache-control': 'no-cache',
            'content-type': 'application/json'
        }

    # Functions that operate on partially of fully populated objects
    def create(self, obj):
        f = self.__get_function_handle_for_obj('create', obj)
        return f(obj)

    def read(self, obj):
        f = self.__get_function_handle_for_obj('read', obj)
        return f(obj)

    def udate(self, obj):
        f = self.__get_function_handle_for_obj('update', obj)
        return f(obj)

    def delete(self, obj):
        f = self.__get_function_handle_for_obj('delete', obj)
        return f(obj)

    def link_actiontopology(self, action, topology, labels=None):
        return self.__link_ActionTopology(action, topology)

    def update_actiontopology(self, action, topology):
        return self.__update_ActionTopology(action, topology)

    # Functions that operate based on classes
    def list(self, type, field_filters=None, pagination_filter=None):
        f = self.__get_function_handle_for_class('list', type)
        return f(field_filters, pagination_filter)

    # Query functions
    def query(self, query, pagination_filter=None):
        f = self.__get_function_handle_for_obj('query', query)
        return f(query, pagination_filter)



    def __get_function_handle_for_obj(self, op, obj):
        func_name = '_{0}__{1}_{2}'.format(self.__class__.__name__, op, obj.__class__.__name__)
        return self.__get_dispatch_func(func_name)

    def __get_function_handle_for_class(self, op, cls):
        _regex=re.compile('ys$')
        _replace='ies'
        func_name = _regex.sub(_replace, '_{0}__{1}_{2}s'.format(self.__class__.__name__, op, cls.__name__))
        return self.__get_dispatch_func(func_name)

    def __get_dispatch_func(self, func_name):
        func = None
        try:
            func = getattr(self, func_name)
        except Exception as e:
            raise DispatchError(obj, op) from e
        return func


    @staticmethod
    def __build_url_with_arguments(cls, url, field_filters=None, pagination_filter=None):
        filters = ''
        pagination = ''
        if field_filters is not None:
            filters = '&'.join(list(map(lambda o: o.compose_filter(cls), field_filters)))
        if pagination_filter is not None:
            pagination = pagination_filter.compose_filter(cls)

        if field_filters is not None:
            if pagination_filter is not None:
                return '{0}?{1}&{2}'.format(url, filters, pagination)
            else:
                return '{0}?{1}'.format(url, filters)
        else:
            if pagination_filter is not None:
                return '{0}?{1}'.format(url, pagination)
        return url





    def __create_DataElement(self, obj):
        return self.__POST('/data/v1_1/dataelements', obj.to_json(), DataElement)

    def __read_DataElement(self, obj):
        return self.__GET('/data/v1_1/dataelements/{0}'.format(obj.id), DataElement)

    def __list_DataElements(self, field_filters, pagination_filter):
        url = DynizerConnection.__build_url_with_arguments(DataElement, '/data/v1_1/dataelements', field_filters, pagination_filter)
        return self.__GET(url, DataElement)

    def __create_Action(self, obj):
        return self.__POST('/data/v1_1/actions', obj.to_json(), Action)

    def __read_Action(self, obj):
        return self.__GET('/data/v1_1/actions/{0}'.format(obj.id), Action)

    def __list_Actions(self, field_filters, pagination_filter):
        url = DynizerConnection.__build_url_with_arguments(Action, '/data/v1_1/actions', field_filters, pagination_filter)
        return self.__GET(url, Action)

    def __create_Topology(self, obj):
        return self.__POST('/data/v1_1/topologies', obj.to_json(), Topology)

    def __read_Topology(self, obj):
        return self.__GET('/data/v1_1/topologies/{0}'.format(obj.id), Topology)

    def __list_Topologies(self, field_filters, pagination_filter):
        url = DynizerConnection.__build_url_with_arguments(Topology, '/data/v1_1/topologies', field_filters, pagination_filter)
        return self.__GET(url, Topology)

    def __link_ActionTopology(self, action, topology):
        data = topology.to_json(include_components=False,
                                include_labels=True,
                                include_constraining=True,
                                include_applying=True)
        return self.__POST('/data/v1_1/actions/{0}/topologies'.format(action.id), data, Topology)

    def __update_ActionTopology(self, action, topology):
        data = topology.to_json(include_components=False,
                                include_labels=True,
                                include_constraining=True,
                                include_applying=True)
        return self.__patch('/data/v1_1/actions/{0}/topologies/{1}'.format(action.id, topology.id), data, Topology)


    def __create_Instance(self, obj):
        return self.__POST('/data/v1_1/instances', obj.to_json(), Instance)

    def __read_Instance(self, obj):
        return self.__GET('/data/v1_1/instances/{0}'.format(obj.id), Instance)

    def __update_Instance(self, obj):
        return self.__PUT('/data/v1_1/instances/{0}'.format(obj.id), obj.to_json(), Instance)

    def __delete_Instance(self, obj):
        return self.__DELETE('/data/v1_1/instances/{0}'.format(obj.id), Instance)

    def __list_Instances(self, field_filters, pagination_filter):
        url = DynizerConnection.__build_url_with_arguments(Instance, '/data/v1_1/instances', field_filters, pagination_filter)
        return self.__GET(url, Instance)

    def __query_InActionQuery(self, query, pagination_filter):
        actionres = None
        topologyres = None
        instanceres = None
        json = query.to_json()
        if (query.query_results & InActionQueryResult.ACTIONS) == InActionQueryResult.ACTIONS:
            url = DynizerConnection.__build_url_with_arguments(Action, '/data/v1_1/actionquery', None, pagination_filter)
            actionres = self.__POST(url, json, Action, success_code=200)
        if (query.query_results & InActionQueryResult.TOPOLOGIES) == InActionQueryResult.TOPOLOGIES:
            url = DynizerConnection.__build_url_with_arguments(Topology, '/data/v1_1/topologyquery', None, pagination_filter)
            topologyres = self.__POST(url, json, Topology, success_code=200)
        if (query.query_results & InActionQueryResult.INSTANCES) == InActionQueryResult.INSTANCES:
            url = DynizerConnection.__build_url_with_arguments(Instance, '/data/v1_1/instancequery', None, pagination_filter)
            instanceres = self.__POST(url, json, Instance, success_code=200)
        return (actionres, topologyres, instanceres)



    def __POST(self, endpoint, payload, result_obj=None, success_code=201):
        return self.__REQUEST('POST', endpoint, payload, result_obj, success_code)

    def __PUT(self, endpoint, payload, result_obj=None, success_code=200):
        return self.__REQUEST('PUT', endpoint, payload, result_obj, success_code)

    def __PATCH(self, endpoint, payload, result_obj=None, success_code=200):
        return self.__REQUEST('PATCH', endpoint, payload, result_obj, success_code)

    def __GET(self, endpoint, result_obj=None, success_code=200):
        return self.__REQUEST('GET', endpoint, result_obj=result_obj, success_code=success_code)

    def __DELETE(self, endpoint, result_obj=None, success_code=204):
        return self.__REQUEST('DELETE', endpoint, resultobj=reult_obj, success_code=success_code)


    def __REQUEST(self, verb, endpoint, payload=None, result_obj=None, success_code=200):
        conn = http.client.HTTPConnection(self.dynizer_address)
        url = '{0}{1}'.format(self.endpoint_prefix, endpoint)
        response = None
        try:
            if payload is not None:
                conn.request(verb, url, body=payload, headers=self._headers)
            else:
                conn.request(verb, url, headers=self._headers)
            response = conn.getresponse()
        except Exception as e:
            conn.close()
            raise ConnectionError() from e

        if response.status != success_code:
            raise RequestError(response.status, response.reason)

        result = None
        if result_obj is not None:
            try:
                bytestr = response.read()
                json_string = bytestr.decode(response.headers.get_content_charset('utf-8'))
                result = result_obj.from_json(json_string)
            except Exception as e:
                raise ResponseError() from e
                conn.close()

        conn.close()
        return result



