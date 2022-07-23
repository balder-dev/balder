import balder
import logging

logger = logging.getLogger(__file__)


class MySettings(balder.BalderSettings):
    """This is our own setting object"""
    used_global_connection_tree = "some-never-used-custom-name"
