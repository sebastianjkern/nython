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

        # mapping of frozenset({a,b}) -> link_item_id created in DearPyGui
        # DPG may return int or str ids depending on build, accept both.
        self._link_lut = {}

    def _subscribe_runtime_events(self):
        try:
            ev = self._flow.events
            # subscribe runtime -> gui handlers (these handlers will be invoked
            # on the main thread when poll() is called)
            ev.subscribe(RuntimeEvents.LOADED, self._on_loaded)
            ev.subscribe(RuntimeEvents.NODE_CREATED, self._on_node_added)
            ev.subscribe(RuntimeEvents.CONN_ESTABLISHED, self._on_connection_added)
            ev.subscribe(RuntimeEvents.CONN_REMOVED, self._on_connection_removed)
            ev.subscribe(RuntimeEvents.NODE_REMOVED, self._on_node_removed)
        except Exception as e:
            print("Failed to subscribe runtime events:", e)

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
            self._node_lut[tag] = node

            node.show()

        # establish connections visually and record link ids
        for node_dict in payload.get("nodes", []):
            outputs = node_dict.get("outputs") or {}
            # outputs is a dict: { connector_uuid: [connected_uuid, ...], ... }
            for out_uuid, conn_list in outputs.items():
                for conn in conn_list or []:
                    try:
                        link_id = dpg.add_node_link(out_uuid, conn, parent=self._editor_tag)
                        key = frozenset([out_uuid, conn])
                        if link_id is not None:
                            self._link_lut[key] = link_id
                    except Exception:
                        pass

    def _on_node_added(self, payload):
        try:
            rev = payload.get("revision", 0)
            if rev <= self._revision:
                print("old revision")
                return
            self._revision = rev
        except Exception:
            print("exception")
            pass

        node_dict = payload.get("node")
        
        if not node_dict:
            print("payload error")
            return
        
        tag = node_dict.get("uuid")
        node = IMGuiNode(self._editor_tag, NodeData.from_dict(node_dict), tag)

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
        # create the node editor widget and wire callbacks minimally
        try:
            # ensure node lookup is present
            self._node_lut = {}

            # create a node editor area
            with dpg.node_editor(parent=self._imgui_parent, tag=self._editor_tag, callback=self.link, delink_callback=self.unlink):
                pass

            # subscribe to runtime events (they will be processed via Flow.events.poll())
            self._subscribe_runtime_events()

            # request loading the default flow (Flow listens to LOAD_FILE)
            try:
                self._flow.events.emit(RuntimeEvents.LOAD_FILE, {"filename": "./flow.json", "emit_loaded": True})
            except Exception:
                # fallback: try synchronous emit if available
                try:
                    self._flow.events.emit_sync(RuntimeEvents.LOAD_FILE, {"filename": "./flow.json", "emit_loaded": True})
                except Exception:
                    pass
        except Exception as e:
            print("NodeEditor.startup failed:", e)