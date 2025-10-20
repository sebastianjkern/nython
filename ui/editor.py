from ui.node import IMGuiNode

from _runtime.node import NodeData, Connector, ConnectorType
from _runtime.flow import Flow

from typing import Union

import dearpygui.dearpygui as dpg

class NodeEditor:
    def __init__(self, parent: int|str) -> None:
        self._imgui_parent = parent
        self._editor_tag = str(dpg.generate_uuid())

        self._node_lut: dict[Union[str, int], IMGuiNode] | None = None

        # Init Runtime Layer
        self._flow = Flow()

    def link(self, sender, app_data):
        data = (dpg.get_item_alias(app_data[0]), dpg.get_item_alias(app_data[1]))

        # TODO: Check whether only output-input pairs are connected
        if len(set([self._flow._conn_lut[str(data[0])].type, self._flow._conn_lut[str(data[1])].type])) != 2:
            return

        dpg.add_node_link(app_data[0], app_data[1], parent=sender)
        self._flow.connect(str(data[0]), str(data[1]))

        print(f"Connection established {data[0], app_data[1]}")

    def unlink(self, sender, app_data):
        dpg.delete_item(app_data)
        self._flow.disconnect(str(app_data[0]), str(app_data[1]))

        print("Connection terminated")


    def create_node(self, label: str):
        input_tag = "input_" + str(dpg.generate_uuid())
        output_tag = "output_" + str(dpg.generate_uuid())

        node_tag = "node_" + str(dpg.generate_uuid())
        data = NodeData(node_tag, "")

        in_conn = Connector(input_tag, data)
        in_conn.type = ConnectorType.INPUT

        out_conn = Connector(output_tag, data)
        out_conn.type = ConnectorType.OUTPUT

        data.inputs = [in_conn]
        data.outputs = [out_conn]

        self._flow.add_node(data)

        node = IMGuiNode(self._editor_tag, data, tag=node_tag)
        node._outputs = [output_tag]
        node._inputs = [input_tag]

        node.show()

        if self._node_lut is None:
            self._node_lut = {}

        self._node_lut[node_tag] = node

        return node_tag


    def _load(self):
        self._flow = self._flow.load()
        self._node_lut = {}

        for node_data in self._flow._nodes:
            tag: str = node_data.uuid
            node = IMGuiNode(self._editor_tag, node_data, tag)

            self._node_lut[tag] = node

        connections: set[tuple[Union[str, int], Union[str, int]]] = set()

        # After the whole nodes lut is created, we can establish connections
        for node_data in self._flow._nodes:
            tag: str = node_data.uuid

            for child in node_data.outputs:
                for connection in child.connections:
                    connections.add((tag, connection))

            for parent in node_data.inputs:
                for connection in parent.connections:
                    connections.add((tag, connection))

        return connections


    def startup(self):
        connections = self._load()

        with dpg.node_editor(parent=self._imgui_parent, tag=self._editor_tag, callback=self.link, delink_callback=self.unlink):
            for item in self._node_lut.items():
                tag, node = item

                print(f"Showing item {tag}")

                node.show()
                
            for item in connections:
                i1, i2 = item

                print(i1, i2)
                dpg.add_node_link(i1, i2, parent=i1)
