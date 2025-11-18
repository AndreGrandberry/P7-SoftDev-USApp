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


def test_book_competition_not_found():
    clubs = [{"name": "Test Club", "email": "test@club.com", "points": "10"}]
    competitions = [{"name": "Spring Festival", "date": "2099-01-01 10:00:00", "spotsAvailable": "5"}]
    with patch("server.get_clubs", return_value=clubs), \
         patch("server.get_competitions", return_value=competitions), \
         app.test_client() as client:
        with client.session_transaction() as sess:
            sess["club"] = clubs[0]
        resp = client.get("/book/Nonexistent Competition", follow_redirects=True)
        assert b"Something went wrong-please try again" in resp.data


def test_logout():
    clubs = [{"name": "Test Club", "email": "test@club.com", "points": "10"}]
    with patch("server.get_clubs", return_value=clubs), app.test_client() as client:
        with client.session_transaction() as sess:
            sess["club"] = clubs[0]
        resp = client.get("/logout", follow_redirects=True)
        assert resp.status_code == 200
        assert b"Welcome to the GUDLFT Registration Portal!" in resp.data


def test_redeem_more_points_than_available():
    clubs = [{"name": "Iron Temple", "email": "admin@irontemple.com", "points": "2"}]
    competitions = [{"name": "Spring Festival", "date": "2099-01-01 10:00:00", "spotsAvailable": "5"}]
    with patch("server.get_clubs", return_value=clubs), \
         patch("server.get_competitions", return_value=competitions):
        with app.test_client() as c:
            c.post("/login", data={"email": "admin@irontemple.com"}, follow_redirects=True)
            resp = c.post(
                "/book", data={"club": "Iron Temple", "competition": "Spring Festival", "spots": "5"}
            )
            assert resp.status_code == 403
            assert "Not enough points." in resp.data.decode()


def test_book_zero_spots():
    clubs = [{"name": "Simply Lift", "email": "john@simplylift.co", "points": "100"}]
    competitions = [{"name": "Spring Festival", "date": "2099-01-01 10:00:00", "spotsAvailable": "25"}]
    with patch("server.get_clubs", return_value=clubs), \
         patch("server.get_competitions", return_value=competitions):
        with app.test_client() as c:
            c.post("/login", data={"email": "john@simplylift.co"}, follow_redirects=True)
            resp = c.post("/book", data={"club": "Simply Lift", "competition": "Spring Festival", "spots": "0"})
            assert resp.status_code == 400
            assert "Invalid number of spots." in resp.data.decode()


def test_book_exact_points():
    clubs = [{"name": "Simply Lift", "email": "john@simplylift.co", "points": "12"}]
    competitions = [{"name": "Spring Festival", "date": "2099-01-01 10:00:00", "spotsAvailable": "25"}]
    with patch("server.get_clubs", return_value=clubs), \
         patch("server.get_competitions", return_value=competitions):
        with app.test_client() as c:
            c.post("/login", data={"email": "john@simplylift.co"}, follow_redirects=True)
            resp = c.post("/book", data={"club": "Simply Lift", "competition": "Spring Festival", "spots": "12"})
            assert resp.status_code == 200
            assert "Great-booking complete!" in resp.data.decode()


def test_book_fewer_points():
    clubs = [{"name": "Simply Lift", "email": "john@simplylift.co", "points": "12"}]
    competitions = [{"name": "Spring Festival", "date": "2099-01-01 10:00:00", "spotsAvailable": "25"}]
    with patch("server.get_clubs", return_value=clubs), \
         patch("server.get_competitions", return_value=competitions):
        with app.test_client() as c:
            c.post("/login", data={"email": "john@simplylift.co"}, follow_redirects=True)
            resp = c.post("/book", data={"club": "Simply Lift", "competition": "Spring Festival", "spots": "5"})
            assert resp.status_code == 200
            assert "Great-booking complete!" in resp.data.decode()


def test_book_more_than_12_spots():
    """Booking more than 12 spots should fail with 403 Forbidden"""
    clubs = [{"name": "Simply Lift", "email": "john@simplylift.co", "points": "12"}]
    competitions = [{"name": "Spring Festival", "date": "2099-01-01 10:00:00", "spotsAvailable": "25"}]
    with patch("server.get_clubs", return_value=clubs), \
         patch("server.get_competitions", return_value=competitions):
        with app.test_client() as c:
            c.post("/login", data={"email": "john@simplylift.co"}, follow_redirects=True)
            resp = c.post("/book", data={"club": "Simply Lift", "competition": "Spring Festival", "spots": "13"})
            assert resp.status_code == 403
            assert "Cannot book more than 12 places." in resp.data.decode()


def test_book_exactly_12_spots():
    clubs = [{"name": "Simply Lift", "email": "john@simplylift.co", "points": "12"}]
    competitions = [{"name": "Spring Festival", "date": "2099-01-01 10:00:00", "spotsAvailable": "25"}]
    with patch("server.get_clubs", return_value=clubs), \
         patch("server.get_competitions", return_value=competitions):
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


def test_booking_deducts_points():
    clubs = [{"name": "Test Club", "email": "test@club.com", "points": "10"}]
    competitions = [{"name": "Test Competition", "date": "2099-01-01 10:00:00", "spotsAvailable": "5"}]

    with patch("server.get_clubs", return_value=clubs), \
         patch("server.get_competitions", return_value=competitions), \
         app.test_client() as client:
        with client.session_transaction() as sess:
            sess["club"] = clubs[0]

        client.post(
            "/book",
            data={"competition": "Test Competition", "spots": "3"},
            follow_redirects=True,
        )

        with client.session_transaction() as sess:
            assert int(sess["club"]["points"]) == 7


def test_booking_exact_points_leaves_zero():
    clubs = [{"name": "Test Club", "email": "test@club.com", "points": "3"}]
    competitions = [{"name": "Test Competition", "date": "2099-01-01 10:00:00", "spotsAvailable": "5"}]

    with patch("server.get_clubs", return_value=clubs), \
         patch("server.get_competitions", return_value=competitions), \
         app.test_client() as client:
        with client.session_transaction() as sess:
            sess["club"] = clubs[0]

        client.post(
            "/book",
            data={"competition": "Test Competition", "spots": "3"},
            follow_redirects=True,
        )

        with client.session_transaction() as sess:
            assert int(sess["club"]["points"]) == 0


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