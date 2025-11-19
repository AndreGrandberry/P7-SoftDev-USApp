import json
from pathlib import Path

DATA_FOLDER = "data"


def _json_from_file(filename, key):
    """Helper method - loads JSON from 'filename'
    and return whatever is at the 'key'"""
    filepath = Path(__file__).parent / DATA_FOLDER / filename
    with open(filepath) as fp:
        data = json.load(fp)
        return data[key]


def get_clubs():
    """Load clubs from JSON"""
    return _json_from_file("clubs.json", "clubs")


def get_competitions():
    """Load competitions from JSON"""
    return _json_from_file("competitions.json", "competitions")
