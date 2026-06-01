from concurrent.futures import ThreadPoolExecutor
from typing import Callable

_executor = ThreadPoolExecutor(max_workers=4)

# Default dispatcher runs the callback directly (tests and MCP headless).
# Qt wire:  set_main_thread_dispatcher(lambda fn: QTimer.singleShot(0, fn)) in commandeck_qt/app.py.
_dispatch_to_main: Callable[[Callable], None] = lambda fn: fn()


def set_main_thread_dispatcher(fn: Callable[[Callable], None]) -> None:
    global _dispatch_to_main
    _dispatch_to_main = fn


def run_in_thread(func: Callable, callback: Callable, *args):
    def _done(future):
        try:
            result = future.result()
        except Exception as e:
            result = e
        _dispatch_to_main(lambda: callback(result))

    _executor.submit(func, *args).add_done_callback(_done)
