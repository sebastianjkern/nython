from _runtime.node import NodeData, Connector
from _util.diff import diff_dict
from _runtime.events import EventBus, RuntimeEvents

import json


class Flow:
    def __init__(self) -> None:
        self._nodes: list[NodeData] = list()

        self._conn_lut: dict[str, Connector] = {}

        # Event bus for notifying observers (GUI) about state changes.
        self.events = EventBus()

        # Simple revision counter to help synchronize GUI and runtime
        self._revision: int = 0
        
        # Subscribe to command events so external layers can request changes
        self.events.subscribe(RuntimeEvents.CREATE_NODE, self._cmd_create_node)
        self.events.subscribe(RuntimeEvents.REM_NODE, self._cmd_remove_node)
        self.events.subscribe(RuntimeEvents.CONNECT, self._cmd_connect)
        self.events.subscribe(RuntimeEvents.DISCONNECT, self._cmd_disconnect)
        self.events.subscribe(RuntimeEvents.SAVE, self._cmd_save)
        self.events.subscribe(RuntimeEvents.LOAD_FILE, self._cmd_load)

    def _bump_revision(self) -> int:
        self._revision += 1
        return self._revision

    def add_node(self, node: NodeData, emit: bool = True):
        """Add node to the flow. If emit is False, no events are emitted (useful during load)."""
        self._nodes.append(node)

        for input in node.inputs:
            self._conn_lut[input.uuid] = input

        for output in node.outputs:
            self._conn_lut[output.uuid] = output

        if emit:
            rev = self._bump_revision()
            self.events.emit_sync(RuntimeEvents.NODE_CREATED, {"node": node.to_dict(), "revision": rev})

    def remove_node(self, node: NodeData):
        self._nodes.remove(node)

        for input in node.inputs:
            del self._conn_lut[input.uuid]

        for output in node.outputs:
            del self._conn_lut[output.uuid]

        rev = self._bump_revision()
        self.events.emit_sync(RuntimeEvents.NODE_REMOVED, {"uuid": getattr(node, "uuid", None), "revision": rev})

    # Command handlers
    def _cmd_create_node(self, payload: dict | None):
        if not payload:
            return

        label = payload.get("label")
        node_dict = payload.get("node")
        if node_dict:
            node = NodeData.from_dict(node_dict)
            self.add_node(node)
            return

        # create minimal node with generated ids if only label provided
        tag = "node_" + str(label) if label else "node_" + str(self._bump_revision())
        node = NodeData(tag, label or "")
        # leave connectors empty; higher-level code can emit further commands to add connectors
        self.add_node(node)

    def _cmd_remove_node(self, payload: dict | None):
        if not payload:
            return
        # payload expected: {"uuid": str}
        uuid = payload.get("uuid")
        if not uuid:
            return
        # find node by uuid
        node = next((n for n in self._nodes if getattr(n, "uuid", None) == uuid or getattr(n, "id", None) == uuid), None)
        if node:
            self.remove_node(node)

    def _cmd_connect(self, payload: dict | None):
        if not payload:
            return
        a = payload.get("a")
        b = payload.get("b")
        if not a or not b:
            return

        self.connect(str(a), str(b))

    def _cmd_disconnect(self, payload: dict | None):
        if not payload:
            return
        a = payload.get("a")
        b = payload.get("b")
        if not a or not b:
            return

        self.disconnect(str(a), str(b))

    def _cmd_save(self, payload: dict | None):
        try:
            with open("./flow.json", "w") as file:
                file.write(json.dumps(self._nodes, default=lambda o: o.to_dict(), indent=4))
        except Exception:
            pass

    def _cmd_load(self, payload: dict):
        emit_loaded = payload.get("emit_loaded", True)
        filename = payload.get("filename", "./_examples/flow.json")

        with open(filename, "r") as file:
            read_flow = json.loads(file.read())

        self._nodes: list[NodeData] = list()
        self._conn_lut: dict[str, Connector] = {}

        # when loading, we don't want to emit node_added events for each node
        for node in read_flow:
            new_node = NodeData.from_dict(node)
            self.add_node(new_node, emit=False)

        # rebuild conn lut explicitly (safety)
        for node in self._nodes:
            for connector in node.inputs:
                self._conn_lut[connector.uuid] = connector

            for connector in node.outputs:
                self._conn_lut[connector.uuid] = connector

        # After load, optionally emit a single 'loaded' event containing the full serialized state and a revision
        self._bump_revision()
        if emit_loaded:
            self.events.emit_sync(RuntimeEvents.LOADED, {"nodes": [n.to_dict() for n in self._nodes], "revision": self._revision})

    def disconnect(self, conn1: str, conn2: str):
        self._conn_lut[conn1].connections.remove(conn2)
        self._conn_lut[conn2].connections.remove(conn1)
        rev = self._bump_revision()
        self.events.emit_sync(RuntimeEvents.CONN_REMOVED, {"a": conn1, "b": conn2, "revision": rev})

    def connect(self, conn1: str, conn2: str):
        self._conn_lut[conn1].connections.add(conn2)
        self._conn_lut[conn2].connections.add(conn1)
        rev = self._bump_revision()
        self.events.emit_sync(RuntimeEvents.CONN_ESTABLISHED, {"a": conn1, "b": conn2, "revision": rev})

    def run(self):
        # TODO: Fix this stuff, does not work at the moment

        # Execute nodes in topological order.
        remaining = set(self._nodes)
        executed_outputs: dict[NodeData, tuple] = {}

        while remaining:
            for node in list(remaining):
                parents = getattr(node, "parents", [])
                if all(p in executed_outputs for p in parents):
                    if not parents:
                        globals_dict = {}
                        locals_dict = {}
                    else:
                        globals_dict, locals_dict = executed_outputs[parents[0]]

                    # <– execute the node in both cases
                    new_globals, new_locals = node.execute(globals_dict, locals_dict)
                    executed_outputs[node] = (new_globals, new_locals)

                    remaining.remove(node)
