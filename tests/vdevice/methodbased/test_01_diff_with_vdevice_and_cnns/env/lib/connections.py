import balder


@balder.insert_into_tree()
class AConnection(balder.Connection):
    pass


@balder.insert_into_tree()
class BConnection(balder.Connection):
    pass


@balder.insert_into_tree()
class CConnection(balder.Connection):
    pass
