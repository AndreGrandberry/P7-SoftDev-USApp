from flask import request

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


def test_redeem_more_points_than_available():
    """Test booking more points than the club has returns 403 and error message"""
    with app.test_client() as c:
        c.post("/login", data={"email": "john@simplylift.co"}, follow_redirects=True)
        resp = c.post(
            "/book", data={"club": "Simply Lift", "competition": "Spring Festival", "spots": "20"}
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
        resp = c.post("/book", data={"club": "Simply Lift", "competition": "Spring Festival", "spots": "13"})
        assert resp.status_code == 200
        assert "Great-booking complete!" in resp.data.decode()


def test_book_fewer_points():
    """Booking fewer points than available should succeed"""
    with app.test_client() as c:
        c.post("/login", data={"email": "john@simplylift.co"}, follow_redirects=True)
        resp = c.post("/book", data={"club": "Simply Lift", "competition": "Spring Festival", "spots": "5"})
        assert resp.status_code == 200
        assert "Great-booking complete!" in resp.data.decode()

