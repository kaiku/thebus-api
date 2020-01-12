import re
from datetime import datetime
from functools import wraps
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Optional

import requests
import xmltodict

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
            v['number'] = str(v['number'])  # e.g. 020 - we might want to preserve leading zero
            v['trip_id'] = None if v['trip'] == 'null_trip' else int(v['trip'])
            v['driver_id'] = None if v['driver'] == '0' else int(v['driver'])
            v['latitude'] = float(v['latitude'])
            v['longitude'] = float(v['longitude'])
            v['adherence'] = int(v['adherence'])
            v['last_message'] = get_vehicles_datestr_to_datetime(v['last_message'])
            v['route'] = None if v['route_short_name'] == 'null' else str(v['route_short_name'])
            v['headsign'] = None if v['headsign'] == 'null' else str(v['headsign'])
            del v['trip']
            del v['driver']
            del v['route_short_name']
            yield v
    return wrapper


@normalize_vehicles_response
def get_vehicles() -> IterableResponseType:
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


def get_active_vehicles() -> IterableResponseType:
    """
    Get only the vehicles with an active trip.

    TODO: verify that this is the correct way to determine active/inactive.
    """
    for row in get_vehicles():
        if row['trip_id'] is not None:
            yield row


def normalize_arrivals_response(f):  # type: ignore
    """Decorator that mutates the arrivals response by casting values into correct types."""
    @wraps(f)
    def wrapper(*args, **kwargs):  # type: ignore
        arrivals = f(*args, **kwargs)
        for a in arrivals:
            a['id'] = int(a['id'])
            a['trip_id'] = int(a['trip'])
            a['route'] = str(a['route'])
            a['headsign'] = str(a['headsign'])
            a['vehicle'] = None if a['vehicle'] == '???' else str(a['vehicle'])
            a['direction'] = str(a['direction'])
            a['stop_time'] = get_arrivals_datestr_to_datetime(str(a['date']), str(a['stopTime']))
            a['estimated'] = int(a['estimated'])
            a['longitude'] = float(a['longitude'])
            a['latitude'] = float(a['latitude'])
            a['shape_id'] = str(a['shape'])
            a['canceled'] = int(a['canceled'])
            del a['trip']
            del a['stopTime']
            del a['date']
            del a['shape']
            yield a
    return wrapper


@normalize_arrivals_response
def get_arrivals(stop_id: int) -> IterableResponseType:
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
            r['route'] = str(r['routeNum'])
            r['shape_id'] = str(r['shapeID'])
            r['first_stop'] = str(r['firstStop'])
            r['headsign'] = str(r['headsign'])
            r['stop_id'] = parse_stop_id_from_route(r['first_stop'])
            del r['routeNum']
            del r['shapeID']
            del r['firstStop']
            yield r
    return wrapper


@normalize_routes_response
def get_routes(route: str) -> IterableResponseType:
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
