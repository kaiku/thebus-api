import os

import pytest

from app.settings import ROOT_DIR


FILES = {
    'vehicles-success': 'tests/data/vehicles-success.xml',
    'arrivals-success': 'tests/data/arrivals-success.xml',
    'routes-success': 'tests/data/routes-success.xml',
}

FIXTURES = {}

for key, filepath in FILES.items():
    with open(os.path.join(ROOT_DIR, filepath)) as f:
        FIXTURES[key] = f.read()


@pytest.fixture
def vehicles() -> str:
    return FIXTURES['vehicles-success']


@pytest.fixture
def arrivals() -> str:
    return FIXTURES['arrivals-success']


@pytest.fixture
def routes() -> str:
    return FIXTURES['routes-success']
