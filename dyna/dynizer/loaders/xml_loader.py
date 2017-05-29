from ..types import Action, ComponentType, DataElement, DataType, Instance, InstanceElement, Topology
from ..connector import DynizerConnection
from ...common.errors import LoaderError
from typing import Sequence
import xml.etree.ElementTree as ET
import itertools

class XMLAbstractElement:
    def __init__(self, value,
                       data_type: DataType,
                       component: ComponentType,
                       label = ''):
        self.value = value
        self.data_type = data_type
        self.component = component
        self.label = label

    def fetch_from_entity(self, entity, components, data, labels):
        components.append(self.component)
        data.append(InstanceElement(value=self.value, datatype=self.data_type))
        labels.append(self.label)
        return True

    def apply_variables(self, combinations):
        pass



class XMLFixedElement(XMLAbstractElement):
    def __init__(self, value,
                       data_type: DataType,
                       component: ComponentType,
                       label = ''):
        super().__init__(value, data_type, component, label)



class XMLVariableElement(XMLAbstractElement):
    def __init__(self, loop_index: int,
                       variable_index: int,
                       data_type: DataType,
                       component: ComponentType,
                       label = '',
                       transform_funcs = []):
        super().__init__(None, data_type, component, label)
        self.loop_index = loop_index
        self.variable_index = variable_index
        self.transform_funcs = transform_funcs


    def apply_variables(self, combination):
        self.value = combination[self.loop_index][self.variable_index]
        for tf in self.transform_funcs:
            self.value = tf(self.value)



class XMLExtractionElement(XMLAbstractElement):
    def __init__(self, path: str,
                       data_type: DataType,
                       component: ComponentType,
                       label = '',
                       required = True,
                       default = None,
                       allow_void = True,
                       transform_funcs = []):
        super().__init__(None, data_type, component, label)
        self.path = path
        self.required = required
        self.default = default
        self.allow_void = allow_void
        self.transform_funcs = transform_funcs

    def fetch_from_entity(self, entity, components, data, labels):
        node = entity.findall(self.path)
        if len(node) == 0:
            if self.required:
                if self.default is not None:
                    components.append(self.component)
                    data.append(InstanceElement(value=value, datatype=self.data_type))
                    labels.append(self.label)
                elif self.allow_void:
                    components.append(self.component)
                    data.append(InstanceElement())
                    labels.append(self.label)
                else:
                    return False
        elif len(node) == 1:
            value = node[0].text
            for tf in self.transform_funcs:
                value = tf(value)

            components.append(self.component)
            data.append(InstanceElement(value=value, datatype=self.data_type))
            labels.append(self.label)
        else:
            for val in node:
                value = val.text
                for tf in transform_fucs:
                    value = tf(value)

                components.append(self.component)
                data.append(InstanceElement(value=value, datatype=self.data_type))
                labels.append(self.label)
        return True



class XMLLoopVariable:
    def __init__(self, path: str, variable_path: Sequence[str]):
        self.path = path
        self.variable_path = variable_path


class XMLMapping:
    def __init__(self, action: Action,
                       root_path: str,
                       variables: Sequence[XMLLoopVariable],
                       elements: Sequence[XMLAbstractElement],
                       fallback: Sequence[XMLAbstractElement] = [],
                       batch_size=100):
        self.action = action
        self.root_path = root_path
        self.variables = variables
        self.elements = elements
        self.fallback = fallback
        self.expanded_variables = []
        self.batch_size = batch_size


class XMLLoader:
    def __init__(self, root_node: ET.Element,
                       mappings: Sequence[XMLMapping] = []):
        self.root_node = root_node
        self.mappings = mappings

    @classmethod
    def parse(cls, xml_file: str):
        return cls(ET.parse(xml_file).getroot())

    @classmethod
    def fromstring(cls, xml_string: str):
        return cls(ET.fromstring(xml_string))

    def add_mapping(self, mapping: XMLMapping):
        self.elements.append(mapping)

    def run(self, connection: DynizerConnection, batch_size=100):
        for mapping in self.mappings:
            self.__run_mapping(connection, mapping)


    def __expand_variables(self, root, mapping, variable):
        elements = root.findall(variable.path)
        values = []
        for elem in elements:
            v_values = []
            for v_path in variable.variable_path:
                var_elem = elem.findall(v_path)
                v_values.append(list(map(lambda x: x.text, var_elem)))
            values = values + list(itertools.product(*v_values))
        mapping.expanded_variables.append(values)


    def __run_mapping(self, connection: DynizerConnection,
                            mapping: XMLMapping):

        print('Creating instances for: {0}'.format( mapping.action.name))
        action_obj = None
        try:
            action_obj = connection.create(mapping.action)
        except Exception as e:
            raise LoaderError(XMLLoader, "Failed to create required action: '{0}'".format(mapping.action))

        topology_map = {}
        loadlist = []

        if len(mapping.variables) == 0:
            # No loopvariables are present
            self.__run_simple_mapping(connection, mapping, mapping.root_path, action_obj, topology_map, loadlist)
        else:
            # We have loop variables, resolve them
            for variable in mapping.variables:
                self.__expand_variables(self.root_node, mapping, variable)

            # Make the combinations of the various loop variables and iterate over them
            var_combinations = list(itertools.product(*mapping.expanded_variables))
            for combination in var_combinations:
                # Adjust the root path with the requested loop variables
                current_root = mapping.root_path.format(*combination)
                for elem in mapping.elements:
                    # Apply the current variables to the XMLVariableElements
                    elem.apply_variables(combination)
                for elem in mapping.fallback:
                    elem.apply_variables(combination)

                self.__run_simple_mapping(connection, mapping, current_root, action_obj, topology_map, loadlist)

        if len(loadlist) > 0:
            self.__push_batch(connection, loadlist)


    def __run_simple_mapping(self, connection: DynizerConnection,
                                   mapping: XMLMapping,
                                   root_path: str,
                                   action_obj, topology_map, loadlist):
        # Fetch the root node
        root = self.root_node.findall(root_path)
        if len(root) == 0:
            raise LoaderError(XMLLoader, "Invalid xpath specified for root path: '{0}'".format(root_path))

        # Loop over all entities in the root node and parse the entities
        for entity in root:
            status = self.__run_mapping_on_entity(entity, topology_map, loadlist, action_obj, connection, mapping)
            if not status:
                self.__run_mapping_on_entity(entity, topology_map, loadlist, action_obj, connection, mapping, fallback=True)


        if len(loadlist) >= mapping.batch_size:
            self.__push_batch(connection, loadlist)



    def __run_mapping_on_entity(self, entity, topology_map, loadlist,
                                      action_obj: Action,
                                      connection: DynizerConnection,
                                      mapping: XMLMapping,
                                      fallback = False):
        components = []
        data = []
        labels = []
        elements = mapping.fallback if fallback else mapping.elements
        if len(elements) == 0:
            return False

        # Loop over all elements and fetch them fro mthe entity
        for element in elements:
            if element.fetch_from_entity(entity, components, data, labels) == False:
                return False

        if len(components) < 2:
            return False

        # Build the topology
        top_map_key = ','.join(map(str, components))
        topology_obj = None
        if top_map_key in topology_map:
            topology_obj = topology_map[top_map_key]
        else:
            # Check if we have it in the system
            if topology_obj is None:
                try:
                    topology = Topology(components=components, labels=labels)
                    topology_obj = connection.create(topology)
                    topology_obj.labels = labels
                except Exception as e:
                    raise LoaderError(XMLLoader, "Failed to create topology: '{0}'".format(top_map_key))

            # Also make sure it is linked to the action
            try:
                connection.link_actiontopology(action_obj, topology_obj)
            except Exception as e:
                raise LoaderError(XMLLoader, "Failed to link action and topology")

            topology_map[top_map_key] = topology_obj

        # Create the instance and push it onto the load list
        inst = Instance(action_id=action_obj.id, topology_id=topology_obj.id, data=data)
        loadlist.append(inst)
        return True



    def __push_batch(self, connection: DynizerConnection,
                           batch: Sequence[Instance]):
        print("Writing batch ...")
        try:
            connection.batch_create(batch)
            batch.clear()
        except Exception as e:
            raise LoaderError(XMLLoader, "Failed to push batch of instances")

