from ui.node import IMGuiNode
from _runtime import flow, node

import dearpygui.dearpygui as dpg

class NodeEditor:
    def __init__(self, parent: int|str) -> None:
        self.nodes: list[IMGuiNode]
        self.flow: flow.Flow
        self.parent = parent

        self.editor_tag = dpg.generate_uuid()

    def _load(self):
        self.flow = flow.Flow()
        self.flow.load()

    def link_callback(self, sender, app_data):
        dpg.add_node_link(app_data[0], app_data[1], parent=sender)
        print(f"Connection established {app_data[0], app_data[1]}")

    def delink_callback(self, sender, app_data):
        dpg.delete_item(app_data)
        print("Connection terminated")

    def create_node(self, label: str = "Node"):
        node_tag = dpg.generate_uuid()
        with dpg.node(label=label, tag=node_tag, parent=self.editor_tag):
            with dpg.node_attribute(label="Input"):
                dpg.add_input_float(width=150)
            with dpg.node_attribute(label="Output", attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_input_float(width=150)
        return node_tag

    def show(self):
        self._load()

        with dpg.node_editor(parent=self.parent, tag=self.editor_tag, callback=self.link_callback, delink_callback=self.delink_callback):
            with dpg.node(label="Node 1"):
                with dpg.node_attribute(label="Node A1"):
                    dpg.add_input_float(label="F1", width=150)

                with dpg.node_attribute(label="Node A2", attribute_type=dpg.mvNode_Attr_Output):
                    dpg.add_input_text(label="Code", width=150, multiline=True)

            with dpg.node(label="Node 2"):
                with dpg.node_attribute(label="Node A3"):
                    dpg.add_input_float(label="F3", width=200)

                with dpg.node_attribute(label="Node A4", attribute_type=dpg.mvNode_Attr_Output):
                    dpg.add_input_float(label="F4", width=200)


