from nython.core.runtime.node import NodeData
from nython.core.runtime.connector import Connector
from nython.core.runtime.connector import ConnectorType

from typing import Union

import json


class Flow:
    def __init__(self) -> None:
        self._nodes: list[NodeData] = list()
        self._connections: set[frozenset[Union[str, int]]] = set()

    def add_node(self, node: NodeData):
        """Add node to the flow. If emit is False, no events are emitted (useful during load)."""
        self._nodes.append(node)

    def remove_node_by_id(self, id: str|int):
        # search node using uuid
        node = next(
            (n for n in self._nodes if getattr(n, "uuid", -1) == id),
            None
        )

        if node is None:
            raise KeyError(f"No node with id {id}")

        self.remove_node(node)

    def remove_node(self, node: NodeData):
        # entferne node aus der node-liste
        self._nodes.remove(node)

        # sammle alle connector-uuids dieses nodes
        uuids = {c.uuid for c in (node.inputs + node.outputs)}

        # entferne alle Verbindungen, die eine dieser uuids enthalten
        self._connections = {pair for pair in self._connections if not (pair & uuids)}

        # entferne referenzen in allen übrigen connector-objekten
        for other in self._nodes:
            for conn in (other.inputs + other.outputs):
                conn.connections.difference_update(uuids)

    def disconnect(self, conn1: str | int, conn2: str | int):
        pair = frozenset({conn1, conn2})
        # sicher entfernen ohne KeyError
        self._connections.discard(pair)

        # aktualisiere Connector-Objekte falls vorhanden
        c1 = self._find_connector(conn1)
        c2 = self._find_connector(conn2)
        if c1:
            c1.connections.discard(conn2)
        if c2:
            c2.connections.discard(conn1)

    def connect(self, conn1: str | int, conn2: str | int):
        pair = frozenset({conn1, conn2})
        # set-Operation
        self._connections.add(pair)

        # aktualisiere Connector-Objekte falls vorhanden
        c1 = self._find_connector(conn1)
        c2 = self._find_connector(conn2)
        if c1:
            c1.connections.add(conn2)
        if c2:
            c2.connections.add(conn1)

    # helper for findig connection
    def _find_connector(self, uid: Union[str, int]) -> Connector | None:
        for node in self._nodes:
            for conn in (node.inputs + node.outputs):
                if conn.uuid == uid:
                    return conn
        return None

    def run(self):
        # Knoten und ihre Ausführungsergebnisse
        remaining = set(self._nodes)
        executed: dict[NodeData, tuple[dict, dict]] = {}

        # Für jeden Knoten Vorgänger aus Verbindungen ermitteln
        predecessors: dict[NodeData, set[NodeData]] = {}
        for node in self._nodes:
            # Finde alle verbundenen Input-Connectors
            pred_set = set()
            for input in node.inputs:
                for conn_id in input.connections:
                    # Finde Quell-Connector und dessen Node
                    source = self._find_connector(conn_id)
                    if source and source.type == ConnectorType.OUTPUT:
                        # Füge den Quell-Node zu Vorgängern hinzu
                        source_node = next((n for n in self._nodes if source in n.outputs), None)
                        if source_node:
                            pred_set.add(source_node)
            predecessors[node] = pred_set

        # Execute in topological order
        while remaining:
            for node in list(remaining):
                # Check if all predecessors where executed
                preds = predecessors[node]
                if all(p in executed for p in preds):
                    # Take the globals and local from the predecessors
                    if not preds:
                        globals_dict, locals_dict = {}, {}
                    else:
                        # Use the predecessors vars
                        globals_dict, locals_dict = next(iter(executed[p] for p in preds))

                    # Execute nodes and store results
                    new_globals, new_locals = node.execute(globals_dict, locals_dict)
                    executed[node] = (new_globals, new_locals)
                    remaining.remove(node)

        return executed

    @classmethod
    def load(cls, filename = "./_examples/flow.json") -> "Flow":
        _flow = Flow()

        with open(filename, "r") as file:
            read_flow = json.loads(file.read())

        for node in read_flow:
            new_node = NodeData.from_dict(node)
            _flow.add_node(new_node)

        # rebuild connections set from connectors
        for node in _flow._nodes:
            for conn in (node.inputs + node.outputs):
                for target in conn.connections:
                    pair = frozenset({conn.uuid, target})
                    _flow._connections.add(pair)

        return _flow
    
    def save(self, filename = "./flow.json"):
        with open(filename, "w") as file:
            file.write(json.dumps(self._nodes, default=lambda o: o.to_dict(), indent=4))