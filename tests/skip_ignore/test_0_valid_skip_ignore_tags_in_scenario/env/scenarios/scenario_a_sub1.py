from .scenario_a_parent import ScenarioAParent


class ScenarioASub1(ScenarioAParent):
    SKIP = ['test_a_3']
