from _runtime.node import NodeData, Connector
from _util.diff import diff_dict

from typing import Union

import json

class Flow:
    def __init__(self) -> None:
        self._nodes: list[NodeData] = list()

        self._conn_lut: dict[str, Connector] = {}

    def add_node(self, node: NodeData):
        self._nodes.append(node)

        for input in node.inputs:
            self._conn_lut[input.uuid] = input

        for output in node.outputs:
            self._conn_lut[output.uuid] = output

        print(self._conn_lut)

    def remove_node(self, node: NodeData):
        self._nodes.remove(node)

        for input in node.inputs:
            del self._conn_lut[input.uuid]

        for output in node.outputs:
            del self._conn_lut[output.uuid]


    def save(self):
        with open("./flow.json", "w") as file:
            file.write( json.dumps(self._nodes, default=lambda o: o.to_dict(), indent=4))
       
    @classmethod
    def load(cls):
        with open("./_examples/flow.json", "r") as file:
            read_flow = json.loads(file.read())

        flow = Flow()

        for node in read_flow:
            new_node = NodeData.from_dict(node)
            flow.add_node(new_node)

        for node in flow._nodes:
            for connector in node.inputs:
                flow._conn_lut[connector.uuid] = connector

            for connector in node.outputs:
                flow._conn_lut[connector.uuid] = connector

        return flow
    
    def disconnect(self, conn1: str, conn2: str):
        self._conn_lut[conn1].connections.remove(conn2)
        self._conn_lut[conn2].connections.remove(conn1)

    def connect(self, conn1: str, conn2: str):
        self._conn_lut[conn1].connections.add(conn2)
        self._conn_lut[conn2].connections.add(conn1)

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

                    print(diff_dict(globals_dict, new_globals))
                    print(diff_dict(locals_dict, new_locals))

                    remaining.remove(node)

    def to_python(self) -> str:
        return NotImplemented

