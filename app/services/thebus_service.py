import re
from datetime import datetime
from functools import wraps
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Optional

import requests
import xmltodict

from app.models import Arrival
from app.models import Route
from app.models import Vehicle
from app.settings import API_KEY
from app.settings import TZ


IterableResponseType = Iterable[Dict[str, Any]]

stop_id_pattern = re.compile(r'\(Stop: (\d+)\)')


def normalize_vehicles_response(f):  # type: ignore
    """Decorator that mutates the vehicle response by casting values into correct types."""
    @wraps(f)
    def wrapper(*args, **kwargs):  # type: ignore
        vehicles = f(*args, **kwargs)
        for v in vehicles:
            vm = Vehicle(
                number=str(v['number']),
                trip_id=None if v['trip'] == 'null_trip' else int(v['trip']),
                driver_id=None if v['driver'] == '0' else int(v['driver']),
                latitude=float(v['latitude']),
                longitude=float(v['longitude']),
                adherence=int(v['adherence']),
                last_message=get_vehicles_datestr_to_datetime(v['last_message']),
                route=None if v['route_short_name'] == 'null' else str(v['route_short_name']),
                headsign=None if v['headsign'] == 'null' else str(v['headsign']),
            )
            yield vm
    return wrapper


@normalize_vehicles_response
def get_vehicles() -> Iterable[Vehicle]:
    """
    Gets all vehicle information, or information about a specific vehicle.

    Raises a requests.HTTPError on non-2xx response.
    """
    resp = requests.get(f'http://api.thebus.org/vehicle/?key={API_KEY}')
    resp.raise_for_status()
    text = escape_ampersands(resp.text)
    as_dict = xmltodict.parse(text)
    if 'vehicle' in as_dict['vehicles']:
        for row in as_dict['vehicles']['vehicle']:
            yield row


def get_active_vehicles() -> Iterable[Vehicle]:
    """
    Get only the vehicles with an active trip.
    """
    for vm in get_vehicles():
        if vm.is_active():
            yield vm


def normalize_arrivals_response(f):  # type: ignore
    """Decorator that mutates the arrivals response by casting values into correct types."""
    @wraps(f)
    def wrapper(*args, **kwargs):  # type: ignore
        arrivals = f(*args, **kwargs)
        for a in arrivals:
            am = Arrival(
                id=int(a['id']),
                trip_id=int(a['trip']),
                route=str(a['route']),
                headsign=str(a['headsign']),
                vehicle=None if a['vehicle'] == '???' else str(a['vehicle']),
                direction=str(a['direction']),
                stop_time=get_arrivals_datestr_to_datetime(str(a['date']), str(a['stopTime'])),
                estimated=int(a['estimated']),
                longitude=float(a['longitude']),
                latitude=float(a['latitude']),
                shape_id=str(a['shape']),
                canceled=int(a['canceled']),
            )
            yield am
    return wrapper


@normalize_arrivals_response
def get_arrivals(stop_id: int) -> Iterable[Arrival]:
    """
    Gets arrival information for a given stop.

    Raises a requests.HTTPError on non-2xx response.
    """
    resp = requests.get(f'http://api.thebus.org/arrivals/?key={API_KEY}&stop={stop_id}')
    resp.raise_for_status()
    text = escape_ampersands(resp.text)
    as_dict = xmltodict.parse(text)
    if 'arrival' in as_dict['stopTimes']:
        for row in as_dict['stopTimes']['arrival']:
            yield row


def normalize_routes_response(f):  # type: ignore
    """Decorator that mutates the routes response by casting values into correct types."""
    @wraps(f)
    def wrapper(*args, **kwargs):  # type: ignore
        routes = f(*args, **kwargs)
        for r in routes:
            rm = Route(
                route=str(r['routeNum']),
                shape_id=str(r['shapeID']),
                first_stop=str(r['firstStop']),
                headsign=str(r['headsign']),
                stop_id=parse_stop_id_from_route(r['firstStop']),
            )
            yield rm
    return wrapper


@normalize_routes_response
def get_routes(route: str) -> Iterable[Route]:
    """
    Gets route information for a given bus route, e.g. 2L, 60.
    """
    resp = requests.get(f'http://api.thebus.org/route/?key={API_KEY}&route={route}')
    resp.raise_for_status()
    text = escape_ampersands(resp.text)
    as_dict = xmltodict.parse(text)
    if 'route' in as_dict['routes']:
        for row in as_dict['routes']['route']:
            yield row


def parse_stop_id_from_route(text: str) -> Optional[int]:
    """
    Extracts the stop id from a string like KAPIOLANI COMMUNITY COLLEGE (Stop: 4538)
    """
    match = stop_id_pattern.search(text)
    if match:
        return int(match.group(1))
    return None


def get_vehicles_datestr_to_datetime(datetime_str: str) -> datetime:
    """Converts the API response's date format into a tz-aware datetime."""
    dt = datetime.strptime(datetime_str, '%m/%d/%Y %I:%M:%S %p')
    return dt.replace(tzinfo=TZ)


def get_arrivals_datestr_to_datetime(date_str: str, time_str: str) -> datetime:
    """Converts the API response's date format into a tz-aware datetime."""
    dt = datetime.strptime(f'{date_str} {time_str}', '%m/%d/%Y %I:%M %p')
    return dt.replace(tzinfo=TZ)


def escape_ampersands(xml: str) -> str:
    """
    Escapes unescaped ampersands in a string of XML.

    TheBus API returns unescaped ampersands in its response.
    Taken from https://stackoverflow.com/a/8731820
    """
    return re.sub(
        r'&(?![A-Za-z]+[0-9]*;|#[0-9]+;|#x[0-9a-fA-F]+;)',
        r'&amp;',
        xml,
    )
