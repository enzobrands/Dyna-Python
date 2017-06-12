from ..types import Action, ComponentType, DataElement, DataType, Instance, InstanceElement, Topology
from ..connector import DynizerConnection
from ...common.errors import LoaderError
from typing import Sequence
import csv

class CSVAbstractElement:
    def __init__(self, value,
                       data_type: DataType,
                       component: ComponentType,
                       label = ''):
        self.value = value
        self.data_type = data_type
        self.component = component
        self.label = label

    def fetch_from_row(self, row, components, data, labels):
        components.append(self.component)
        data.append(InstanceElement(value=self.value, datatype=self.data_type))
        labels.append(self.label)
        return True



class CSVFixedElement(CSVAbstractElement):
    def __init__(self, value,
                       data_type: DataType,
                       component: ComponentType,
                       label = ''):
        super().__init__(value, data_type, component, label)



class CSVRowElement(CSVAbstractElement):
    def __init__(self, index: int,
                       data_type: DataType,
                       component: ComponentType,
                       label = '',
                       required = True,
                       default = None,
                       allow_void = True,
                       transform_funcs = [],
                       na_list = ['', 'n/a', 'N/A']):
        super().__init__(None, data_type, component, label)
        self.index = index
        self.required = required
        self.default = default
        self.allow_void = allow_void
        self.transform_funcs = list(transform_funcs)
        self.na_list = list(na_list)

    def fetch_from_row(self, row, components, data, labels):
        if len(row) <= self.index:
            if self.required:
                return self._add_na_value(components, data, labels)
        else:
            value = row[self.index]
            if value in self.na_list:
                if self.required:
                    return self._add_na_value(components, data, labels)
            else:
                data.append(InstanceElement(value=value, datatype=self.data_type))
                components.append(self.component)
                labels.append(self.label)
                return True

    def _add_na_value(self, components, data, labels):
        if self.default is not None:
            data.append(InstanceElement(value=value, datatype=self.data_type))
        elif self.allow_void:
            data.append(InstanceElement())
        else:
            return False

        components.append(self.component)
        labels.append(self.label)
        return True



class CSVStringCombinationElement(CSVAbstractElement):
    def __init__(self, indices: Sequence[int],
                        component: ComponentType,
                        label = '',
                        combinator_func = None,
                        required = True):
        super().__init__(None, DataType.STRING, component, label)
        self.indices = indices
        self.combinator_func = combinator_func
        self.required = required

    def fetch_from_row(self, row, components, data, labels):
        tmp_data = []
        for index in self.indices:
            data = ''
            if len(row) > index:
                data = row[index]
            tmp_data.append(data)

        value = self.combinator_func(tmp_data) if self.combinator_func is not None else self._default_combinator(tmp_data)
        if len(value) == 0:
            if self.required:
                data.append(InstanceElement())
            else:
                return False
        else:
            data.append(InstanceElement(value=value, datatype=DataType.STRING))

        component.append(self.component)
        labels.append(self.label)

    def _default_combinator(self, tmp_data):
        result = '';
        for elem in tmp_data:
            if len(elem) > 0:
                if len(result) == 0:
                    result = '{0}'.format(result, elem)
                else:
                    result = '{0} {1}'.format(result, elem)
        return result



class CSVMapping:
    def __init__(self, action: Action,
                       elements: Sequence[CSVAbstractElement],
                       fallback: Sequence[CSVAbstractElement] = [],
                       batch_size = 100):
        self.action = action
        self.elements = elements
        self.fallback = list(fallback)
        self.batch_size = batch_size



class CSVLoader:
    def __init__(self, csv_path: str,
                       mappings: Sequence[CSVMapping] = [],
                       header_count=0,
                       delimiter=',',
                       doublequote=True,
                       escapechar=None,
                       lineterminator='\r\n',
                       quotechar='"',
                       quoting=csv.QUOTE_MINIMAL,
                       skipinitialspace=False,
                       strict=False):
        print("INIT !!!")
        print(mappings)
        self.csv_path = csv_path
        self.mappings = list(mappings)
        self.header_count = header_count
        self.delimiter = delimiter
        self.doublequote = doublequote
        self.escapechar = escapechar
        self.lineterminator = lineterminator
        self.quotechar = quotechar
        self.quoting = quoting
        self.skipinitialspace = skipinitialspace
        self.strict = strict
        print(self.mappings)

    def add_mapping(self, mapping: CSVMapping):
        self.mappings.append(mapping)

    def run(self, connection: DynizerConnection, debug=False):
        try:
            if connection is not None:
                connection.connect()
            for mapping in self.mappings:
                self.__run_mapping(connection, mapping, debug)
            if connection is not None:
                connection.close()
        except Exception as e:
            if connection is not None:
                connection.close()
            raise e

    def __run_mapping(self, connection: DynizerConnection,
                            mapping: CSVMapping,
                            debug):
        print('Creating instances for: {0}'.format(mapping.action.name))
        action_obj = None
        if connection is not None:
            try:
                action_obj = connection.create(mapping.action)
            except Exceptoin as e:
                raise LoaderError(CSVLoader, "Failed to create required action: '{0}'".format(mapping.action.name))

        topology_map = {}
        loadlist = []

        self.__run_simple_mapping(connection, mapping, action_obj, topology_map, loadlist, debug)

        if len(loadlist) > 0:
            self.__push_batch(connection, loadlist)

    def __run_simple_mapping(self, connection: DynizerConnection,
                                   mapping: CSVMapping,
                                   action_obj, topology_map, loadlist,
                                   debug):
        with open(self.csv_path, newline='') as csvfile:
            row_cnt=0
            csv_rdr = csv.reader(csvfile,
                                 delimiter=self.delimiter,
                                 doublequote=self.doublequote,
                                 escapechar=self.escapechar,
                                 lineterminator=self.lineterminator,
                                 quotechar=self.quotechar,
                                 quoting=self.quoting,
                                 skipinitialspace=self.skipinitialspace,
                                 strict=self.strict)
            for row in csv_rdr:
                row_cnt = row_cnt+1
                if row_cnt <= self.header_count:
                    continue

                status = self.__run_mapping_on_row(row, topology_map, loadlist, action_obj, connection, mapping, debug=debug)
                if not status:
                    self.__run_mapping_on_row(row, topology_map, loadlist, action_obj, connection, mapping, fallback=True, debug=debug)

            if len(loadlist) >= mapping.batch_size:
                self.__push_batch(connection, loadlist)

    def __run_mapping_on_row(self, row, topology_map, loadlist,
                                   action_obj: Action,
                                   connection: DynizerConnection,
                                   mapping: CSVMapping,
                                   fallback = False,
                                   debug = False):
        components = []
        data = []
        labels = []
        elements = mapping.fallback if fallback else mapping.elements
        if len(elements) == 0:
            return False

        for element in elements:
            if element.fetch_from_row(row, components, data, labels) == False:
                return False

        if len(components) < 2:
            return False

        if debug:
            inst = Instance(action_id=0, topology_id=0, data=data)
            print(inst.to_json())

        if connection is None:
            return True

        top_map_key = ','.join(map(str, components))
        topology_obj = None
        if top_map_key in topology_map:
            topology_obj = topology_map[top_map_key]
        else:
            if topology_obj is None:
                try:
                    topology = Topology(components=components, labels=labels)
                    topology_obj = connection.create(topology)
                    topology_obj.labels = labels
                except Exception as e:
                    raise LoaderError(CSVLoader, "Failed to create topology: '{0}'".format(top_map_key))

            try:
                connection.link_actiontopology(action_obj, topology_obj)
            except Exception as e:
                print("Failed to link action and topology.")

            topology_map[top_map_key] = topology_obj

        inst = Instance(action_id=action_obj.id, topology_id=topology_obj.id, data=data)
        loadlist.append(inst)
        return True



    def __push_batch(self, connection: DynizerConnection,
                           batch: Sequence[Instance]):
        if connection is not None:
            print("Writing batch ...")
            try:
                connection.batch_create(batch)
                batch.clear()
            except Exception as e:
                raise LoaderError(CSVLoader, "Failed to push batch of instances")

