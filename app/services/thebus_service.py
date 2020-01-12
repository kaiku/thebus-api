import re
from datetime import datetime
from functools import wraps
from typing import Any
from typing import Dict
from typing import List

import requests
import xmltodict

from app.settings import API_KEY
from app.settings import TZ
# from defusedxml import ElementTree


ListResponseType = List[Dict[str, Any]]


def normalize_vehicles_response(f):  # type: ignore
    """Decorator that mutates the vehicle response by casting values into correct types."""
    @wraps(f)
    def wrapper(*args, **kwargs):  # type: ignore
        vehicles = f(*args, **kwargs)
        for v in vehicles:
            v['number'] = str(v['number'])  # e.g. 020 - we might want to preserve leading zero
            v['trip'] = None if v['trip'] == 'null_trip' else int(v['trip'])
            v['driver'] = int(v['driver'])
            v['latitude'] = float(v['latitude'])
            v['longitude'] = float(v['longitude'])
            v['adherence'] = int(v['adherence'])
            v['last_message'] = get_vehicles_datestr_to_datetime(v['last_message'])
            v['route_short_name'] = None if v['route_short_name'] == 'null' else str(v['route_short_name'])
            v['headsign'] = None if v['headsign'] == 'null' else str(v['headsign'])
        return vehicles
    return wrapper


@normalize_vehicles_response
def get_vehicles() -> ListResponseType:
    """
    Gets all vehicle information, or information about a specific vehicle.

    Raises a requests.HTTPError on non-2xx response.
    """
    resp = requests.get(f'http://api.thebus.org/vehicle/?key={API_KEY}')
    resp.raise_for_status()
    text = escape_ampersands(resp.text)
    as_dict = xmltodict.parse(text)
    # xmltodict stores all child <vehicle> tags like this
    vehicles: ListResponseType = as_dict['vehicles']['vehicle']
    return vehicles


def normalize_arrivals_response(f):  # type: ignore
    """Decorator that mutates the arrivals response by casting values into correct types."""
    @wraps(f)
    def wrapper(*args, **kwargs):  # type: ignore
        arrivals = f(*args, **kwargs)
        for a in arrivals:
            a['id'] = int(a['id'])
            a['trip'] = int(a['trip'])
            a['route'] = str(a['route'])
            a['headsign'] = str(a['headsign'])
            a['vehicle'] = None if a['vehicle'] == '???' else str(a['vehicle'])
            a['direction'] = str(a['direction'])
            a['stop_time'] = get_arrivals_datestr_to_datetime(str(a['date']), str(a['stopTime']))
            a['estimated'] = int(a['estimated'])
            a['longitude'] = float(a['longitude'])
            a['latitude'] = float(a['latitude'])
            a['shape'] = int(a['shape'])
            a['canceled'] = int(a['canceled'])
            del a['stopTime']
            del a['date']
        return arrivals
    return wrapper


@normalize_arrivals_response
def get_arrivals(stop_id: int) -> ListResponseType:
    """
    Gets arrival information for a given stop.

    Raises a requests.HTTPError on non-2xx response.
    """
    resp = requests.get(f'http://api.thebus.org/arrivals/?key={API_KEY}&stop={stop_id}')
    resp.raise_for_status()
    text = escape_ampersands(resp.text)
    as_dict = xmltodict.parse(text)
    stop_times = as_dict['stopTimes']
    arrivals: ListResponseType = stop_times['arrival'] if 'arrival' in stop_times else []
    return arrivals


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


# def get_routes(route: int):
#     resp = requests.get(f'http://api.thebus.org/route/?key={API_KEY}&route={route}')
#     root = ElementTree.fromstring(resp.text)
#     for child in root:
#         print(child.tag, child.attrib)
