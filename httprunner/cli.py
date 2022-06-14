"""
命令行启动参数
需要完成 生成脚本，并且执行
"""
import typing
import enum
from httprunner import __BASE_PATH__
import sys
import pytest
from loguru import logger

from httprunner import __version__

from httprunner.make import main_make

if typing.TYPE_CHECKING:
    from pathlib import Path


def run(extra_args: list) -> enum.IntEnum:
    tests_path_list: list[Path] = []
    extra_args_new: list[str] = []
    for item in extra_args:
        item: str
        _path: Path = __BASE_PATH__.joinpath('resource', item)
        if _path.exists():
            tests_path_list.append(_path)
        else:
            extra_args_new.append(item)

    if len(tests_path_list) == 0:
        # has not specified any testcase path
        logger.error(f"No valid testcase path in cli arguments: {extra_args}")
        sys.exit(1)

    testcase_path_list = main_make(tests_path_list)
    if not testcase_path_list:
        logger.error("No valid testcases found, exit 1.")
        sys.exit(1)

    if "--tb=short" not in extra_args_new:
        extra_args_new.append("--tb=short")

    extra_args_new.extend(testcase_path_list)
    logger.info(f"start to run tests with pytest. HttpRunner version: {__version__}")
    return pytest.main(extra_args_new)


if __name__ == "__main__":
    run(['-v', 'testcase/userlogin.yml'])
