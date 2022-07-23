import balder
import logging
from .setup_features import SetupFeatureI, SetupFeatureII
from ..lib.connections import ChildBConnection, ParentConnection
from ..balderglob import RuntimeObserver

logger = logging.getLogger(__name__)


class SetupAWorking(balder.Setup):
    """This is a setup of category A, that uses the `ChildBConnection`. This should match, because the used
    `FeatureII` only allows the `ChildBConnection`"""

    class SetupDevice1(balder.Device):
        s_i = SetupFeatureI()

    @balder.connect(SetupDevice1, over_connection=ChildBConnection.based_on(ParentConnection))
    class SetupDevice2(balder.Device):
        s_ii = SetupFeatureII(VDeviceFeatureI="SetupDevice1")

    @balder.fixture(level="session")
    def fixture_session(self):
        RuntimeObserver.add_entry(__file__, SetupAWorking, SetupAWorking.fixture_session, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupAWorking, SetupAWorking.fixture_session, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="setup")
    def fixture_setup(self):
        RuntimeObserver.add_entry(__file__, SetupAWorking, SetupAWorking.fixture_setup, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupAWorking, SetupAWorking.fixture_setup, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="scenario")
    def fixture_scenario(self):
        RuntimeObserver.add_entry(__file__, SetupAWorking, SetupAWorking.fixture_scenario, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupAWorking, SetupAWorking.fixture_scenario, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="variation")
    def fixture_variation(self):
        RuntimeObserver.add_entry(__file__, SetupAWorking, SetupAWorking.fixture_variation, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupAWorking, SetupAWorking.fixture_variation, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

    @balder.fixture(level="testcase")
    def fixture_testcase(self):
        RuntimeObserver.add_entry(__file__, SetupAWorking, SetupAWorking.fixture_testcase, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupAWorking, SetupAWorking.fixture_testcase, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice2.s_ii.do_something()
