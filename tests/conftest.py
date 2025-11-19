import pytest


def mock_clubs():
    """Static data to mock clubs"""
    return [
        {
            "name": "Simply Lift",
            "email": "john@simplylift.co",
            "points": "13",
        },
        {
            "name": "Iron Temple",
            "email": "admin@irontemple.com",
            "points": "4",
        },
        {
            "name": "She Lifts",
            "email": "kate@shelifts.co.uk",
            "points": "12",
        },
    ]


def mock_competitions():
    """Static data to mock competitions"""
    return [
        {
            "name": "Spring Festival",
            "date": "2020-03-27 10:00:00",
            "spotsAvailable": "25",
        },
        {
            "name": "Fall Classic",
            "date": "2020-10-22 13:30:00",
            "spotsAvailable": "13",
        },
    ]


@pytest.fixture(autouse=True)
def mock_data_provider(monkeypatch):
    """
    This fixture will be automatically used in test functions.

    We patch `server.get_clubs`, because that's
    where the get_clubs function is used.
    """

    monkeypatch.setattr("server.get_clubs", mock_clubs)
    monkeypatch.setattr("server.get_competitions", mock_competitions)
