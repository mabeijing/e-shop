from pathlib import Path

__version__ = "3.1.11"
__description__ = "One-stop solution for HTTP(S) testing."

# import firstly for monkey patch if needed
from httprunner.parser import parse_parameters as Parameters
from httprunner.runner import HttpRunner
from httprunner.testcase import Config, Step, RunRequest, RunTestCase

__BASE_PATH__: Path = Path(__file__).parent.parent
__all__ = [
    "__version__",
    "__description__",
    "HttpRunner",
    "Config",
    "Step",
    "RunRequest",
    "RunTestCase",
    "Parameters",
    "__BASE_PATH__"
]
