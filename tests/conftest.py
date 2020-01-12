import os

import pytest

from app.settings import ROOT_DIR


# load vehicles xml
with open(os.path.join(ROOT_DIR, 'tests/data/vehicles.xml')) as f:
    _VEHICLES = f.read()


@pytest.fixture
def vehicles() -> str:
    return _VEHICLES
