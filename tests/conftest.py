import pathlib
import pytest
import logging

logging.basicConfig(
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-7.7s]  %(message)s", level=logging.DEBUG)


@pytest.fixture(scope="function")
def balder_working_dir(request) -> pathlib.Path:
    DIR_NAME = "env"

    filepath = pathlib.Path(request.node.fspath)
    session_working_dir = filepath.parent.joinpath(DIR_NAME)
    if session_working_dir.is_dir():
        return session_working_dir
    else:
        raise NotADirectoryError(f"can not find the testfile related working directory `{DIR_NAME}` for test file "
                                 f"`{filepath.relative_to(request.config.rootdir)}`")
