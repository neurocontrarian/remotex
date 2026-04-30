from concurrent.futures import ThreadPoolExecutor
from gi.repository import GLib
from typing import Callable

_executor = ThreadPoolExecutor(max_workers=4)


def run_in_thread(func: Callable, callback: Callable, *args):
    """Run func(*args) in a background thread.
    When done, schedule callback(result) on the GLib main loop.
    This keeps the GTK UI responsive during long-running operations.
    """
    def _done(future):
        result = future.result()
        GLib.idle_add(callback, result)

    future = _executor.submit(func, *args)
    future.add_done_callback(_done)
