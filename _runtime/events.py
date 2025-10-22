from typing import Callable, Dict, List, Any, Optional
from queue import Queue, Empty
from threading import Thread, Event
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)

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

    LOAD_FILE = "cmd:load"
    LOADED = "loaded"

    # EXECUTION


class EventBus:
    """
    Threaded EventBus: by default `emit` enqueues events for asynchronous delivery
    by a background worker thread. Use `emit_sync` for immediate, synchronous
    dispatch (useful in tests or during initialization).

    Call `stop()` to shut down the worker thread cleanly.
    """

    def __init__(self, threaded: bool = False) -> None:
        self._listeners: Dict[Events, List[Callable[[Any], None]]] = {}
        self._queue: Queue = Queue()
        self._stop_evt: Event = Event()
        self._worker: Optional[Thread] = None

        # only start worker when explicitly requested
        if threaded:
            self._worker = Thread(target=self._run, daemon=True)
            self._worker.start()

        print("EventBus initialized (threaded=%s)" % threaded)

    def subscribe(self, name: Events, callback: Callable[[Any], None]):
        """Subscribe to an event. Returns the callback for convenience."""
        logging.debug("Registering listener for %s", name)
        self._listeners.setdefault(name, []).append(callback)
        return callback

    def unsubscribe(self, name: Events, callback: Callable[[Any], None]):
        """Unsubscribe a previously subscribed callback."""
        logging.debug("Unregistering listener for %s", name)
        if name in self._listeners:
            try:
                self._listeners[name].remove(callback)
            except ValueError:
                logging.debug("callback not found for %s", name)

    def emit(self, name: Events, payload: Any = None) -> None:
        """Enqueue an event for later delivery by either worker or main-thread poll()."""
        logging.debug("Emitting %s (queued)", name)
        self._queue.put((name, payload))

    def emit_sync(self, name: Events, payload: Any = None) -> None:
        """Immediately dispatch event to listeners on the caller thread."""
        logging.debug("Emitting sync %s", name)
        for cb in list(self._listeners.get(name, [])):
            try:
                cb(payload)
            except Exception:
                logging.exception("listener raised in emit_sync for %s", name)

    def poll(self, max_items: int = 100) -> None:
        """Process up to max_items events from the queue synchronously (safe to call from main thread)."""
        processed = 0
        while processed < max_items:
            try:
                name, payload = self._queue.get_nowait()
            except Empty:
                break
            for cb in list(self._listeners.get(name, [])):
                try:
                    cb(payload)
                except Exception:
                    logging.exception("listener raised while polling %s", name)
            processed += 1

    def _run(self) -> None:
        # worker loop: block and dispatch; same dispatch logic but runs in worker thread
        while not self._stop_evt.is_set():
            try:
                name, payload = self._queue.get(timeout=0.1)
            except Empty:
                continue
            for cb in list(self._listeners.get(name, [])):
                try:
                    cb(payload)
                except Exception:
                    pass

    def stop(self) -> None:
        self._stop_evt.set()
        if self._worker and self._worker.is_alive():
            self._worker.join(timeout=0.5)
