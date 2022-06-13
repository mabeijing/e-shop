"""
Built-in functions used in YAML/JSON testcases.
"""

import datetime
import random
import string
import time

from httprunner.exceptions import ParamsError


def gen_random_string(str_len):
    """ generate random string with specified length
    """
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(str_len)
    )


def get_timestamp(str_len: int = 13) -> str:
    """ get timestamp string, length can only between 0 and 16
    """
    if isinstance(str_len, int) and 0 < str_len < 17:
        return str(time.time()).replace(".", "")[:str_len]

    raise ParamsError("timestamp length can only between 0 and 16.")


def get_current_date(fmt="%Y-%m-%d") -> str:
    """ get current date, default format is %Y-%m-%d
    """
    return datetime.datetime.now().strftime(fmt)


def sleep(n_secs: float):
    """ sleep n seconds
    """
    time.sleep(n_secs)
