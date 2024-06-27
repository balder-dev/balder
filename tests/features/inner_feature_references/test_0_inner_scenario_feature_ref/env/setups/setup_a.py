import balder
import logging
from .setup_features import SetupFeatureI, SetupFeatureII, SetupFeatureIII, SetupFeatureIV
from ..lib.connections import AConnection
from ..balderglob import RuntimeObserver

logger = logging.getLogger(__name__)


class SetupA(balder.Setup):
    """This is a setup of category A (exactly the same as scenario A)"""

    class SetupDevice1(balder.Device):
        s_i = SetupFeatureI()
        s_ii = SetupFeatureII()

    @balder.connect(SetupDevice1, over_connection=AConnection)
    class SetupDevice2(balder.Device):
        s_iii = SetupFeatureIII()
        s_iv = SetupFeatureIV()

    @balder.fixture(level="session")
    def fixture_session(self):
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_session, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice1.s_ii.do_something()
        self.SetupDevice2.s_iii.do_something()
        self.SetupDevice2.s_iv.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_session, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice1.s_ii.do_something()
        self.SetupDevice2.s_iii.do_something()
        self.SetupDevice2.s_iv.do_something()

    @balder.fixture(level="setup")
    def fixture_setup(self):
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_setup, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice1.s_ii.do_something()
        self.SetupDevice2.s_iii.do_something()
        self.SetupDevice2.s_iv.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_setup, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice1.s_ii.do_something()
        self.SetupDevice2.s_iii.do_something()
        self.SetupDevice2.s_iv.do_something()

    @balder.fixture(level="scenario")
    def fixture_scenario(self):
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_scenario, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice1.s_ii.do_something()
        self.SetupDevice2.s_iii.do_something()
        self.SetupDevice2.s_iv.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_scenario, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice1.s_ii.do_something()
        self.SetupDevice2.s_iii.do_something()
        self.SetupDevice2.s_iv.do_something()

    @balder.fixture(level="variation")
    def fixture_variation(self):
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_variation, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice1.s_ii.do_something()
        self.SetupDevice2.s_iii.do_something()
        self.SetupDevice2.s_iv.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_variation, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice1.s_ii.do_something()
        self.SetupDevice2.s_iii.do_something()
        self.SetupDevice2.s_iv.do_something()

    @balder.fixture(level="testcase")
    def fixture_testcase(self):
        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_testcase, category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice1.s_ii.do_something()
        self.SetupDevice2.s_iii.do_something()
        self.SetupDevice2.s_iv.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupA, SetupA.fixture_testcase, category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
        self.SetupDevice1.s_ii.do_something()
        self.SetupDevice2.s_iii.do_something()
        self.SetupDevice2.s_iv.do_something()
