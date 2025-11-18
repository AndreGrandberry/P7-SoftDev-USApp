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


def test_login_invalid_email():
    """Tests login with an email not in the database"""
    with app.test_client() as c:
        resp = c.post("/login", data={"email": "notfound@example.com"})
        assert resp.status_code == 401
        assert b"Email not found" in resp.data


def test_login_missing_email():
    """Tests login with a missing email field"""
    with app.test_client() as c:
        resp = c.post("/login", data={})
        assert resp.status_code == 400
        assert b"Email is required" in resp.data


def test_login_empty_email():
    """Test login with empty email field"""
    with app.test_client() as c:
        resp = c.post("/login", data={"email": ""})
        assert resp.status_code == 400
        assert b"Email is required" in resp.data


def test_protected_route_without_login():
    """Test accessing a protected route without authentication"""
    with app.test_client() as c:
        resp = c.get("/summary")
        assert resp.status_code == 401
        assert b"Unauthorized" in resp.data


def test_redeem_more_points_than_available():
    """Test booking more points than the club has returns 403 and error message"""
    with app.test_client() as c:
        c.post("/login", data={"email": "admin@irontemple.com"}, follow_redirects=True)
        resp = c.post(
            "/book", data={"club": "Iron Temple", "competition": "Spring Festival", "spots": "5"}
        )
        assert resp.status_code == 403
        assert "Not enough points." in resp.data.decode()


def test_book_zero_spots():
    """Booking zero spots should fail with 400 Bad Request"""
    with app.test_client() as c:
        c.post("/login", data={"email": "john@simplylift.co"}, follow_redirects=True)
        resp = c.post("/book", data={"club": "Simply Lift", "competition": "Spring Festival", "spots": "0"})
        assert resp.status_code == 400
        assert "Invalid number of spots." in resp.data.decode()


def test_book_exact_points():
    """Booking exactly the available points should succeed"""
    with app.test_client() as c:
        c.post("/login", data={"email": "john@simplylift.co"}, follow_redirects=True)
        resp = c.post("/book", data={"club": "Simply Lift", "competition": "Spring Festival", "spots": "12"})
        assert resp.status_code == 200
        assert "Great-booking complete!" in resp.data.decode()


def test_book_fewer_points():
    """Booking fewer points than available should succeed"""
    with app.test_client() as c:
        c.post("/login", data={"email": "john@simplylift.co"}, follow_redirects=True)
        resp = c.post("/book", data={"club": "Simply Lift", "competition": "Spring Festival", "spots": "5"})
        assert resp.status_code == 200
        assert "Great-booking complete!" in resp.data.decode()


def test_book_more_than_12_spots():
    """Booking more than 12 spots should fail with 403 Forbidden"""
    with app.test_client() as c:
        c.post("/login", data={"email": "john@simplylift.co"}, follow_redirects=True)
        resp = c.post("/book", data={"club": "Simply Lift", "competition": "Spring Festival", "spots": "13"})
        assert resp.status_code == 403
        assert "Cannot book more than 12 places." in resp.data.decode()


def test_book_exactly_12_spots():
    """Booking exactly 12 spots should succeed (HTTP 200 OK)"""
    with app.test_client() as c:
        c.post("/login", data={"email": "john@simplylift.co"}, follow_redirects=True)
        resp = c.post("/book", data={"club": "Simply Lift", "competition": "Spring Festival", "spots": "12"})
        assert resp.status_code == 200
        assert "Cannot book more than 12 places." not in resp.data.decode()


def create_competition(name, date):
    return {"name": name, "date": date, "spotsAvailable": "25"}


def create_club(name, email="john@simplylift.co", points="100"):
    return {"name": name, "email": email, "points": points}


def test_book_past_competition():
    past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    competitions = [create_competition("Fall Classic", past_date)]
    clubs = [create_club("Simply Lift")]
    with patch("provider.get_competitions", return_value=competitions), \
         patch("provider.get_clubs", return_value=clubs):
        with app.test_client() as c:
            c.post("/login", data={"email": "john@simplylift.co"}, follow_redirects=True)
            resp = c.post("/book", data={"club": "Simply Lift", "competition": "Fall Classic", "spots": "1"})
            assert resp.status_code == 403


def test_book_today_competition():
    competitions = [create_competition("Winter Cup", "2025-11-18 20:00:00")]
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








