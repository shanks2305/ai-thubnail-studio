import queue
import threading
from typing import Any


class EventBus:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._subscribers: dict[str, list[queue.Queue[dict[str, Any]]]] = {}
        self._history: dict[str, list[dict[str, Any]]] = {}

    def publish(self, project_id: str, event: dict[str, Any]) -> None:
        with self._lock:
            history = self._history.setdefault(project_id, [])
            history.append(event)
            del history[:-200]
            subscribers = list(self._subscribers.get(project_id, []))
        for subscriber in subscribers:
            subscriber.put(event)

    def subscribe(self, project_id: str) -> queue.Queue[dict[str, Any]]:
        subscriber: queue.Queue[dict[str, Any]] = queue.Queue()
        with self._lock:
            history = list(self._history.get(project_id, []))
            self._subscribers.setdefault(project_id, []).append(subscriber)
        for event in history:
            subscriber.put(event)
        return subscriber

    def unsubscribe(self, project_id: str, subscriber: queue.Queue[dict[str, Any]]) -> None:
        with self._lock:
            subscribers = self._subscribers.get(project_id, [])
            if subscriber in subscribers:
                subscribers.remove(subscriber)

    def clear(self) -> None:
        with self._lock:
            self._subscribers.clear()
            self._history.clear()

    def clear_project(self, project_id: str) -> None:
        with self._lock:
            self._subscribers.pop(project_id, None)
            self._history.pop(project_id, None)


bus = EventBus()


def publish(project_id: str, event: dict[str, Any]) -> None:
    bus.publish(project_id, event)
