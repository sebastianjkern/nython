from typing import Callable, Dict, List, Any, Optional
from queue import Queue, Empty
from threading import Thread, Event

from enum import Enum

class Events(Enum):
    pass

class RuntimeEvents(Events):
    # Request Change
    CREATE_NODE = "cmd:create_node"
    REM_NODE = "cmd:remove_node"
    CONNECT = "cmd:connect"
    DISCONNECT = "cmd:disconnect"

    # Change Happened
    NODE_CREATED = "node_added"
    NODE_REMOVED = "node_removed"

    CONN_ESTABLISHED = "connection_added"
    CONN_REMOVED = "connection_removed"

    # IO
    SAVE = "cmd:save"
    LOADED = "loaded"

    # EXECUTION


class EventBus:
    """
    Threaded EventBus: by default `emit` enqueues events for asynchronous delivery
    by a background worker thread. Use `emit_sync` for immediate, synchronous
    dispatch (useful in tests or during initialization).

    Call `stop()` to shut down the worker thread cleanly.
    """

    def __init__(self) -> None:
        self._listeners: Dict[Events, List[Callable[[Any], None]]] = {}
        self._queue: Queue = Queue()
        self._stop_evt: Event = Event()
        self._worker: Optional[Thread] = Thread(target=self._run, daemon=True)
        self._worker.start()

        print("Started EventBus...")

    def subscribe(self, name: Events, callback: Callable[[Any], None]):
        """Subscribe to an event. Returns the callback for convenience."""
        print(f"Registered listener for {name}")
        
        self._listeners.setdefault(name, []).append(callback)
        return callback

    def unsubscribe(self, name: str, callback: Callable[[Any], None]):
        """Unsubscribe a previously subscribed callback."""
        print(f"Un-registered listener for {name}")
        
        if name in self._listeners:
            try:
                self._listeners[name].remove(callback)
            except ValueError:
                pass

    def emit(self, name: str, payload: Any = None) -> None:
        """Asynchronously enqueue an event for delivery by the worker thread."""
        print(f"Emitted {name}")
        
        self._queue.put((name, payload))

    def emit_sync(self, name: Events, payload: Any = None) -> None:
        """Deliver event synchronously to listeners. Exceptions are swallowed."""
        print(f"Emitted Synced {name}")
        
        for cb in list(self._listeners.get(name, [])):
            try:
                cb(payload)
            except Exception:
                pass

    def _run(self) -> None:
        while not self._stop_evt.is_set():
            try:
                name, payload = self._queue.get(timeout=0.1)
            except Empty:
                continue
            for cb in list(self._listeners.get(name, [])):
                try:
                    cb(payload)
                except Exception:
                    # swallow listener exceptions; they must not kill the worker
                    pass
            self._queue.task_done()

    def stop(self) -> None:
        """Stop the background worker and wait for it to exit."""
        self._stop_evt.set()
        if self._worker and self._worker.is_alive():
            self._worker.join(timeout=1.0)
