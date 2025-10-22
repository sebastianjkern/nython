from types import CodeType
from nython.core.runtime.connector import Connector, ConnectorType

class NodeData:
    def __init__(self, uuid: str|int, code:str) -> None:
        self.uuid: str|int = uuid
        self.code: str = code
        self.title: str = "Name"

        self.inputs: list[Connector] = []
        self.outputs: list[Connector] = []

        self.code_hash: int = hash(self.code)
        self._compiled_code: CodeType

    def _compile(self):
        self._compiled_code = compile(self.code, "<string>", "exec")

    def set_code(self, code: str):
        self.code = code

        self._compile()

    def execute(self, _locals: dict, _globals: dict) -> tuple[dict, dict]:
        print(f"Executing node {self.uuid}")

        self._compile()

        # create isolated copies so caller's dicts remain unchanged
        g = _globals.copy()
        l = _locals.copy()
        exec(self._compiled_code, g, l)
        print(f"Executed node {self.uuid}")
        return g, l

    def to_dict(self):
        return {
            "name": self.title,
            "code": self.code,
            "uuid": self.uuid,
            "inputs": [in_conns.to_dict() for in_conns in self.inputs], 
            "outputs": [out_conns.to_dict() for out_conns in self.outputs]
        }
    
    @staticmethod
    def from_dict(data: dict) -> "NodeData":
        """
        Erzeuge ein NodeData-Objekt aus dem von to_dict erzeugten dict.
        Erwartetes Format (nur neues Format):
        {
            "name": str,
            "code": str,
            "uuid": str|int,
            "inputs": { connector_uuid: connector_dict, ... },
            "outputs": { connector_uuid: connector_dict, ... }
        }
        """
        uuid: int = data.get("uuid", 0)
        code: str = data.get("code", "")
        title: str = data.get("name", "Imported Node")

        node = NodeData(uuid, code)
        node.title = title

        inputs = data.get("inputs", []) or []
        outputs = data.get("outputs", []) or []

        for conn_data in inputs:
            c = Connector.from_dict(conn_data)
            c.type = ConnectorType.INPUT
            node.inputs.append(c)

        for conn_data in outputs:
            c = Connector.from_dict(conn_data)
            c.type = ConnectorType.OUTPUT
            node.outputs.append(c)

        return node
