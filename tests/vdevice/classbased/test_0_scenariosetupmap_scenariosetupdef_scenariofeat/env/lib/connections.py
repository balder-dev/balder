import balder


@balder.insert_into_tree()
class ParentConnection(balder.Connection):
    pass


@balder.insert_into_tree(parents=[ParentConnection])
class ChildAConnection(balder.Connection):
    pass


@balder.insert_into_tree(parents=[ParentConnection])
class ChildBConnection(balder.Connection):
    pass
