from enum import Enum
from typing import Union

class ConnectorType(Enum):
    INPUT = 0
    OUTPUT = 1

class Connector:
    def __init__(self, tag: str | int) -> None:
        self.type: ConnectorType

        self.uuid: str | int = tag
        self.connections: set[Union[str, int]] = set()

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "connections": list(self.connections)
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Connector":
        tag = data.get("uuid", -1)
        conn = cls(tag)

        # optionales 'type' Feld handhaben (Name oder Wert)
        t = data.get("type")
        if t is not None:
            try:
                conn.type = ConnectorType[t] if isinstance(t, str) else ConnectorType(t)
            except Exception:
                # unbekannter Typ -> ignorieren, Standard belassen
                pass

        # Verbindungen als set wiederherstellen
        conn.connections = set(data.get("connections", []))
        return conn
