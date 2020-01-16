import os

import pytest

from app.settings import ROOT_DIR


FILES = {
    'vehicles-multiple.success': 'tests/data/vehicles-multiple.success.xml',
    'vehicles-single.success': 'tests/data/vehicles-single.success.xml',
    'arrivals.success': 'tests/data/arrivals.success.xml',
    'routes.success': 'tests/data/routes.success.xml',
}

FIXTURES = {}

for key, filepath in FILES.items():
    with open(os.path.join(ROOT_DIR, filepath)) as f:
        FIXTURES[key] = f.read()


@pytest.fixture
def vehicles_multiple() -> str:
    return FIXTURES['vehicles-multiple.success']


@pytest.fixture
def vehicles_single() -> str:
    return FIXTURES['vehicles-single.success']


@pytest.fixture
def arrivals() -> str:
    return FIXTURES['arrivals.success']


@pytest.fixture
def routes() -> str:
    return FIXTURES['routes.success']
