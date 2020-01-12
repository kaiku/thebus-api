import re

import pytest
import responses

from app.models import Arrival
from app.models import Route
from app.models import Vehicle
from app.services.thebus_service import get_arrivals
from app.services.thebus_service import get_arrivals_datestr_to_datetime
from app.services.thebus_service import get_routes
from app.services.thebus_service import get_vehicles
from app.services.thebus_service import get_vehicles_datestr_to_datetime


ANY_URL = re.compile('.*')


@responses.activate
@pytest.mark.parametrize('row,expected', [
    (0, Vehicle(
        number='020',
        trip_id=2558851,
        driver_id=7828,
        latitude=21.39357,
        longitude=-157.7444,
        adherence=0,
        last_message=get_vehicles_datestr_to_datetime('1/7/2020 7:05:54 AM'),
        route='671',
        headsign='KAILUA TOWN',
    )),
    (4, Vehicle(
        number='026',
        trip_id=None,
        driver_id=None,
        latitude=21.4005346,
        longitude=-157.9701914,
        adherence=-1,
        last_message=get_vehicles_datestr_to_datetime('7/18/2012 3:12:42 PM'),
        route=None,
        headsign=None,
    )),
])
def test_get_vehicles(vehicles, row, expected):
    responses.add(responses.GET, ANY_URL, body=vehicles, status=200)
    resp = list(get_vehicles())
    assert expected == resp[row]


@responses.activate
@pytest.mark.parametrize('row,expected', [
    (0, Arrival(
        id=1504241264,
        trip_id=2587528,
        route='2',
        headsign='SCHOOL ST - KALIHI TRANSIT CENTER',
        vehicle='178',
        direction='Westbound',
        stop_time=get_arrivals_datestr_to_datetime('1/11/2020', '11:11 PM'),
        estimated=1,
        latitude=21.3315100,
        longitude=-157.8658300,
        shape_id='20160',
        canceled=0,
    )),
])
def test_get_arrivals(arrivals, row, expected):
    responses.add(responses.GET, ANY_URL, body=arrivals, status=200)
    resp = list(get_arrivals(79))
    assert expected == resp[row]


@responses.activate
@pytest.mark.parametrize('row,expected,extracted_stop_id', [
    (0, Route(
        route='2L',
        shape_id='2L0009',
        first_stop='KAPIOLANI COMMUNITY COLLEGE (Stop: 4538)',
        headsign='SCHOOL STREET - Limited Stops',
    ), 4538),
])
def test_get_routes(routes, row, expected, extracted_stop_id):
    responses.add(responses.GET, ANY_URL, body=routes, status=200)
    resp = list(get_routes('2L'))
    rm = resp[row]
    assert expected == rm
    # assert
