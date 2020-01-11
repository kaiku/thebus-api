from collections import defaultdict
import os


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SETTINGS = defaultdict(str)

with open(os.path.join(ROOT_DIR, '.env')) as f:
    for line in f:
        key, value = tuple(line.split('='))
        SETTINGS[key] = value


API_KEY = SETTINGS['API_KEY']