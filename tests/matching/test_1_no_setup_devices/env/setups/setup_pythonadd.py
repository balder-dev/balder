import balder
from ..lib.utils import SharedObj


class SetupPythonAdd(balder.Setup):

    # NOTE: This setup does not implement some devices

    @balder.fixture(level="testcase")
    def cleanup_memory(self):
        SharedObj.shared_mem_list = []
