from ui.node import IMGuiNode

from _runtime.node import NodeData, Connector, ConnectorType
from _runtime.flow import Flow
from _runtime.events import RuntimeEvents

from typing import Union

import dearpygui.dearpygui as dpg

class NodeEditor:
    def __init__(self, parent: int|str) -> None:
        self._imgui_parent = parent
        self._editor_tag = str(dpg.generate_uuid())

        self._node_lut: dict[Union[str, int], IMGuiNode] | None = None

        # Init Runtime Layer
        self._flow = Flow()
        # track last known revision to avoid applying stale events
        self._revision = 0

        # Subscribe to runtime events so GUI reconciles from runtime state
        self._subscribe_runtime_events()

        # mapping of frozenset({a,b}) -> link_item_id created in DearPyGui
        # DPG may return int or str ids depending on build, accept both.
        self._link_lut = {}

    def _subscribe_runtime_events(self):
        try:
            self._flow.events.subscribe(RuntimeEvents.NODE_CREATED, self._on_node_added)
            self._flow.events.subscribe(RuntimeEvents.LOADED, self._on_loaded)
            self._flow.events.subscribe(RuntimeEvents.CONN_ESTABLISHED, self._on_connection_added)
            self._flow.events.subscribe(RuntimeEvents.CONN_REMOVED, self._on_connection_removed)
            self._flow.events.subscribe(RuntimeEvents.NODE_REMOVED, self._on_node_removed)
        except Exception:
            # in tests or headless mode events may not be available
            pass

    def link(self, sender, app_data):
        # Resolve aliases to connector UUIDs (the runtime uses UUID strings)
        a = dpg.get_item_alias(app_data[0])
        b = dpg.get_item_alias(app_data[1])

        # Validate types using runtime connector LUT (ensure output-input pair)
        try:
            ca = self._flow._conn_lut.get(str(a))
            cb = self._flow._conn_lut.get(str(b))
        except Exception:
            ca = cb = None

        if ca is None or cb is None:
            return

        if len(set([ca.type, cb.type])) != 2:
            return
        # Delegate connection to runtime via command event; GUI will be updated from the emitted event
        try:
            self._flow.events.emit_sync(RuntimeEvents.CONNECT, {"a": str(a), "b": str(b)})
        except Exception:
            pass

    def unlink(self, sender, app_data):
        # app_data contains the two ends
        a = dpg.get_item_alias(app_data[0])
        b = dpg.get_item_alias(app_data[1])

        try:
            self._flow.events.emit_sync(RuntimeEvents.DISCONNECT, {"a": str(a), "b": str(b)})
        except Exception:
            pass

        # GUI link will be removed when runtime emits connection_removed


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

        # Request runtime to create the node via command event; GUI will be created from the runtime event
        try:
            # send serialized node so runtime can recreate it exactly
            self._flow.events.emit_sync(RuntimeEvents.CREATE_NODE, {"node": data.to_dict(), "label": label})
        except Exception:
            pass
        return node_tag


    def _load(self):
        # Load runtime state; runtime will emit a single 'loaded' event which we handle
        # load without emitting 'loaded' so we can subscribe GUI handlers first
        old_flow = getattr(self, "_flow", None)
        self._flow = self._flow.load(emit_loaded=False)
        # re-subscribe handlers to the new Flow.events instance
        try:
            self._subscribe_runtime_events()
        except Exception:
            pass
        # _on_loaded handler will populate _node_lut and return connections if needed
        # Do not emit 'loaded' here — caller (startup) will emit it inside a valid
        # DearPyGui node_editor context so handlers can create GUI items safely.
        return set()


    # Event handlers from runtime
    def _on_loaded(self, payload):
        try:
            rev = payload.get("revision", 0)
            if rev <= self._revision:
                return
            self._revision = rev
        except Exception:
            pass

        self._node_lut = {}
        for node_dict in payload.get("nodes", []):
            tag = node_dict.get("uuid")
            node = IMGuiNode(self._editor_tag, NodeData.from_dict(node_dict), tag)
            node._inputs = [c.get("uuid") for c in node_dict.get("inputs", [])]
            node._outputs = [c.get("uuid") for c in node_dict.get("outputs", [])]
            self._node_lut[tag] = node
            node.show()

        # establish connections visually and record link ids
        for node_dict in payload.get("nodes", []):
            for out in node_dict.get("outputs", []):
                for conn in out.get("connections", []):
                    try:
                        link_id = dpg.add_node_link(out.get("uuid"), conn, parent=self._editor_tag)
                        key = frozenset([out.get("uuid"), conn])
                        try:
                            # some DPG builds return None for ids; handle gracefully
                            if link_id is not None:
                                self._link_lut[key] = link_id
                        except Exception:
                            pass
                    except Exception:
                        pass

    def _on_node_added(self, payload):
        try:
            rev = payload.get("revision", 0)
            if rev <= self._revision:
                return
            self._revision = rev
        except Exception:
            pass

        node_dict = payload.get("node")
        if not node_dict:
            return
        
        print(node_dict)

        tag = node_dict.get("uuid")
        node = IMGuiNode(self._editor_tag, NodeData.from_dict(node_dict), tag)
        node._inputs = [c.get("uuid") for c in node_dict.get("inputs", [])]
        node._outputs = [c.get("uuid") for c in node_dict.get("outputs", [])]
        if self._node_lut is None:
            self._node_lut = {}
        self._node_lut[tag] = node
        node.show()

    def _on_connection_added(self, payload):
        a = payload.get("a")
        b = payload.get("b")
        try:
            link_id = dpg.add_node_link(a, b, parent=self._editor_tag)
            key = frozenset([a, b])
            if link_id is not None:
                self._link_lut[key] = link_id
        except Exception:
            pass

    def _on_connection_removed(self, payload):
        # payload contains endpoints 'a' and 'b' — remove link if it exists
        a = payload.get("a")
        b = payload.get("b")
        # dearpygui identifies links by their id (the two endpoints tuple), but we can try to delete by alias
        try:
            key = frozenset([a, b])
            link_id = self._link_lut.get(key)
            if link_id is not None:
                dpg.delete_item(link_id)
                try:
                    del self._link_lut[key]
                except KeyError:
                    pass
        except Exception:
            pass

    def _on_node_removed(self, payload):
        uuid = payload.get("uuid")
        if not uuid:
            return
        if self._node_lut and uuid in self._node_lut:
            try:
                dpg.delete_item(uuid)
            except Exception:
                pass
            del self._node_lut[uuid]


    def startup(self):
        connections = self._load()

        with dpg.node_editor(parent=self._imgui_parent, tag=self._editor_tag, callback=self.link, delink_callback=self.unlink):
            # Emit the 'loaded' event now that the node_editor container exists so
            # handlers can create nodes/links with a valid parent.
            try:
                self._flow.events.emit_sync(RuntimeEvents.LOADED, {"nodes": [n.to_dict() for n in self._flow._nodes], "revision": self._flow._revision})
            except Exception:
                pass
            if not self._node_lut:
                # nothing loaded yet
                self._node_lut = {}

            for tag, node in list(self._node_lut.items()):
                print(f"Showing item {tag}")
                node.show()
                
            for item in connections:
                i1, i2 = item

                print(i1, i2)
                try:
                    dpg.add_node_link(i1, i2, parent=self._editor_tag)
                except Exception:
                    pass
