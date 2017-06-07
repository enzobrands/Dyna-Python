from ..types import Action, ComponentType, DataElement, DataType, Instance, InstanceElement, Topology
from ..connector import DynizerConnection
from ...common.errors import LoaderError
from typing import Sequence
import xml.etree.ElementTree as ET
import itertools

class XMLAbstractElement:
    """
    Abstract XML element

    This class represents an abstract XML element, that can be use to build up
    Dynizer instance data.

    Member Variables
    ----------------
    value : any
        The actual value of the xml element

    data_type : DataType
        The Dynizer data type of the xml element

    component : ComponentType
        The Dynizer component type of the xml element

    label : str
        The label for the xml element

    Member Functions
    ----------------
    fetch_from_entity
        Should be overwritten in concrete elements that fetch the value from the
        parsed xml file

    apply_ariables
        Should be overwritten in concrete elements that retrieve the value from
        previously parsed variables out of the xml file

    """
    def __init__(self, value,
                       data_type: DataType,
                       component: ComponentType,
                       label = ''):
        self.value = value
        self.data_type = data_type
        self.component = component
        self.label = label

    def fetch_from_entity(self, entity, components, data, labels, ns):
        components.append(self.component)
        data.append(InstanceElement(value=self.value, datatype=self.data_type))
        labels.append(self.label)
        return True

    def apply_variables(self, combinations):
        pass



class XMLFixedElement(XMLAbstractElement):
    """
    Fixed element

    This class represents a Fixed element, that can be use to build up
    Dynizer instance data. A Fixed element acts like a constant and will always
    represent the same value. It can not be altered once provided.
    """
    def __init__(self, value,
                       data_type: DataType,
                       component: ComponentType,
                       label = ''):
        super().__init__(value, data_type, component, label)



class XMLVariableElement(XMLAbstractElement):
    """
    Variable element

    This class represents a Variable element. Variable elements are assigned
    a value based upon a combination of LoopVariables, which have been fetched
    in a pre-parsing loop of the xml file. A full combinatoric off all loop variables
    are created and provided to the variable elements. Based upon the loop_index and
    variable_index the correct element is assigned to the variable element.

    The loop index specifies the loopvariable to access in the combinatorics matrix.
    Since each loop variable can have multiple subvariable references, the variable_index
    refers to the sub-index within the loopvariable.

    See the XmlLoopVariable class for more information
    """
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

    def fetch_from_entity(self, entity, components, data, labels, ns):
        node = entity.findall(self.path, ns)
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


class XMLStringCombinationElement(XMLAbstractElement):
    def __init__(self, paths: Sequence[str],
                 component: ComponentType,
                 label = '',
                 combinator_func = None,
                 required = True,
                 sequence_join_char = ','):
        super().__init__(None, DataType.STRING, component, label)
        self.paths = paths
        self.combinator_func = combinator_func
        self.required = required

    def fetch_from_entity(self, entity, components, data, labels, ns):
        tmp_data=[]
        for path in self.paths:
            node = entity.findall(path, ns)
            data = ''
            if len(node) == 1:
                data = node[0].text
            elif len(node) > 1:
                arr = []
                for n in node:
                    arr.append(n.text)
                data = sequence_join_char.join(arr)

            tmp_data.append(data)

        """
        if len(tmp_data) == 0:
            if not self.required:
                return True
            else:
                data.append(InstanceElement())
        else:

            if self.combinator_func is not None:
                data.append(InstanceElement(value=self.combinator_func(tmp_data), datatype=DataType.STRING))
            else:
                data.append(InstanceElement(value=self._default_combinator(tmp_data), datatype=DataType.STRING))
        """
        value = self.combinator_func(tmp_data) if self.combinator_func is not None else self._default_combinator(tmp_data)
        if len(value) == 0:
            if self.required:
                data.append(InstanceElement())
            else:
                return False
        else:
            data.append(InstanceElement(value=value, datatype=DataType.STRING))

        components.append(self.component)
        labels.append(self.label)

        return True


    def _default_combinator(self, tmp_data):
        result = '';
        for elem in tmp_data:
            if len(elem) > 0:
                if len(result) == 0:
                    result = '{0}'.format(result, elem)
                else:
                    result = '{0} {1}'.format(result, elem)
        return result



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
                       mappings: Sequence[XMLMapping] = [],
                       namespaces={}):
        self.root_node = root_node
        self.mappings = mappings
        self.ns = namespaces

    @classmethod
    def parse(cls, xml_file: str, mappings: Sequence[XMLMapping] = [], namespaces={}):
        return cls(ET.parse(xml_file).getroot(), mappings, namespaces)

    @classmethod
    def fromstring(cls, xml_string: str):
        return cls(ET.fromstring(xml_string))

    def add_mapping(self, mapping: XMLMapping):
        self.elements.append(mapping)

    def run(self, connection: DynizerConnection, debug=False):
        try:
            if connection is not None:
                print('CONNECT')
                connection.connect()
            for mapping in self.mappings:
                self.__run_mapping(connection, mapping, debug)
            if connection is not None:
                print('CLOSE')
                connection.close()
        except Exception as e:
            if connection is not None:
                print('CLOSE')
                connection.close()
            raise e


    def __expand_variables(self, root, mapping, variable):
        elements = root.findall(variable.path, self.ns)
        values = []
        for elem in elements:
            v_values = []
            for v_path in variable.variable_path:
                var_elem = elem.findall(v_path, self.ns)
                v_values.append(list(map(lambda x: x.text, var_elem)))
            values = values + list(itertools.product(*v_values))
        mapping.expanded_variables.append(values)


    def __run_mapping(self, connection: DynizerConnection,
                            mapping: XMLMapping,
                            debug):

        print('Creating instances for: {0}'.format( mapping.action.name))
        action_obj = None
        if connection is not None:
            try:
                print('CREATE ACTION')
                action_obj = connection.create(mapping.action)
            except Exception as e:
                raise LoaderError(XMLLoader, "Failed to create required action: '{0}'".format(mapping.action))

        topology_map = {}
        loadlist = []

        if len(mapping.variables) == 0:
            # No loopvariables are present
            self.__run_simple_mapping(connection, mapping, mapping.root_path, action_obj, topology_map, loadlist, debug)
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

                self.__run_simple_mapping(connection, mapping, current_root, action_obj, topology_map, loadlist, debug)

        if len(loadlist) > 0:
            self.__push_batch(connection, loadlist)


    def __run_simple_mapping(self, connection: DynizerConnection,
                                   mapping: XMLMapping,
                                   root_path: str,
                                   action_obj, topology_map, loadlist,
                                   debug):
        # Fetch the root node
        root = None

        try:
            root = self.root_node.findall(root_path, self.ns)
        except Exception as e:
            print(root_path)
            raise e
        if len(root) == 0:
            raise LoaderError(XMLLoader, "Invalid xpath specified for root path: '{0}'".format(root_path))

        # Loop over all entities in the root node and parse the entities
        for entity in root:
            status = self.__run_mapping_on_entity(entity, topology_map, loadlist, action_obj, connection, mapping, debug = debug)
            if not status:
                self.__run_mapping_on_entity(entity, topology_map, loadlist, action_obj, connection, mapping, fallback=True, debug = debug)


        if len(loadlist) >= mapping.batch_size:
            self.__push_batch(connection, loadlist)



    def __run_mapping_on_entity(self, entity, topology_map, loadlist,
                                      action_obj: Action,
                                      connection: DynizerConnection,
                                      mapping: XMLMapping,
                                      fallback = False,
                                      debug = False):
        components = []
        data = []
        labels = []
        elements = mapping.fallback if fallback else mapping.elements
        if len(elements) == 0:
            return False

        # Loop over all elements and fetch them fro mthe entity
        for element in elements:
            if element.fetch_from_entity(entity, components, data, labels, self.ns) == False:
                return False

        if len(components) < 2:
            return False

        if debug:
            inst = Instance(action_id=0, topology_id=0, data=data)
            print(inst.to_json())



        if connection is None:
            return True

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
                    print('CREATE TOPOLOGY')
                    topology_obj = connection.create(topology)
                    topology_obj.labels = labels
                except Exception as e:
                    raise LoaderError(XMLLoader, "Failed to create topology: '{0}'".format(top_map_key))

            # Also make sure it is linked to the action
            try:
                print('LINK TOPOLOGY')
                connection.link_actiontopology(action_obj, topology_obj)
            except Exception as e:
                print("Failed to link action and topology.")

            topology_map[top_map_key] = topology_obj

        # Create the instance and push it onto the load list
        inst = Instance(action_id=action_obj.id, topology_id=topology_obj.id, data=data)
        loadlist.append(inst)
        return True



    def __push_batch(self, connection: DynizerConnection,
                           batch: Sequence[Instance]):
        if connection is not None:
            print("Writing batch ...")
            try:
                PRINT('BATCH')
                connection.batch_create(batch)
                batch.clear()
            except Exception as e:
                raise LoaderError(XMLLoader, "Failed to push batch of instances")

