import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


stop_id_pattern = re.compile(r'\(Stop: (\d+)\)')


@dataclass
class Arrival:
    id: int
    trip_id: int
    route: str
    headsign: str
    vehicle: Optional[str]
    direction: str
    stop_time: datetime
    estimated: int
    longitude: float
    latitude: float
    shape_id: str
    canceled: int


@dataclass
class Route:
    route: str
    shape_id: str
    first_stop: str
    headsign: str

    @property
    def first_stop_id(self) -> Optional[int]:
        """Extracts the stop id from the first stop string"""
        match = stop_id_pattern.search(self.first_stop)
        if match:
            return int(match.group(1))
        return None


@dataclass
class Vehicle:
    number: str  # vehicle number, e.g. 020 (may have leading zeroes)
    trip_id: Optional[int]
    driver_id: Optional[int]
    latitude: float
    longitude: float
    adherence: int
    last_message: datetime
    route: Optional[str]
    headsign: Optional[str]

    def is_active(self) -> bool:
        """TODO: Confirm this is how we determine active vehicles"""
        return self.trip_id is not None
