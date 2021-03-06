from ..common.decorators import *
from ..common.errors import *
from .types import *
from .filters import *
import http.client
from enum import Enum, IntEnum
import urllib
import re


class DynizerConnection:
    def __init__(self, address, port=None, endpoint_prefix=None, https=False,
                 key_file=None, cert_file=None, username=None, password=None):
        self.dynizer_address = address
        if port == None:
            self.dynizer_port = 80 if https == False else 443
        else:
            self.dynizer_port = port
        self.endpoint_prefix = '' if endpoint_prefix is None else endpoint_prefix
        self.https = https
        self.key_file = key_file
        self.cert_file = cert_file
        self._headers = {
            'cache-control': 'no-cache',
            'content-type': 'application/json'
        }
        self.connection = None

    def __del__(self):
        self.close()

    def connect(self, reconnect=False):
        if not self.connection is None:
            if not reconnect:
                return
            else:
                self.close()

        if self.https:
            self.connection = http.client.HTTPSConnection(
                    self.dynizer_address, self.dynizer_port,
                    key_file=self.key_file, cert_file=self.cert_file)
        else:
            self.connection = http.client.HTTPConnection(self.dynizer_address, self.dynizer_port)


    def close(self):
        if not self.connection is None:
            self.connection.close()
            self.connection = None



    # Functions that operate on partially of fully populated objects
    def create(self, obj):
        f = self.__get_function_handle_for_obj('create', obj)
        return f(obj)

    def batch_create(self, obj_arr):
        f = self.__get_function_handle_for_obj('batch_create', obj_arr[0])
        return f(obj_arr)

    def read(self, obj):
        f = self.__get_function_handle_for_obj('read', obj)
        return f(obj)

    def update(self, obj):
        f = self.__get_function_handle_for_obj('update', obj)
        return f(obj)

    def delete(self, obj):
        f = self.__get_function_handle_for_obj('delete', obj)
        return f(obj)

    def link_actiontopology(self, action, topology, labels=None):
        if labels:
            topology.labels = labels
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
        func_name = _regex.sub(_replace, '_{0}__{1}_{2}s'.format(
            self.__class__.__name__, op, cls.__name__))
        return self.__get_dispatch_func(func_name)

    def __get_dispatch_func(self, func_name):
        func = None
        try:
            func = getattr(self, func_name)
        except Exception as e:
            raise DispatchError(obj, func_name) from e
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
        url = '/data/v1_1/dataelements'
        return self.__POST(url, obj.to_json(), DataElement)

    def __read_DataElement(self, obj):
        url = '/data/v1_1/datalements/{0}'.format(obj.id)
        return self.__GET(url, DataElement)

    def __list_DataElements(self, field_filters, pagination_filter):
        url = DynizerConnection.__build_url_with_arguments(
                DataElement, '/data/v1_1/dataelements', field_filters, pagination_filter)
        return self.__GET(url, DataElement)


    def __create_Action(self, obj):
        url = '/data/v1_1/actions'
        return self.__POST(url, obj.to_json(), Action)

    def __read_Action(self, obj):
        url = '/data/v1_1/actions/{0}'.format('' if obj.id is None else obj.id)
        return self.__GET(url, Action)

    def __list_Actions(self, field_filters, pagination_filter):
        url = DynizerConnection.__build_url_with_arguments(
                Action, '/data/v1_1/actions', field_filters, pagination_filter)
        return self.__GET(url, Action)

    def __create_Topology(self, obj):
        url = '/data/v1_1/topologies'
        return self.__POST(url, obj.to_json(), Topology)

    def __read_Topology(self, obj):
        url = '/data/v1_1/topologies/{0}'.format('' if obj.id is None else obj.id)
        return self.__GET(url, Topology)

    def __list_Topologies(self, field_filters, pagination_filter):
        url = DynizerConnection.__build_url_with_arguments(
                Topology, '/data/v1_1/topologies', field_filters, pagination_filter)
        return self.__GET(url, Topology)

    def __link_ActionTopology(self, action, topology):
        data = topology.to_json(include_components=False,
                                include_labels=True,
                                include_constraining=True,
                                include_applying=True)
        url = '/data/v1_1/actions/{0}/topologies'.format(action.id)
        return self.__POST(url, data, Topology)

    def __update_ActionTopology(self, action, topology):
        data = topology.to_json(include_components=False,
                                include_labels=True,
                                include_constraining=True,
                                include_applying=True)
        url = '/data/v1_1/actions/{0}/topologies/{1}'.format(
                action.id, '' if topology.id is None else topology.id)
        return self.__patch(url, data, Topology)


    def __create_Instance(self, obj):
        url = '/data/v1_1/instances'
        return self.__POST('/data/v1_1/instances', obj.to_json(), Instance)

    def __batch_create_Instance(self, obj_arr):
        json_arr = list(map(lambda x: x.to_json(), obj_arr))
        data = '['+','.join(json_arr)+']'
        url = '/data/v1_1/instances'
        return self.__POST(url, data, Instance)

    def __read_Instance(self, obj):
        url = '/data/v1_1/instances/{0}'.format('' if obj.id is None else obj.id)
        return self.__GET(url, Instance)

    def __update_Instance(self, obj):
        url = '/data/v1_1/instances/{0}'.format(obj.id)
        return self.__PUT(url, obj.to_json(), Instance)

    def __delete_Instance(self, obj):
        url = '/data/v1_1/instances/{0}'.format(obj.id)
        return self.__DELETE(url, Instance)

    def __list_Instances(self, field_filters, pagination_filter):
        url = DynizerConnection.__build_url_with_arguments(
                Instance, '/data/v1_1/instances', field_filters, pagination_filter)
        return self.__GET(url, Instance)

    def __query_InActionQuery(self, query, pagination_filter):
        actionres = None
        topologyres = None
        instanceres = None
        json = query.to_json()

        if (query.query_results & InActionQueryResult.ACTIONS) == InActionQueryResult.ACTIONS:
            url = DynizerConnection.__build_url_with_arguments(
                    Action, '/data/v1_1/actionquery', None, pagination_filter)
            actionres = self.__POST(url, json, Action, success_code=200)
        if (query.query_results & InActionQueryResult.TOPOLOGIES) == InActionQueryResult.TOPOLOGIES:
            url = DynizerConnection.__build_url_with_arguments(
                    Topology, '/data/v1_1/topologyquery', None, pagination_filter)
            topologyres = self.__POST(url, json, Topology, success_code=200)
        if (query.query_results & InActionQueryResult.INSTANCES) == InActionQueryResult.INSTANCES:
            url = DynizerConnection.__build_url_with_arguments(
                    Instance, '/data/v1_1/instancequery', None, pagination_filter)
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
        if self.connection is None:
            raise ConnectionError('Not connected to dynizer. Please issue a connect() call first')

        url = '{0}{1}'.format(self.endpoint_prefix, endpoint)
        response = None
        try:
            if payload is not None:
                self.connection.request(verb, url, body=payload, headers=self._headers)
            else:
                self.connection.request(verb, url, headers=self._headers)
            response = self.connection.getresponse()
        except Exception as e:
            self.connect(True)
            print('{0} {1}'.format(verb, url))
            if not payload is None:
                print(payload)
            print(e)
            raise ConnectionError() from e

        if response.status != success_code:
            print('{0} {1}'.format(verb, url))
            if not payload is None:
                print(payload)
            self.connect(True)
            raise RequestError(response.status, response.reason)


        result = None
        if result_obj is not None:
            try:
                bytestr = response.read()
                json_string = bytestr.decode(response.headers.get_content_charset('utf-8'))
                result = result_obj.from_json(json_string)
            except Exception as e:
                self.connect(True)
                print('{0} {1}'.format(verb, url))
                if not payload is None:
                    print(payload)
                print(e)
                raise ResponseError() from e

        return result

