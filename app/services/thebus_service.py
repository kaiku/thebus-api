import re
from typing import List
from typing import OrderedDict

from defusedxml import ElementTree
import requests
import xmltodict

from app.settings import API_KEY


def fix_ampersands(xml_text: str) -> str:
    # taken from https://stackoverflow.com/a/8731820
    # thebus api returns unescaped ampersands
    return re.sub(
        r'&(?![A-Za-z]+[0-9]*;|#[0-9]+;|#x[0-9a-fA-F]+;)',
        r'&amp;',
        xml_text
    )


def get_vehicle(vehicle_num: int = None):
    """Gets all vehicle information, or information about a specific vehicle."""
    # http://api.thebus.org/vehicle/?key={API_KEY}&vehicle_num={vehicle}
    resp = requests.get(f'http://api.thebus.org/vehicle/?key={API_KEY}')
    text = fix_ampersands(resp.text)
    as_dict = xmltodict.parse(text)
    # breakpoint()
    # xmltodict stores all child <vehicle> tags like this
    vehicles: List[OrderedDict[str, str]] = as_dict['vehicles']['vehicle']
    # for vehicle in vehicles:
    #     d = dict(vehicle)
    return vehicles


def get_routes(route: int):
    resp = requests.get(f'http://api.thebus.org/route/?key={API_KEY}&route={route}')
    root = ElementTree.fromstring(resp.text)
    for child in root:
        print(child.tag, child.attrib)
