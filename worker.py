import cmd
from time import sleep

from app.services import thebus_service
from app.settings import get_setting


class Worker(cmd.Cmd):
    """Fetches TheBus API data and loads it into Redis"""
    prompt = '(server) '

    def do_hello(self, arg):
        print(f'Hello, {arg}!')

    def do_settings_val(self, arg):
        value = get_setting(arg, str, '')
        print(f'{arg}={value}')

    def do_get_vehicles(self, arg):
        """Gets vehicle info"""
        vehicles = thebus_service.get_vehicle()
        print(f'Found {len(vehicles)} vehicles')

    def do_combined(self, arg):
        self.cmdqueue.extend([
            'hello a',
            'hello b',
            'delay 1.5',
            'hello c',
        ])

    def do_delay(self, arg: str):
        try:
            seconds = float(arg)
            print(f'Sleeping {seconds}s...')
            sleep(seconds)
        except ValueError:
            print('Please provide a float value')


if __name__ == '__main__':
    Worker().cmdloop()
