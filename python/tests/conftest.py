import os
import shutil
from pathlib import Path


def pytest_sessionstart(session):
    project_root = Path(__file__).parents[2]
    frompath = project_root / "schema"
    topath = project_root / "python" / "imeta" / "schema"
    if topath.exists():
        shutil.rmtree(topath)
    shutil.copytree(frompath, topath)
