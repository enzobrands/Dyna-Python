from ..types import Action, ComponentType, DataElement, DataType, Instance, InstanceElement, Topology
from ..connector import DynizerConnection
from ...common.errors import LoaderError
from typing import Sequence
import xml.etree.ElementTree as ET

class XMLExtractionElement:
    def __init__(self, path: str,
                       data_type: DataType,
                       component: ComponentType,
                       label = '',
                       required = True):
        self.path = path
        self.data_type = data_type
        self.component = component
        self.label = label
        self.required = required


class XMLMapping:
    def __init__(self, action: Action,
                       root_path: str,
                       elements: Sequence[XMLExtractionElement]):
        self.action = action
        self.root_path = root_path
        self.elements = elements


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


    def __run_mapping(self, connection: DynizerConnection,
                            mapping: XMLMapping):
        root = self.root_node.find(mapping.root_path)
        if root == None:
            raise LoaderError(XMLLoader, "Invalid xpath specified for root path: '{0}'".format(mapping.root_path))

        action_obj = None
        try:
            print(mapping.action.to_json())
            action_obj = connection.create(mapping.action)
        except Exception as e:
            raise LoaderError(XMLLoader, "Failed to create required action: '{0}'".format(mapping.action))

        topology_map = {}
        loadlist = []
        for entity in root:
            components = []
            data = []
            labels = []
            for element in mapping.elements:
                node = entity.find(element.path)
                if node is None:
                    if element.required:
                        components.append(element.component)
                        data.append(InstanceElement())
                        labels.append(element.label)
                else:
                    components.append(element.component)
                    data.append(InstanceElement(value=node.text, datatype=element.data_type))
                    labels.append(element.label)

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

            loadlist.append(Instance(action_id=action_obj.id,
                                     topology_id=topology_obj.id,
                                     data=data))

            if len(loadlist) == 100:
                self.__push_batch(connection, loadlist)
                loadlist = []

        if len(loadlist) > 0:
            self.__push_batch(connection, loadlist)


    def __push_batch(self, connection: DynizerConnection,
                           batch: Sequence[Instance]):
        print("Writing batch ...")
        try:
            connection.batch_create(batch)
        except Exception as e:
            raise LoaderError(XMLLoader, "Failed to push batch of instances")

