from _balder.vdevice import VDevice
from _balder.exceptions import AccessToUnmappedVDeviceException


class UnmappedVDevice(VDevice):
    """
    This special vdevice class will be assigned to all existing VDevice's that are not mapped during the execution of
    a variation.
    """

    def __getattr__(self, item):
        raise AccessToUnmappedVDeviceException('it is not allowed to access the attributes of an unmapped VDevice - '
                                               'did you forget to map it?')
