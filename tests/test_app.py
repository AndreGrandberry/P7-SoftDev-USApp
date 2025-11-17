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



