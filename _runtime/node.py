from types import CodeType
from typing import Any, Union

from enum import Enum

class ConnectorType(Enum):
    INPUT = 0
    OUTPUT = 1

class NodeData:
    def __init__(self, uuid: str, code:str) -> None:
        self.uuid: str = str(uuid)
        self.code: str = code

        self.code_hash = hash(self.code)

        self.inputs: list[Connector] = []
        self.outputs: list[Connector] = []

        self._compiled_code: CodeType

    def execute(self, _locals:dict, _globals:dict) -> tuple[dict, dict]:
        print(f"Executing node {self.uuid}")

        # On Demand compilation of the node code
        if self.code_hash != hash(self.code):
            self._compiled_code = compile(self.code, "<string>", "exec")

        # create isolated copies so caller's dicts remain unchanged
        g = _globals.copy()
        l = _locals.copy()
        exec(self._compiled_code, g, l)
        print(f"Executed node {self.uuid}")
        return g, l

    def to_dict(self):
        return {
            "code": self.code,
            "uuid": self.uuid,
            "inputs": {in_conns.uuid: [p for p in in_conns.connections] for in_conns in self.inputs}, 
            "outputs": {out_conns.uuid: [p for p in out_conns.connections] for out_conns in self.outputs}
        }
    
    @staticmethod
    def from_dict(data: dict) -> "NodeData":
        """
        Erzeuge ein NodeData-Objekt aus dem von to_dict erzeugten dict.
        Erwartetes Format:
        {
            "code": str,
            "uuid": str|int,
            "inputs": { connector_uuid: [conn_uuid, ...], ... },
            "outputs": { connector_uuid: [conn_uuid, ...], ... }
        }
        """
        uuid: str = data.get("uuid", "")
        code: str = data.get("code", "")
        node = NodeData(uuid, code)

        inputs = data.get("inputs", {}) or {}
        outputs = data.get("outputs", {}) or {}

        for c_uuid, conn_list in inputs.items():
            c = Connector(c_uuid, node)
            c.type = ConnectorType.INPUT
            # sicherstellen, dass das connections-Attribut existiert
            c.connections = set(conn_list or [])
            node.inputs.append(c)

        for c_uuid, conn_list in outputs.items():
            c = Connector(c_uuid, node)
            c.type = ConnectorType.OUTPUT
            c.connections = set(conn_list or [])
            node.outputs.append(c)

        return node

class Connector:
    def __init__(self, tag: str, parent: NodeData) -> None:
        self.type: ConnectorType

        self.uuid: str = tag
        self.connections: set[Union[str, int]] = set()

        self.parent: NodeData

        self.name = "name"