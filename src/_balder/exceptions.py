from __future__ import annotations


class BalderException(Exception):
    """basic balder exception"""
    pass


class BalderWarning(Warning):
    """basic balder warning"""
    pass


class FixtureScopeError(BalderException):
    """is thrown for fixtures that were defined in an illegal scope"""
    pass


class FixtureReferenceError(BalderException):
    """
    is thrown when an error is detected in the reference between fixtures
    """
    pass


class UnclearSetupScopedFixtureReference(BalderException):
    """
    is thrown for the special UNCLEAR SETUP SCOPED FIXTURE REFERENCE error
    """
    pass


class UnclearUniqueClassReference(BalderException):
    """
    is thrown after balder can not clearly determine the related instance reference for a :class:`Scenario` or
    :class:`Setup` class
    """
    pass


class LostInExecutorTreeException(BalderException):
    """
    is thrown if you make a wrong call when entering and leaving the fixture manager, and you got lost
    """
    pass


class DeviceResolvingException(BalderException):
    """
    is thrown if an error occurs while resolving a device string
    """
    pass


class NodeNotExistsError(BalderException):
    """
    is thrown if no connection node exists for a device
    """
    pass


class DuplicateForVDeviceError(BalderException):
    """
    is thrown if some illegal `@for_vdevice` decorator exists for a feature
    """
    pass


class DuplicateBalderSettingError(BalderException):
    """
    is thrown if balder can not determine the BalderSettings object clearly.
    """
    pass


class VDeviceOverwritingError(BalderException):
    """
    is thrown if the device is not overwritten correctly
    """
    pass


class DeviceOverwritingError(BalderException):
    """
    is thrown if the device is not overwritten correctly
    """
    pass


class FeatureOverwritingError(BalderException):
    """
    is thrown if an inner instantiated feature is not overwritten correctly
    """
    pass


class UnknownVDeviceException(BalderException):
    """
    is thrown if some not allowed vDevices are given in a :meth:`Feature`
    """
    pass


class RoutingBrokenChainError(BalderException):
    """
    is thrown if the routing determines a broken pipe
    """
    pass


class IllegalConnectionTypeError(BalderException):
    """
    is thrown if the connection is illegal
    """
    pass


class ConnectionMetadataConflictError(BalderException):
    """
    is thrown if here is an illegal conflict between some metadata
    """
    pass


class DeviceScopeError(BalderException):
    """
    is thrown if the device class is placed on an illegal scope
    """
    pass


class ConnectionIntersectionError(BalderException):
    """
    is thrown if the intersection connection between two devices is reduced in a way that no intersection exists anymore
    """
    pass


class UnclearAssignableFeatureConnectionError(BalderException):
    """
    is thrown if two devices have parallel connections and a used feature could use both or more at the same time
    """
    pass


class InheritanceError(BalderException):
    """
    is thrown if a class inheritance is not allowed for the mentioned class
    """
    pass


class MultiInheritanceError(BalderException):
    """
    is thrown if multi inheritance was used where it is not allowed
    """
    pass


class InnerFeatureResolvingError(BalderException):
    """
    is thrown if an inner feature reference can not be resolved with the instantiated features of the device
    """
    pass


class VDeviceResolvingError(BalderException):
    """
    is thrown if there is an error while resolving VDevice's.
    """
    pass


class IllegalVDeviceMappingError(BalderException):
    """
    is thrown if there is an error while resolving vDevice mappings.
    """
    pass


class NotApplicableVariationError(BalderException):
    """
    is thrown internally after the current variation is not applicable
    """


class UnclearMethodVariationError(BalderException):
    """
    is thrown if there are more than one possible method variations possible
    """
    pass


class UnexpectedPluginMethodReturnValue(BalderException):
    """
    is thrown if a user plugin doesn't return something or returns wrong values in its plugin method
    """
    pass
