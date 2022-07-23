import balder
import logging
from .setup_features import SetupFeatureIII, SetupFeatureIV
from ..lib.connections import BConnection
from ..balderglob import RuntimeObserver

logger = logging.getLogger(__name__)


class SetupB(balder.Setup):
    """This is a setup of category B (exactly the same as scenario B)"""

    class SetupDevice3(balder.Device):
        s_iii = SetupFeatureIII()

    @balder.connect(SetupDevice3, over_connection=BConnection)
    class SetupDevice4(balder.Device):
        s_iv = SetupFeatureIV()

    @balder.fixture(level="session")
    def fixture_session(self):
        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_session,  category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")
        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_session,  category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")
        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()

    @balder.fixture(level="setup")
    def fixture_setup(self):
        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_setup,  category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")
        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_setup,  category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")
        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()

    @balder.fixture(level="scenario")
    def fixture_scenario(self):
        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_scenario,  category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")
        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_scenario,  category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")
        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()

    @balder.fixture(level="variation")
    def fixture_variation(self):
        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_variation,  category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")
        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_variation,  category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")
        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()

    @balder.fixture(level="testcase")
    def fixture_testcase(self):
        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_testcase,  category="fixture", part="construction",
                                  msg="begin execution CONSTRUCTION of fixture")
        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupB, SetupB.fixture_testcase,  category="fixture", part="teardown",
                                  msg="begin execution TEARDOWN of fixture")
        self.SetupDevice3.s_iii.do_something()
        self.SetupDevice4.s_iv.do_something()
