# user define function

import time
from typing import Sequence, Union, NoReturn


def get_httprunner_version():
    return "v4.0.0-beta"


def sleep(n_secs: Union[int, float]) -> NoReturn:
    time.sleep(n_secs)


def sum_sequence(args: Sequence[int]) -> int:
    result = 0
    for arg in args:
        result += arg
    return result


def join_sequence(sequence: Sequence[str]) -> str:
    return "".join(sequence)
