from flask import request
from unittest.mock import patch
from server import app


def test_homepage():
    """Test the homepage works (HTTP status 200 OK)"""
    with app.test_client() as c:
        resp = c.get("/")
        assert resp.status_code == 200


def test_login():
    """Tests a login action"""
    with app.test_client() as c:
        resp = c.post(
            "/login", data={"email": "john@simplylift.co"}, follow_redirects=True
        )
        # We should be redirected to the summary page
        assert request.path == "/summary"
        # The status code should be 200 OK
        assert resp.status_code == 200
        # The email of the user logged in is displayed on the page
        assert "john@simplylift.co" in resp.data.decode()


def test_clubs_page_loads():
    with app.test_client() as client:
        resp = client.get("/clubs")
        assert resp.status_code == 200

def test_clubs_page_displays_clubs():
    clubs = [
        {"name": "Alpha Club", "email": "alpha@club.com", "points": "10"},
        {"name": "Beta Club", "email": "beta@club.com", "points": "5"},
    ]
    with patch("server.get_clubs", return_value=clubs), app.test_client() as client:
        resp = client.get("/clubs")
        data = resp.data.decode()
        assert "Alpha Club" in data
        assert "10" in data
        assert "Beta Club" in data
        assert "5" in data

def test_clubs_page_no_clubs():
    with patch("server.get_clubs", return_value=[]), app.test_client() as client:
        resp = client.get("/clubs")
        data = resp.data.decode()
        assert "Clubs and Points" in data