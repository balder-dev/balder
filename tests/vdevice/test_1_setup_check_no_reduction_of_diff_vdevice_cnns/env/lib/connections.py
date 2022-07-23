import balder


class MySimplySharedMemoryConnection(balder.Connection):
    """This is a simply shared memory connection"""
    pass


@balder.insert_into_tree()
class SimulatedParentConnection(balder.Connection):
    pass


@balder.insert_into_tree(parents=[SimulatedParentConnection])
class SimulatedChildConnection(balder.Connection):
    pass
