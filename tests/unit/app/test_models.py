import pytest

from app.models import Route


@pytest.mark.parametrize('first_stop,expected', [
    ('KALIHI TRANSIT CENTER (Stop: 4523)', 4523),
    ('(Stop: 5) foo', 5),
    ('bar', None),
    ('', None),
])
def test_route__first_stop_id(first_stop, expected):
    rm = Route(route='_', shape_id='_', headsign='_', first_stop=first_stop)
    assert rm.first_stop_id == expected
