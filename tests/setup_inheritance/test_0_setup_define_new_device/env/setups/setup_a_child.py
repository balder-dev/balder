import balder
import logging
from .setup_features import SetupFeatureI, SetupFeatureII
from ..lib.connections import AConnection
from ..balderglob import RuntimeObserver
from .setup_a_parent import SetupAParent

logger = logging.getLogger(__name__)


class SetupAChild(SetupAParent):
    """This is a setup of category A (exactly the same as scenario A)"""

    class SetupDevice1(SetupAParent.SetupDevice1):
        s_i = SetupFeatureI()

    @balder.connect(SetupDevice1, over_connection=AConnection)
    class SetupDevice2(balder.Device):
        s_ii = SetupFeatureII()

    @balder.fixture(level="session")
    def fixture_session(self):
        RuntimeObserver.add_entry(__file__, SetupAChild, SetupAChild.fixture_session, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupAChild, SetupAChild.fixture_session, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="setup")
    def fixture_setup(self):
        RuntimeObserver.add_entry(__file__, SetupAChild, SetupAChild.fixture_setup, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupAChild, SetupAChild.fixture_setup, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="scenario")
    def fixture_scenario(self):
        RuntimeObserver.add_entry(__file__, SetupAChild, SetupAChild.fixture_scenario, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupAChild, SetupAChild.fixture_scenario, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="variation")
    def fixture_variation(self):
        RuntimeObserver.add_entry(__file__, SetupAChild, SetupAChild.fixture_variation, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupAChild, SetupAChild.fixture_variation, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="testcase")
    def fixture_testcase(self):
        RuntimeObserver.add_entry(__file__, SetupAChild, SetupAChild.fixture_testcase, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupAChild, SetupAChild.fixture_testcase, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()
