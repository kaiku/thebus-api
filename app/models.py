from dataclasses import dataclass
from datetime import datetime
from typing import Optional


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
    stop_id: Optional[int]


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
