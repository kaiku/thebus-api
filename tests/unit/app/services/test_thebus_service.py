import re

import pytest
import responses

from app.services.thebus_service import get_arrivals
from app.services.thebus_service import get_arrivals_datestr_to_datetime
from app.services.thebus_service import get_vehicles
from app.services.thebus_service import get_vehicles_datestr_to_datetime

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
        'last_message': get_vehicles_datestr_to_datetime('1/7/2020 7:05:54 AM'),
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
        'last_message': get_vehicles_datestr_to_datetime('7/18/2012 3:12:42 PM'),
        'route_short_name': None,
        'headsign': None,
    })
])
def test_get_vehicles(vehicles, row, expected):
    responses.add(responses.GET, ANY_URL, body=vehicles, status=200)
    resp = get_vehicles()
    vehicle = resp[row]
    for k, v in expected.items():
        assert vehicle[k] == v, f'mismatch for `{k}`'
    assert set(vehicle.keys()) == set(expected.keys())


@responses.activate
@pytest.mark.parametrize('row,expected', [
    (0, {
        'id': 1504241264,
        'trip': 2587528,
        'route': '2',
        'headsign': 'SCHOOL ST - KALIHI TRANSIT CENTER',
        'vehicle': '178',
        'direction': 'Westbound',
        'stop_time': get_arrivals_datestr_to_datetime('1/11/2020', '11:11 PM'),
        'estimated': 1,
        'latitude': 21.3315100,
        'longitude': -157.8658300,
        'shape': 20160,
        'canceled': 0,
    }),
])
def test_get_arrivals(arrivals, row, expected):
    responses.add(responses.GET, ANY_URL, body=arrivals, status=200)
    resp = get_arrivals(79)
    arrival = resp[row]
    for k, v in expected.items():
        assert arrival[k] == v, f'mismatch for `{k}`'
    assert set(arrival.keys()) == set(expected.keys())
