from core.runtime.node import NodeData

import dearpygui.dearpygui as dpg

class IMGuiNode:
    def __init__(self, parent: str | int, node: NodeData, tag: str | int) -> None:
        self._imgui_parent = parent
        self._data: NodeData = node

        self.tag: str | int = tag

    def show(self):
        # TODO: Construct dynamic nodes based on the connector types or some
        with dpg.node(label=self._data.title, parent=self._imgui_parent, tag=self.tag):
            for input in self._data.inputs:
                with dpg.node_attribute(label="Node A1", tag=input.uuid, attribute_type=dpg.mvNode_Attr_Input):
                    dpg.add_input_float(label="Input", tag=f"float_{self.tag}", width=150)

            for output in self._data.outputs:
                with dpg.node_attribute(label="Node A2", tag=output.uuid, attribute_type=dpg.mvNode_Attr_Output):
                    dpg.add_input_text(label="Code", tag=f"text_{self.tag}", width=150, multiline=True)
