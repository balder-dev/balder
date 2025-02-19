from .scenario_b_parent import ScenarioBParent
from ..balderglob import RuntimeObserver


class ScenarioBSub2(ScenarioBParent):
    IGNORE = ['test_b_1']
    SKIP = ['test_b_2']

    def test_b_3(self):
        RuntimeObserver.add_entry(__file__, ScenarioBSub2, ScenarioBSub2.test_b_3, category="testcase",
                                  msg=f"execute Test `{ScenarioBSub2.test_b_3.__qualname__}`")
        self.ScenarioDevice3.iii.do_something()
        self.ScenarioDevice4.iv.do_something()
