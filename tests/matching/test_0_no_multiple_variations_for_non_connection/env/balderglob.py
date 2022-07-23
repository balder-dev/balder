from typing import Literal, Union, List
from datetime import datetime

import pathlib
import balder
import argparse
import inspect
import logging

logger = logging.getLogger(__file__)


class MyTestException(Exception):
    pass


class RuntimeObserver:
    """This is a helper object, that will be used from this test environment to observe the execution order"""
    data = []

    error_throwing = {}

    @staticmethod
    def add_entry(file: Union[str, pathlib.Path], cls: object, meth: callable, msg: str,
                  category: Literal["fixture", "testcase", "feature"] = None,
                  part: Literal["construction", "teardown"] = None):
        """
        adds a new entry into the internal data

        :param file: the full filepath where the log will be generated

        :param cls: the class object, the entry is generated in

        :param meth: the method name, the entry is generated in

        :param msg: the message that should be inserted into the entry

        :param category: optional string of the category the entry is from

        :param part: optional string of the sub part the entry is from
        """
        if hasattr(meth, 'fn'):
            meth = meth.fn
        new_dataset = {
            "timestamp": datetime.now(), "file": file, "cls": cls, "meth": meth, "msg": msg, "category": category,
            "part": part
        }
        logger.info("{:16} | {:16} | {:30} | {:12} | {:15} | {}".format(
            pathlib.Path(file).parts[-1], "" if cls is None else cls.__name__, "" if meth is None else meth.__name__,
            "" if category is None else category, "" if part is None else part, "" if msg is None else msg))

        RuntimeObserver.data.append(new_dataset)
        # check if we have to throw the error
        error_throwing_required = len(RuntimeObserver.error_throwing) > 0
        for cur_key in RuntimeObserver.error_throwing.keys():
            new_dataset_val = new_dataset[cur_key]
            if callable(new_dataset_val):
                new_dataset_val = new_dataset_val.__name__
            if new_dataset_val != RuntimeObserver.error_throwing[cur_key]:
                error_throwing_required = False
                break
        if error_throwing_required:
            raise MyTestException(f'raise test triggered exception for `{str(RuntimeObserver.error_throwing)}`')


class MyErrorThrowingPlugin(balder.BalderPlugin):
    """
    This is a plugin that reads the values from console arguments and sets these values into the
    :class:`RuntimeObserver`. The static method `RuntimeObserver.add_entry` will automatically throw an exception on the
    given position.
    """

    def addoption(self, argument_parser: argparse.ArgumentParser):
        argument_parser.add_argument('--test-error-file', help='the file id, the error should be thrown in')
        argument_parser.add_argument('--test-error-cls', help='the class id, the error should be thrown in')
        argument_parser.add_argument('--test-error-meth', help='the meth id, the error should be thrown in')
        argument_parser.add_argument('--test-error-part', help='the part (`construct` or `teardown`), the error should '
                                                               'be thrown in - only for fixtures')

    def modify_collected_pyfiles(self, pyfiles: List[pathlib.Path]) -> List[pathlib.Path]:
        # use this method to set the values
        RuntimeObserver.error_throwing = {}
        if self.balder_session.parsed_args.test_error_file:
            RuntimeObserver.error_throwing['file'] = self.balder_session.parsed_args.test_error_file
        if self.balder_session.parsed_args.test_error_cls:
            RuntimeObserver.error_throwing['cls'] = self.balder_session.parsed_args.test_error_cls
        if self.balder_session.parsed_args.test_error_meth:
            RuntimeObserver.error_throwing['meth'] = self.balder_session.parsed_args.test_error_meth
        if self.balder_session.parsed_args.test_error_part:
            RuntimeObserver.error_throwing['part'] = self.balder_session.parsed_args.test_error_part
        return pyfiles


@balder.fixture(level="session")
def balderglob_fixture_session():
    RuntimeObserver.add_entry(__file__, None, balderglob_fixture_session, "begin execution CONSTRUCTION of fixture",
                              category="fixture", part="construction")

    yield

    RuntimeObserver.add_entry(__file__, None, balderglob_fixture_session, "begin execution TEARDOWN of fixture",
                              category="fixture", part="teardown")


@balder.fixture(level="setup")
def balderglob_fixture_setup():
    RuntimeObserver.add_entry(__file__, None, balderglob_fixture_setup, "begin execution CONSTRUCTION of fixture",
                              category="fixture", part="construction")

    yield

    RuntimeObserver.add_entry(__file__, None, balderglob_fixture_setup, "begin execution TEARDOWN of fixture",
                              category="fixture", part="teardown")


@balder.fixture(level="scenario")
def balderglob_fixture_scenario():
    RuntimeObserver.add_entry(__file__, None, balderglob_fixture_scenario, "begin execution CONSTRUCTION of fixture",
                              category="fixture", part="construction")

    yield

    RuntimeObserver.add_entry(__file__, None, balderglob_fixture_scenario, "begin execution TEARDOWN of fixture",
                              category="fixture", part="teardown")


@balder.fixture(level="variation")
def balderglob_fixture_variation():
    RuntimeObserver.add_entry(__file__, None, balderglob_fixture_variation, "begin execution CONSTRUCTION of fixture",
                              category="fixture", part="construction")

    yield

    RuntimeObserver.add_entry(__file__, None, balderglob_fixture_variation, "begin execution TEARDOWN of fixture",
                              category="fixture", part="teardown")


@balder.fixture(level="testcase")
def balderglob_fixture_testcase():
    RuntimeObserver.add_entry(__file__, None, balderglob_fixture_testcase, "begin execution CONSTRUCTION of fixture",
                              category="fixture", part="construction")

    yield

    RuntimeObserver.add_entry(__file__, None, balderglob_fixture_testcase, "begin execution TEARDOWN of fixture",
                              category="fixture", part="teardown")
