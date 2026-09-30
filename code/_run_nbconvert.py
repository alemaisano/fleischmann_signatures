import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

sys.argv = [
    "jupyter-nbconvert",
    "--to", "notebook",
    "--execute", "--inplace",
    "--ExecutePreprocessor.timeout=-1",
    "--ExecutePreprocessor.kernel_name=fleischmann-fixed",
    "code/zurich_city.ipynb",
]

from nbconvert.nbconvertapp import main

main()
