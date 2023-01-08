from enum import Enum


class ExitCode(Enum):
    """
    This enum describes the balder exit codes.
    """
    #: tests were collected and all tests and fixtures terminates with success
    SUCCESS = 0
    #: tests were collected but some tests failed
    TESTS_FAILED = 1
    #: test was interrupted by user
    USER_INTERRUPT = 2
    #: an internal unexpected error occurs
    UNEXPECTED_ERROR = 3
    #: Balder usage error
    BALDER_USAGE_ERROR = 4
    #: no tests were collected
    NO_TESTS_COLLECTED = 5
