import cmd
from time import sleep

from attr import asdict
from tabulate import tabulate

from app.services.redis_service import redis_client
from app.services.thebus_service import get_active_vehicles
from app.services.thebus_service import get_active_vehicles_by_route
from app.services.thebus_service import get_arrivals
from app.services.thebus_service import get_routes


class ServerCommands(cmd.Cmd):
    """Fetches TheBus API data and loads it into Redis"""
    prompt = '(command) '

    def do_vehicles(self, arg: str) -> None:
        """Get all active vehicles on the road"""
        if arg:
            try:
                cmd, value = tuple(arg.split(' '))
                if cmd == 'number':
                    generator = get_active_vehicles(value)
                elif cmd == 'route':
                    generator = get_active_vehicles_by_route(value)
                else:
                    raise ValueError(f'Invalid command {cmd}')
            except ValueError:
                print('Please enter a valid command')
                return
        else:
            generator = get_active_vehicles()

        vehicles = [asdict(v) for v in generator]
        print(f'Found {len(vehicles)} vehicles')
        if len(vehicles):
            print(tabulate(vehicles, headers='keys'))

    def do_routes(self, route: str) -> None:
        """Get info on a particular bus route"""
        if not route:
            print('Please enter a route')
            return

        routes = [asdict(r) for r in get_routes(route)]
        print(f'Found {len(routes)} routes for route {route}')
        if len(routes):
            print(tabulate(routes, headers='keys'))

    def do_arrivals(self, stop_id: str) -> None:
        """Get arrival times by stop_id"""
        try:
            stop_id_int = int(stop_id)
        except ValueError:
            print('Please enter a valid numeric stop id')
            return

        arrivals = [asdict(a) for a in get_arrivals(stop_id_int)]
        print(f'Found {len(arrivals)} arrivals for stop {stop_id_int}')
        if len(arrivals):
            print(tabulate(arrivals, headers='keys'))

    def do_write_vehicles_to_redis(self, arg: str) -> None:
        for vm in get_active_vehicles():
            try:
                number = vm.number
                coord = vm.get_coordinate()
            except ValueError:
                continue
            redis_client.geoadd('vehicles:geo', coord.lng, coord.lat, number)  # type: ignore

    def do_get_results_from_redis(self, arg: str) -> None:
        lat, lng, radius = 21.3075785, -157.8542978, 2
        results = redis_client.georadius(  # type: ignore
            'vehicles:geo',
            lng, lat,
            radius, unit='mi',
            withdist=True, withcoord=True, sort='ASC',
        )
        print(tabulate(results, headers=['number', 'distance', 'coordinate']))

    def do_combined(self, arg: str) -> None:
        self.cmdqueue.extend([
            'hello a',
            'hello b',
            'delay 1.5',
            'hello c',
        ])

    def do_delay(self, arg: str) -> None:
        try:
            seconds = float(arg)
            print(f'Sleeping {seconds}s...')
            sleep(seconds)
        except ValueError:
            print('Please provide a float value')
