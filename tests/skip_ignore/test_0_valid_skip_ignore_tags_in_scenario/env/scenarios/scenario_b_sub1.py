from .scenario_b_parent import ScenarioBParent
from ..balderglob import RuntimeObserver


class ScenarioBSub1(ScenarioBParent):
    SKIP = ['test_b_3']

    def test_b_3(self):
        RuntimeObserver.add_entry(__file__, ScenarioBSub1, ScenarioBSub1.test_b_3, category="testcase",
                                  msg=f"execute Test `{ScenarioBSub1.test_b_3.__qualname__}`")
        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()
