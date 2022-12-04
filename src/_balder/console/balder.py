from __future__ import annotations

from _balder.balder_session import BalderSession


def console_balder():
    """script that executes a balder session"""
    balder_session = BalderSession()
    balder_session.run()
