"""Thread-safe dispatcher: worker thread → Qt main thread.

QTimer.singleShot(0, fn) called from a non-Qt thread has no event loop
and never fires. The signal/slot mechanism with Qt.QueuedConnection is
the correct Qt idiom: emitting from any thread delivers the slot call
in the receiver's thread (the main thread here).
"""
from PySide6.QtCore import QObject, Signal, Qt


class _Dispatcher(QObject):
    _call = Signal(object)

    def __init__(self):
        super().__init__()
        self._call.connect(self._invoke, Qt.QueuedConnection)

    def _invoke(self, fn):
        fn()

    def dispatch(self, fn):
        self._call.emit(fn)


_instance: _Dispatcher | None = None


def get_dispatcher() -> _Dispatcher:
    global _instance
    if _instance is None:
        _instance = _Dispatcher()
    return _instance
