from core.runtime.node import NodeData
from core.runtime.flow import Flow
from core.runtime.connector import Connector, ConnectorType

from core.ui.node import IMGuiNode

from _util.uuid import get_uuid

import dearpygui.dearpygui as dpg

class NodeEditor:
    def __init__(self) -> None:
        # Imgui Stuff
        self._editor_tag = "_editor"

        # Load Runtime Layer
        self.flow: Flow = Flow.load()

        self._center_window = "main_window"
        self._settings_window = "settings_window"

        self._create_node_popup = "create_node_popup"
        self._create_node_input = "create_node_input"

    def __enter__(self):
        # Main editor window
        with dpg.window(label="Nython Editor", tag=self._center_window, no_collapse=True, no_close=True, no_title_bar=True, no_move=True):
            with dpg.node_editor(parent=self._center_window, tag=self._editor_tag, callback=self.link, delink_callback=self.unlink):
                pass

        # Create Node Pop Up
        with dpg.window(label="Create Node", modal=True, show=False, tag=self._create_node_popup, no_resize=True, no_collapse=True, no_move=True):
            dpg.add_input_text(tag=self._create_node_input, default_value="New Node")

            def _create_node_cb(sender, app_data):
                name = dpg.get_value(self._create_node_input)

                input_tag = get_uuid()
                output_tag = get_uuid()

                node_tag = get_uuid()

                data = NodeData(node_tag, "")
                data.title = name

                in_conn = Connector(input_tag)
                in_conn.type = ConnectorType.INPUT

                out_conn = Connector(output_tag)
                out_conn.type = ConnectorType.OUTPUT

                data.inputs = [in_conn]
                data.outputs = [out_conn]

                node = IMGuiNode(self._editor_tag, data)
                node.show()

                self.flow.add_node(data)

                # Close the Popup in case the node was created sucessfully
                dpg.configure_item(self._create_node_popup, show=False)

            # Close popup immediately; the GUI node will be created when the runtime emits the event
            dpg.configure_item(self._create_node_popup, show=False)

            with dpg.group(horizontal=True):
                dpg.add_button(label="Create", callback=_create_node_cb)
                dpg.add_button(label="Cancel", callback=lambda s,a: dpg.configure_item(self._create_node_popup, show=False))

        with dpg.handler_registry() as fff:
            dpg.add_key_press_handler(callback=self.key_handler)

        return self


    def __exit__(self, exc_type, exc_value, exc_traceback):
        for node in self.flow._nodes:
            ui_node = IMGuiNode(self._editor_tag, node)

            try:
                ui_node.show()
            except Exception as err:
                print("error while loading node:", err)

        # Restore connections from flow._connections (set[frozenset])
        for pair in self.flow._connections:
            # pair ist ein frozenset mit genau zwei connector-uuids
            a, b = tuple(pair)

            ca = self.flow._find_connector(a)
            cb = self.flow._find_connector(b)

            # beide Connector-Objekte müssen vorhanden sein
            if ca is None or cb is None:
                continue

            # bestimme Richtung: add_node_link(output_attr, input_attr, ...)
            if ca.type == ConnectorType.INPUT and cb.type == ConnectorType.OUTPUT:
                out_attr = cb.uuid
                in_attr = ca.uuid
            elif cb.type == ConnectorType.INPUT and ca.type == ConnectorType.OUTPUT:
                out_attr = ca.uuid
                in_attr = cb.uuid
            else:
                # ungültige Paarung (z.B. input-input oder output-output) überspringen
                continue

            dpg.add_node_link(out_attr, in_attr, parent=self._editor_tag)
    

    def key_handler(self, sender, app_data):
        # Provide a functionality for adding a new node
        if app_data == dpg.mvKey_N and dpg.is_key_down(dpg.mvKey_LShift):
            # Item-Größen und -Positionen im Bezug auf die Viewport/Applikation abfragen
            dpg.configure_item(self._create_node_popup, show=True)

            main_w = dpg.get_viewport_width()
            main_h = dpg.get_viewport_height()
            modal_w = dpg.get_item_width(self._create_node_popup)
            modal_h = dpg.get_item_height(self._create_node_popup)
            main_pos = dpg.get_viewport_pos()  # absolute Position des Viewports

            if any(v is None for v in (main_w, main_h, modal_w, modal_h, main_pos)):
                return

            # Berechne Position, damit das Modal im Zentrum des Hauptfensters sitzt
            # help static type checkers: assert values are not None
            assert main_w is not None and main_h is not None and modal_w is not None and modal_h is not None and main_pos is not None

            rel_x = int(main_w / 2 - modal_w / 2)
            rel_y = int(main_h / 2 - modal_h / 2)
            abs_x = int(main_pos[0] + rel_x)
            abs_y = int(main_pos[1] + rel_y)
            # setze die absolute Position im Koordinatensystem des Viewports
            dpg.set_item_pos(self._create_node_popup, [rel_x, rel_y])
            
            dpg.focus_item(self._create_node_input)

        # Delete selected nodes
        if app_data == dpg.mvKey_Delete:
            nodes = dpg.get_selected_nodes(self._editor_tag) or []
            links = dpg.get_selected_links(self._editor_tag) or []

            # Dann die selektierten Nodes löschen
            for node in nodes:
                self.flow.remove_node_by_id(node)
                dpg.delete_item(node)

            for link in links:
                self.unlink(sender=None, app_data=link)

        if app_data == dpg.mvKey_S and dpg.is_key_down(dpg.mvKey_LControl):
            print("Saved")
            self.flow.save()


    def link(self, sender, app_data):
        # Connect nodes
        self.flow.connect(app_data[0], app_data[1])
        dpg.add_node_link(app_data[0], app_data[1], parent=sender)


    def unlink(self, sender, app_data):
        # get link info
        cfg = dpg.get_item_configuration(app_data)
        start_attr = cfg["attr_1"]
        end_attr = cfg["attr_2"]

        # get node tags (wenn benötigt)
        start_node = dpg.get_item_parent(start_attr)
        end_node = dpg.get_item_parent(end_attr)

        if start_node is None or end_node is None:
            return

        # Übergib die Attribut-UUIDs an die Flow-Logik (nicht Node-Tags)
        self.flow.disconnect(start_attr, end_attr)
        dpg.delete_item(app_data)

