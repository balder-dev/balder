
__all__ = [
    "__version__",

    "__version_tuple__"
]

try:
    from ._version import __version__, __version_tuple__
except ImportError:
    __version__ = ""
    __version_tuple__ = tuple()
