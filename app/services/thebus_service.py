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


VehiclesResponseType = List[Dict[str, Any]]


def api_datestr_to_datetime(datestr: str) -> datetime:
    """Converts the API response's date format into a tz-aware datetime."""
    dt = datetime.strptime(datestr, '%m/%d/%Y %I:%M:%S %p')
    return dt.replace(tzinfo=TZ)


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
            v['last_message'] = api_datestr_to_datetime(v['last_message'])
            v['route_short_name'] = None if v['route_short_name'] == 'null' else str(v['route_short_name'])
            v['headsign'] = None if v['headsign'] == 'null' else str(v['headsign'])
        return vehicles
    return wrapper


@normalize_vehicles_response
def get_vehicles() -> VehiclesResponseType:
    """
    Gets all vehicle information, or information about a specific vehicle.

    Raises a requests.HTTPError on non-2xx response.
    """
    resp = requests.get(f'http://api.thebus.org/vehicle/?key={API_KEY}')
    resp.raise_for_status()
    text = escape_ampersands(resp.text)
    as_dict = xmltodict.parse(text)
    # xmltodict stores all child <vehicle> tags like this
    vehicles: VehiclesResponseType = as_dict['vehicles']['vehicle']
    return vehicles


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
