import cmd
from time import sleep

from app.services import thebus_service
from app.settings import get_setting


class ServerCommands(cmd.Cmd):
    """Fetches TheBus API data and loads it into Redis"""
    prompt = '(command) '

    def do_hello(self, arg: str) -> None:
        print(f'Hello, {arg}!')

    def do_settings_val(self, arg: str) -> None:
        value = get_setting(arg, str, '')
        print(f'{arg}={value}')

    def do_get_vehicles(self, arg: str) -> None:
        """Get all vehicle info"""
        vehicles = thebus_service.get_vehicles()
        print(f'Found {len(vehicles)} vehicles')

    def do_arrivals(self, arg: str) -> None:
        """Get arrival times by stop_id"""
        try:
            stop_id = int(arg)
        except ValueError:
            print('Please enter a valid numeric stop id')
            return

        arrivals = thebus_service.get_arrivals(stop_id)
        print(f'Found {len(arrivals)} arrivals for stop {stop_id}')

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
