import balder


class ParentConnection(balder.Connection):
    pass


@balder.insert_into_tree(parents=[ParentConnection])
class BetweenConnection(balder.Connection):
    pass


@balder.insert_into_tree(parents=[BetweenConnection])
class ChildConnection(balder.Connection):
    pass
