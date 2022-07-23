from __future__ import annotations


class BalderSettings:
    """
    This class can be overwritten to manipulate the default settings for the balder test system. You can overwrite these
    settings by defining a subclass in your `balderglob.py`.
    """

    #: specifies that the test run should include duplicated tests that are declared as ``@covered_by`` another test
    #:   method
    force_covered_by_duplicates = False

    #: specifies the connection tree identifier that should be used as global identifier ("" is the default one)
    used_global_connection_tree = ""
