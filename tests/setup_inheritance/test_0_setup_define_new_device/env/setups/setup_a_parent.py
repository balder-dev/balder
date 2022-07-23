import balder
import logging
from .setup_features import SetupFeatureI
from ..balderglob import RuntimeObserver

logger = logging.getLogger(__name__)


class SetupAParent(balder.Setup):
    """This is a setup of category A (exactly the same as scenario A)"""

    class SetupDevice1(balder.Device):
        s_i = SetupFeatureI()

    # the `SetupDevice2` is not defined here

    @balder.fixture(level="session")
    def fixture_session(self):
        RuntimeObserver.add_entry(__file__, SetupAParent, SetupAParent.fixture_session, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupAParent, SetupAParent.fixture_session, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()

    @balder.fixture(level="setup")
    def fixture_setup(self):
        RuntimeObserver.add_entry(__file__, SetupAParent, SetupAParent.fixture_setup, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupAParent, SetupAParent.fixture_setup, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()

    @balder.fixture(level="scenario")
    def fixture_scenario(self):
        RuntimeObserver.add_entry(__file__, SetupAParent, SetupAParent.fixture_scenario, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupAParent, SetupAParent.fixture_scenario, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()

    @balder.fixture(level="variation")
    def fixture_variation(self):
        RuntimeObserver.add_entry(__file__, SetupAParent, SetupAParent.fixture_variation, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupAParent, SetupAParent.fixture_variation, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()

    @balder.fixture(level="testcase")
    def fixture_testcase(self):
        RuntimeObserver.add_entry(__file__, SetupAParent, SetupAParent.fixture_testcase, category="fixture",
                                  part="construction", msg="begin execution CONSTRUCTION of fixture")

        self.SetupDevice1.s_i.do_something()

        yield

        RuntimeObserver.add_entry(__file__, SetupAParent, SetupAParent.fixture_testcase, category="fixture",
                                  part="teardown", msg="begin execution TEARDOWN of fixture")

        self.SetupDevice1.s_i.do_something()
