import cmd
from time import sleep

from tabulate import tabulate

from app.services import thebus_service


class ServerCommands(cmd.Cmd):
    """Fetches TheBus API data and loads it into Redis"""
    prompt = '(command) '

    def do_vehicles(self, arg: str) -> None:
        """Get all vehicle info"""
        vehicles = list(thebus_service.get_vehicles())
        print(f'Found {len(vehicles)} vehicles')
        if len(vehicles):
            print(tabulate(vehicles, headers='keys'))

    def do_active_vehicles(self, arg: str) -> None:
        """Get info for active vehicles only"""
        vehicles = list(thebus_service.get_active_vehicles())
        print(f'Found {len(vehicles)} active vehicles')
        if len(vehicles):
            print(tabulate(vehicles, headers='keys'))

    def do_routes(self, route: str) -> None:
        if not route:
            print('Please enter a route')
            return

        routes = list(thebus_service.get_routes(route))
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

        arrivals = list(thebus_service.get_arrivals(stop_id_int))
        print(f'Found {len(arrivals)} arrivals for stop {stop_id_int}')
        if len(arrivals):
            print(tabulate(arrivals, headers='keys'))

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


if __name__ == '__main__':
    ServerCommands().cmdloop()
