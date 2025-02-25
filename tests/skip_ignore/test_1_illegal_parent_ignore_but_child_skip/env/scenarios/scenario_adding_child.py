from .scenario_adding_parent import ScenarioAddingParent


class ScenarioAddingChild(ScenarioAddingParent):
    SKIP = ['test_add_two_numbers']
