from types import CodeType
from typing import Any

class NodeData:
    def __init__(self, uuid: str, code:str) -> None:
        self.uuid: str = uuid
        self.code: str = code
        self._compiled_code: CodeType

        self.parents: list[NodeData] = []
        self.children:list[NodeData] = []

        if code is not None:
            print(f"Initial node {self.uuid} code compilation")
            self._compiled_code = compile(code, "<string>", "exec")

    def set_code(self, code: str) -> None:
        print(f"Recompiling node {self.uuid} code")
        self._compiled_code = compile(code, "<string>", "exec")

    def execute(self, _locals:dict, _globals:dict) -> tuple[dict, dict]:
        print(f"Executing node {self.uuid}")
        # create isolated copies so caller's dicts remain unchanged
        g = _globals.copy()
        l = _locals.copy()
        exec(self._compiled_code, g, l)
        print(f"Executed node {self.uuid}")
        return g, l

    def to_dict(self) -> dict[str, str | list[str]]:
        return {
            "code": self.code, 
            "uuid": self.uuid,
            "parents": [p.uuid for p in self.parents], 
            "children": [c.uuid for c in self.children]
        }
