"""
Run an interactive shell via `python command.py`.

The command itself is in the app.command module so that other modules inside app can use it.
"""
from app.command import ServerCommands


if __name__ == '__main__':
    try:
        ServerCommands().cmdloop()
    except KeyboardInterrupt:
        print('\nBye!')
