"""Kernel launcher identical to ipykernel_launcher.py, except it forces the
Windows selector event loop policy first -- the default Proactor loop is
flaky with zmq/dask-distributed on this machine and has caused repeated
silent kernel hangs during long automated nbconvert runs.
"""
import sys
from pathlib import Path

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        import asyncio

        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    if sys.path[0] == "" or Path(sys.path[0]) == Path.cwd():
        del sys.path[0]

    from ipykernel import kernelapp as app

    app.launch_new_instance()
