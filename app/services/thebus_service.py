import re
from typing import Dict
from typing import List
from typing import Optional

import requests
import xmltodict

from app.settings import API_KEY
# from defusedxml import ElementTree


def fix_ampersands(xml_text: str) -> str:
    # taken from https://stackoverflow.com/a/8731820
    # thebus api returns unescaped ampersands
    return re.sub(
        r'&(?![A-Za-z]+[0-9]*;|#[0-9]+;|#x[0-9a-fA-F]+;)',
        r'&amp;',
        xml_text
    )


def get_vehicle(vehicle_num: Optional[int] = None) -> List[Dict[str, str]]:
    """Gets all vehicle information, or information about a specific vehicle."""
    # http://api.thebus.org/vehicle/?key={API_KEY}&vehicle_num={vehicle}
    resp = requests.get(f'http://api.thebus.org/vehicle/?key={API_KEY}')
    text = fix_ampersands(resp.text)
    as_dict = xmltodict.parse(text)
    # xmltodict stores all child <vehicle> tags like this
    vehicles: List[Dict[str, str]] = as_dict['vehicles']['vehicle']
    return vehicles


# def get_routes(route: int):
#     resp = requests.get(f'http://api.thebus.org/route/?key={API_KEY}&route={route}')
#     root = ElementTree.fromstring(resp.text)
#     for child in root:
#         print(child.tag, child.attrib)
