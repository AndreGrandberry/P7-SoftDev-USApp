from flask import request
from unittest.mock import patch
from server import app
from datetime import datetime, timedelta
from provider import get_clubs, get_competitions


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


def create_competition(name, date):
    return {"name": name, "date": date, "spotsAvailable": "25"}


def create_club(name, email="john@simplylift.co", points="100"):
    return {"name": name, "email": email, "points": points}


def test_book_past_competition():
    past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    competitions = [create_competition("Spring Festival", past_date)]
    clubs = [create_club("Simply Lift")]
    with patch("provider.get_competitions", return_value=competitions), \
         patch("provider.get_clubs", return_value=clubs):
        with app.test_client() as c:
            c.post("/login", data={"email": "john@simplylift.co"}, follow_redirects=True)
            resp = c.post("/book", data={"club": "Simply Lift", "competition": "Spring Festival", "spots": "1"})
            assert resp.status_code == 403


def test_book_today_competition():
    competitions = [create_competition("Winter Cup", "2025-11-17 20:00:00")]
    clubs = [create_club("Simply Lift")]
    with patch("server.get_competitions", return_value=competitions), \
         patch("server.get_clubs", return_value=clubs):
        with app.test_client() as c:
            c.post("/login", data={"email": "john@simplylift.co"}, follow_redirects=True)
            resp = c.post("/book", data={"club": "Simply Lift", "competition": "Winter Cup", "spots": "1"})
            assert resp.status_code == 200

def test_book_future_competition():
    competitions = [create_competition("Summer Slam", "2028-07-19 16:00:00")]
    clubs = [create_club("Simply Lift")]
    with patch("server.get_competitions", return_value=competitions), \
         patch("server.get_clubs", return_value=clubs):
        with app.test_client() as c:
            c.post("/login", data={"email": "john@simplylift.co"}, follow_redirects=True)
            resp = c.post("/book", data={"club": "Simply Lift", "competition": "Summer Slam", "spots": "1"})
            assert resp.status_code == 200








