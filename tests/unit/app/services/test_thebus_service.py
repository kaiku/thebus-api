import re

import pytest
import responses

from app.services.thebus_service import api_datestr_to_datetime
from app.services.thebus_service import get_vehicles


ANY_URL = re.compile('.*')


@responses.activate
@pytest.mark.parametrize('row,expected', [
    (0, {
        'number': '020',
        'trip': 2558851,
        'driver': 7828,
        'latitude': 21.39357,
        'longitude': -157.7444,
        'adherence': 0,
        'last_message': api_datestr_to_datetime('1/7/2020 7:05:54 AM'),
        'route_short_name': '671',
        'headsign': 'KAILUA TOWN',
    }),
    (4, {
        'number': '026',
        'trip': None,
        'driver': 0,
        'latitude': 21.4005346,
        'longitude': -157.9701914,
        'adherence': -1,
        'last_message': api_datestr_to_datetime('7/18/2012 3:12:42 PM'),
        'route_short_name': None,
        'headsign': None,
    })
])
def test_get_vehicles(vehicles, row, expected):
    responses.add(responses.GET, ANY_URL, body=vehicles, status=200)
    resp = get_vehicles()
    vehicle = resp[row]
    for k, v in expected.items():
        assert vehicle[k] == v
