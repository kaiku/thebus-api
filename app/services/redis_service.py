import redis

from app.models import Vehicle


redis_client = redis.Redis(host='localhost', port=6379, db=0)


def add_vehicle(vm: Vehicle) -> None:
    pass
